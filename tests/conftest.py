import pytest

from _audit_helpers.lineage import install_collector


@pytest.fixture(scope="session", autouse=True)
def _audit_lineage_collector():
    install_collector()
    yield
