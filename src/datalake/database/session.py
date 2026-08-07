from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker

from datalake.database.engine import engine


SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

SessionFactoryType = sessionmaker[Session]


@contextmanager
def session_scope(
    session_factory: SessionFactoryType = SessionFactory,
) -> Iterator[Session]:
    """Fornece uma sessão com commit, rollback e fechamento."""

    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()