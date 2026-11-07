"""Explicit Free MCP research path, NOT a paid REST-plan/quota bypass.

Only two entitlement symbols, two read-only tool names, twelve calls maximum.
Provider Free-plan proof is required; remaining MCP quota is unknown and server
quota errors stop immediately. No account/watchlist writes or automatic retries.
"""
import hashlib
import json
from datetime import date
from pathlib import Path

import requests

from .tapetide_fetch import FetchError, MAX_BYTES

URL = 'https://mcp.tapetide.com/mcp'
TOOLS = {'get_price_history', 'get_adjustment_factors'}
SYMBOLS = {'JIOFIN', 'KWIL'}
LISTED = {'JIOFIN':'2023-08-21','KWIL':'2026-02-16'}
MAX_TOOL_CALLS = 12  # Explicit paging budget: MCP truncates a maximum-window response.


def _reflected(value, token, depth=0):
    if depth > 20:
        raise FetchError('MCP nesting exceeds safe inspection depth')
    if isinstance(value,dict):
        return any(_reflected(k,token,depth+1) or _reflected(v,token,depth+1) for k,v in value.items())
    if isinstance(value,list):
        return any(_reflected(v,token,depth+1) for v in value)
    if isinstance(value,str):
        if token in value:return True
        if value.lstrip().startswith(('{','[')):
            try:nested=json.loads(value)
            except ValueError:return False
            return _reflected(nested,token,depth+1)
    return False


class MCPHistoryClient:
    def __init__(self, token, cache, free_plan_proof, session=None):
        if free_plan_proof != {'plan':'free', 'notice_code':'api_access_not_in_plan'}:
            raise FetchError('MCP requires verified Free-plan notice; no paid fallback')
        self._token = token
        self.cache = Path(cache)
        self.cache.mkdir(parents=True,exist_ok=True)
        self.session = session or requests.Session()
        self.session.trust_env = False
        self.headers = {'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream',
                        'Content-Type':'application/json'}
        self.seq = 0
        self.calls = 0
        self.receipts = []

    def _rpc(self, method, params=None, notification=False):
        if method not in ('initialize','notifications/initialized','tools/call'):
            raise FetchError('MCP method outside read-only client allow-list')
        if method == 'tools/call':
            self._check(params)
        self.seq += 1
        payload = dict(jsonrpc='2.0',method=method)
        if not notification:
            payload['id'] = self.seq
        if params is not None:
            payload['params'] = params
        try:
            with self.session.post(URL, headers=self.headers, json=payload, stream=True,
                                   allow_redirects=False, timeout=(10,30)) as response:
                if response.status_code not in (200,202,204):
                    raise FetchError(f'MCP HTTP {response.status_code}; no retry/redirect/upgrade')
                chunks,size = [],0
                for chunk in response.iter_content(65536):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise FetchError('MCP response exceeds byte limit')
                    chunks.append(chunk)
                raw = b''.join(chunks)
                if self._token.encode() in raw:
                    raise FetchError('MCP credential reflection rejected')
                sid = response.headers.get('Mcp-Session-Id')
                if sid:
                    self.headers['Mcp-Session-Id'] = sid
                if not raw:
                    if notification:return {}
                    raise FetchError('Empty MCP reply')
                text = raw.decode('utf-8')
                if response.headers.get('Content-Type','').startswith('text/event-stream'):
                    messages = [json.loads(line[5:].strip()) for line in text.splitlines() if line.startswith('data:')]
                    obj = next((m for m in messages if isinstance(m,dict) and m.get('id')==self.seq),None)
                else:
                    obj = json.loads(text)
                if not isinstance(obj,dict) or obj.get('id') != self.seq:
                    raise FetchError('MCP reply ID/envelope mismatch')
                if _reflected(obj,self._token):
                    raise FetchError('Decoded MCP credential reflection rejected')
                if obj.get('error'):
                    raise FetchError('MCP rejected request; no retry, quota bypass or upgrade')
                result = obj.get('result')
                if not isinstance(result,dict) or result.get('isError'):
                    raise FetchError('MCP tool failed; no retry, quota bypass or upgrade')
                return result
        except requests.RequestException:
            raise FetchError('MCP network/TLS failure; details withheld') from None
        except (UnicodeError,json.JSONDecodeError):
            raise FetchError('MCP reply encoding/JSON invalid') from None

    @staticmethod
    def _check(params):
        if not isinstance(params,dict) or params.get('name') not in TOOLS:
            raise FetchError('MCP tool outside approved read-only allow-list')
        args = params.get('arguments',{})
        if args.get('symbol') not in SYMBOLS:
            raise FetchError('MCP symbol outside entitlement scope')
        end = args.get('end_date')
        if params['name']=='get_price_history':
            try:parsed=date.fromisoformat(end)
            except (ValueError,TypeError):raise FetchError('MCP cursor date invalid') from None
            if not LISTED[args['symbol']] <= parsed.isoformat() <= '2026-11-06':
                raise FetchError('MCP cursor outside approved listed-history scope')
        expected = ({'symbol':args['symbol'],'days':2000,'interval':'daily','end_date':end}
                    if params['name']=='get_price_history' else {'symbol':args['symbol']})
        if args != expected:
            raise FetchError('MCP arguments outside approved maximum-window request')

    def initialize(self):
        result = self._rpc('initialize',dict(protocolVersion='2025-03-26',capabilities={},
                          clientInfo=dict(name='local-paper-research',version='1.0')))
        version = result.get('protocolVersion')
        if version not in ('2025-03-26','2025-06-18','2025-11-25'):
            raise FetchError('Unsupported negotiated MCP protocol')
        self.headers['MCP-Protocol-Version'] = version
        self._rpc('notifications/initialized',notification=True)

    def tool(self,name,args):
        params = dict(name=name,arguments=args)
        self._check(params)
        key = hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest()
        cached, checksum = self.cache/(key+'.json'),self.cache/(key+'.sha256')
        if cached.exists():
            if cached.stat().st_size > MAX_BYTES or not checksum.is_file():
                raise FetchError('Invalid MCP cache')
            raw = cached.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=checksum.read_text(encoding='ascii').strip():
                raise FetchError('MCP cache checksum mismatch')
            result = json.loads(raw)
            if _reflected(result,self._token):
                raise FetchError('MCP cache credential reflection rejected')
            hit=True
        else:
            if self.calls >= MAX_TOOL_CALLS:
                raise FetchError('MCP twelve-tool local paging budget exhausted')
            self.calls += 1
            result = self._rpc('tools/call',params)
            raw = json.dumps(result,allow_nan=False).encode('utf-8')
            with cached.open('xb') as fh:fh.write(raw)
            with checksum.open('x',encoding='ascii') as fh:fh.write(hashlib.sha256(raw).hexdigest())
            hit=False
        self.receipts.append(dict(tool=name,symbol=args['symbol'],cache_hit=hit,
                                  sha256=hashlib.sha256(raw).hexdigest()))
        return result
