"""Root conftest.py -- configures pytest for the curriculum.

Adds the repo root to sys.path so that shared/ imports work
from any week directory. Also adds the current test file's directory
so that week-local imports (e.g., 'from agent import ...') resolve.
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_collection_modifyitems(config, items):
    """Add the test file's directory to sys.path before each test runs."""
    dirs_added = set()
    for item in items:
        test_dir = str(item.fspath.dirpath())
        if test_dir not in dirs_added:
            if test_dir not in sys.path:
                sys.path.insert(0, test_dir)
            dirs_added.add(test_dir)
