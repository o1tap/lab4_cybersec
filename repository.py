"""Модуль сховища даних (Repository Pattern) з дотриманням принципу OCP."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from sqlmodel import Session, SQLModel, create_engine, select

from models import Server, ServerCreate, ServerUpdate

# Рядок підключення до PostgreSQL у Docker контейнері
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/security_db"

# Двигун підключення SQLModel (psycopg 3)
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Створення всіх таблиць у базі даних (якщо вони ще не створені)."""
    SQLModel.metadata.create_all(engine)


class AbstractServerRepository(ABC):
    """Абстрактний інтерфейс сховища серверів (OCP Контракт)."""

    @abstractmethod
    def get_all(self) -> Sequence[Server]:
        """Отримати список усіх серверів."""
        pass

    @abstractmethod
    def get_by_id(self, server_id: int) -> Server | None:
        """Отримати один сервер за ID."""
        pass

    @abstractmethod
    def create(self, server_data: ServerCreate) -> Server:
        """Створити новий сервер."""
        pass

    @abstractmethod
    def update(self, server_id: int, server_data: ServerUpdate) -> Server | None:
        """Оновити існуючий сервер."""
        pass

    @abstractmethod
    def delete(self, server_id: int) -> bool:
        """Видалити сервер за ID."""
        pass


class PostgresServerRepository(AbstractServerRepository):
    """Конкретна реалізація сховища для PostgreSQL через SQLModel/SQLAlchemy."""

    def get_all(self) -> Sequence[Server]:
        """Отримує всі записи серверів із БД."""
        with Session(engine) as session:
            statement = select(Server)
            return session.exec(statement).all()

    def get_by_id(self, server_id: int) -> Server | None:
        """Шукає сервер за первинним ключем (ID)."""
        with Session(engine) as session:
            return session.get(Server, server_id)

    def create(self, server_data: ServerCreate) -> Server:
        """Додає новий сервер у базу даних PostgreSQL."""
        with Session(engine) as session:
            db_server = Server.model_validate(server_data)
            session.add(db_server)
            session.commit()
            session.refresh(db_server)
            return db_server

    def update(self, server_id: int, server_data: ServerUpdate) -> Server | None:
        """Оновлює передані поля сервера."""
        with Session(engine) as session:
            db_server = session.get(Server, server_id)
            if not db_server:
                return None
            # Дамп полів, які дійсно були передані у запиті (exclude_unset=True)
            update_dict = server_data.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(db_server, key, value)
            session.add(db_server)
            session.commit()
            session.refresh(db_server)
            return db_server

    def delete(self, server_id: int) -> bool:
        """Видаляє сервер та пов'язані з ним інциденти."""
        with Session(engine) as session:
            db_server = session.get(Server, server_id)
            if not db_server:
                return False
            session.delete(db_server)
            session.commit()
            return True
