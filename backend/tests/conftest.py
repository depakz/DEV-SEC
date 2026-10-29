import sys
from pathlib import Path

# Allow `from app...` imports when pytest is run from backend/ without
# the package being pip-installed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
