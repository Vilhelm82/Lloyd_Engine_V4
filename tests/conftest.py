import pytest

from _audit_helpers.lineage import install_collector


SLOW_TEST_FILES = {
    "test_task017b_multi_precision_instrument_model.py",
    "test_task017c_multi_precision_theorem2.py",
    "test_task025_path_law_discovery.py",
    "test_task026_lattice_anomaly_investigation.py",
    "test_task026c_prime_polarity_grid_stability.py",
    "test_task027_sr_four_form_cross_fixture.py",
    "test_task028_conditional_masks_joint_lattice_pure_algebraic.py",
    "test_task029_path_basis_rank_clustering.py",
    "test_task029b_methodology_refinement.py",
    "test_task029c_cbrt_four_form_battery.py",
    "test_task030_refinery_mvp.py",
    "test_task031_sterbenz_audit.py",
    "test_task032_quartic_lattice_grain_discrimination.py",
    "test_task033_schwarzschild_cbrt_transformed_n3.py",
    "test_task034_schwarzschild_quartic_transformed_n4.py",
}


def pytest_addoption(parser):
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="skip campaign/report regression tests marked as slow",
    )


def pytest_collection_modifyitems(config, items):
    skip_slow = config.getoption("--skip-slow")
    skip_marker = pytest.mark.skip(reason="slow campaign/report regression test skipped by --skip-slow")
    for item in items:
        if item.path.name in SLOW_TEST_FILES:
            item.add_marker(pytest.mark.slow)
            if skip_slow:
                item.add_marker(skip_marker)


@pytest.fixture(scope="session", autouse=True)
def _audit_lineage_collector():
    install_collector()
    yield
