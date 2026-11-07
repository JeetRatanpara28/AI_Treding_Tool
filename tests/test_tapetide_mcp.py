"""Fake MCP transport; no user token or authenticated service access."""
import json

import pytest

from nsebot.research.tapetide_fetch import FetchError
from nsebot.research.tapetide_mcp import MCPHistoryClient,URL

TOKEN='tpt_rt_SYNTHETIC_MCP_ONLY_12345678'
PROOF={'plan':'free','notice_code':'api_access_not_in_plan'}


class Reply:
    def __init__(self,result=None,status=200,raw=None):
        self.status_code=status
        self.result=result
        self.raw=raw
        self.headers={}
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def iter_content(self,size):yield self.raw


class Session:
    def __init__(self,replies):self.replies=list(replies);self.calls=[]
    def post(self,url,**kwargs):
        self.calls.append((url,kwargs))
        reply=self.replies.pop(0)
        if reply.raw is None:
            reply.raw=json.dumps({'jsonrpc':'2.0','id':kwargs['json']['id'],'result':reply.result}).encode()
        return reply


def args():return dict(symbol='JIOFIN',days=2000,interval='daily',end_date='2026-11-06')


def test_only_verified_free_plan_can_construct_client(tmp_path):
    with pytest.raises(FetchError,match='Free-plan'):
        MCPHistoryClient(TOKEN,tmp_path,{'plan':'paid'})


def test_entitlement_tool_cache_never_invokes_account_writes_or_redirects(tmp_path):
    s=Session([Reply(dict(content=[dict(type='text',text='{"rows":[]}')]))])
    c=MCPHistoryClient(TOKEN,tmp_path,PROOF,s)
    c.tool('get_price_history',args())
    c.tool('get_price_history',args())
    assert c.calls==1 and len(s.calls)==1
    assert s.calls[0][0]==URL
    assert s.calls[0][1]['allow_redirects'] is False
    assert s.trust_env is False
    with pytest.raises(FetchError,match='allow-list'):
        c.tool('add_portfolio_stocks',{'symbol':'JIOFIN'})
    with pytest.raises(FetchError,match='scope'):
        c.tool('get_price_history',{**args(),'symbol':'OTHER'})
    with pytest.raises(FetchError,match='arguments'):
        c.tool('get_price_history',{**args(),'days':9999})
    with pytest.raises(FetchError,match='scope'):
        c.tool('get_price_history',{**args(),'end_date':'2027-01-01'})
    assert len(s.calls)==1


@pytest.mark.parametrize('reply',[Reply(status=302,raw=b'redirect'),
                                 Reply(dict(isError=True,content=[]))])
def test_mcp_errors_stop_without_retry_or_cache(tmp_path,reply):
    s=Session([reply]);c=MCPHistoryClient(TOKEN,tmp_path,PROOF,s)
    with pytest.raises(FetchError):c.tool('get_price_history',args())
    assert len(s.calls)==1 and not list(tmp_path.glob('*.json'))


def test_escaped_reflected_token_is_not_cached(tmp_path):
    raw=json.dumps(dict(jsonrpc='2.0',id=1,result=dict(text=TOKEN))).replace('tpt_rt_','\\u0074pt_rt_').encode()
    c=MCPHistoryClient(TOKEN,tmp_path,PROOF,Session([Reply(raw=raw)]))
    with pytest.raises(FetchError,match='credential reflection'):
        c.tool('get_price_history',args())
    assert not list(tmp_path.glob('*.json'))


def test_paging_uses_bounded_dates_and_preserves_fixed_symbol_and_host(tmp_path):
    s=Session([Reply(dict(content=[]))])
    c=MCPHistoryClient(TOKEN,tmp_path,PROOF,s)
    c.tool('get_price_history',{**args(),'end_date':'2026-05-17'})
    assert s.calls[0][0]==URL
    assert s.calls[0][1]['json']['params']['arguments']['days']==2000
    c.calls=12
    with pytest.raises(FetchError,match='budget'):
        c.tool('get_price_history',{**args(),'end_date':'2026-01-01'})
    assert len(s.calls)==1


def test_nested_json_text_cannot_hide_a_reflected_token(tmp_path):
    text=json.dumps({'unexpected':TOKEN}).replace('tpt_rt_','\\u0074pt_rt_')
    reply=Reply(dict(content=[dict(type='text',text=text)]))
    c=MCPHistoryClient(TOKEN,tmp_path,PROOF,Session([reply]))
    with pytest.raises(FetchError,match='credential reflection'):
        c.tool('get_price_history',args())
    assert not list(tmp_path.glob('*.json'))
