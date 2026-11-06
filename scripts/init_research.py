"""Create a new INR 100,000 paper portfolio; refuse to replace existing state."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nsebot.ledger import Ledger


def initialize(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    for mode, capital in (('swing', 33333.33), ('intraday', 33333.33), ('momentum', 33333.34)):
        Ledger(str(root), mode, capital).save()
    return root


if __name__ == '__main__':
    destination = Path(__file__).resolve().parent.parent / 'local_research' / 'state'
    initialize(destination)
    print('Created INR 100,000 paper portfolio at', destination)
