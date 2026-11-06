"""Windows research launcher: fixed interpreter via dailytask.bat, isolated state."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs='?', default='status',
                        choices=('init', 'status', 'test', 'swing', 'intraday', 'momentum', 'backtest'))
    parser.add_argument('--allow-network', action='store_true',
                        help='use only after approving public market data downloads')
    args = parser.parse_args()
    if args.command not in ('init', 'status', 'test') and not args.allow_network:
        parser.error('Approve public market data downloads before using --allow-network.')
    repo = Path(__file__).resolve().parent.parent
    os.chdir(repo)
    if args.command == 'init':
        from init_research import initialize
        initialize(repo / 'local_research' / 'state')
        print('Created INR 100,000 paper portfolio; no existing state was replaced.')
        return 0
    if args.command == 'test':
        runs = repo.parent / 'test-runs'
        runs.mkdir(exist_ok=True)
        fresh = tempfile.mkdtemp(prefix='suite-', dir=runs)
        return subprocess.call([sys.executable, '-X', 'utf8', '-m', 'pytest',
                                'tests', 'diagnostics', '-q', '--basetemp', str(Path(fresh) / 'pytest')])
    os.environ.update(PYTHONUTF8='1', NSEBOT_BROKER='paper',
                      NSEBOT_STATE=str(repo / 'local_research' / 'state'),
                      NSEBOT_RESULTS='E:/AI-Trading-Data/results/nsebot',
                      NSEBOT_DATA='E:/AI-Trading-Data', EMAIL_PASSWORD='',
                      SWING_CAPITAL='33333.33', INTRADAY_CAPITAL='33333.33',
                      MOMENTUM_CAPITAL='33333.34')
    return subprocess.call([sys.executable, '-X', 'utf8', '-m', 'nsebot', args.command])


if __name__ == '__main__':
    sys.exit(main())
