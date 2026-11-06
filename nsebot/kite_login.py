"""Broker login is disabled in this paper-only research checkout."""

import sys


def main(argv=None):
    print('Live broker login is disabled. Use paper execution; no credentials are needed.')
    return 2


if __name__ == '__main__':
    sys.exit(main())
