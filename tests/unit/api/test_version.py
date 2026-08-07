from importlib.metadata import version

from datalake.api.app import create_app


def test_app_version_matches_package_metadata() -> None:
    app = create_app()

    expected = version(
        "datalake-health-platform"
    )

    assert app.version == expected
