import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Les tests d'intégration (vrai testnet Hyperliquid) ne tournent que sur demande :
    HL_INTEGRATION=1 pytest tests/integration -v"""
    if os.getenv("HL_INTEGRATION") == "1":
        return
    skip = pytest.mark.skip(reason="integration test: set HL_INTEGRATION=1 to run against the testnet")
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(skip)
