from datalake.config.settings import Settings


def test_settings_builds_database_url(monkeypatch) -> None:
    monkeypatch.setenv("POSTGRES_DB", "test_database")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    settings = Settings(_env_file=None)
    url = settings.database_url

    assert url.drivername == "postgresql+psycopg"
    assert url.username == "test_user"
    assert url.password == "test_password"
    assert url.host == "localhost"
    assert url.port == 5432
    assert url.database == "test_database"
