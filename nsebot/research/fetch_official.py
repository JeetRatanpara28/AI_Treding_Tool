"""Explicitly approved official-source download; no trading or automatic scheduling."""

import argparse
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
import zipfile

import pandas as pd
from curl_cffi import requests

from .source_check import load_official_snapshot

BASE = 'https://nsearchives.nseindia.com/content/'
SOURCES = {
    'calendar': [BASE + 'circulars/' + name + '.pdf' for name in
                 ('CMTR71775', 'CMTR72260', 'CMTR72349', 'CMTR76941', 'CMTR77334')],
    'closes': [BASE + 'cm/BhavCopy_NSE_CM_0_0_0_20261106_F_0000.csv.zip',
               BASE + 'indices/ind_close_all_06112026.csv'],
}
MUHURAT_HASH = 'ce94ee1c54d98eccdf3c30fa0673ae2b6a49ea4ed4a72fb83d826f4359f71d58'


def download(group, destination, get=None):
    """Bounded allow-list, fresh destination, strict errors, default libcurl transport."""
    get = get or requests.get
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    manifest = {'group': group, 'transport': 'curl_cffi default; no impersonation or custom proxy',
                'status': 'PASS', 'sources': []}
    for url in SOURCES[group]:
        name = Path(urlparse(url).path).name
        entry = {'url': url, 'file': name}
        try:
            response = get(url, timeout=20, allow_redirects=False)
            if response.status_code != 200:
                raise ValueError(f'HTTP {response.status_code}; redirects and access blocks are not bypassed')
            payload = response.content
            if not payload or len(payload) > 10_000_000:
                raise ValueError('empty or oversized source file')
            if name.endswith('.pdf') and not payload.startswith(b'%PDF-'):
                raise ValueError('official PDF URL returned non-PDF content')
            if name.endswith('.zip'):
                with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                    members = archive.infolist()
                    if len(members) != 1 or not members[0].filename.endswith('.csv'):
                        raise ValueError('unexpected bhavcopy ZIP structure')
                    if members[0].file_size > 50_000_000:
                        raise ValueError('oversized expanded bhavcopy')
                    # Do not extract archive paths supplied by a remote server.
                    with (root / 'cash_report.csv').open('xb') as fh:
                        fh.write(archive.read(members[0]))
            if name.endswith('.csv'):
                frame = pd.read_csv(io.BytesIO(payload), nrows=1)
                if not {'Index Name', 'Index Date', 'Closing Index Value'}.issubset(frame.columns):
                    raise ValueError('unexpected index CSV schema')
            digest = hashlib.sha256(payload).hexdigest()
            if name == 'CMTR76941.pdf' and digest != MUHURAT_HASH:
                raise ValueError('Muhurat PDF differs from the visually reviewed source; re-review required')
            with (root / name).open('xb') as fh:
                fh.write(payload)
            entry.update(status='PASS', sha256=digest, bytes=len(payload))
        except Exception as exc:
            entry.update(status='FAIL', error=f'{type(exc).__name__}: {exc}')
            manifest['status'] = 'FAIL'
        manifest['sources'].append(entry)
    if group == 'closes' and manifest['status'] == 'PASS':
        try:
            frames = load_official_snapshot(root / 'cash_report.csv', root / 'ind_close_all_06112026.csv',
                                            '2026-11-06')
            manifest['verified_closes'] = {s: float(f['close'].iloc[0]) for s, f in frames.items()}
        except Exception as exc:
            manifest.update(status='FAIL', validation_error=f'{type(exc).__name__}: {exc}')
    with (root / 'manifest.json').open('x', encoding='utf-8') as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=SOURCES, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--allow-network', action='store_true', help='requires explicit user approval first')
    args = parser.parse_args(argv)
    if not args.allow_network:
        parser.error('Explicit download approval is required before using --allow-network.')
    result = download(args.group, args.out)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 3


if __name__ == '__main__':
    raise SystemExit(main())
