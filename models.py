"""Модуль доменних моделей даних та Pydantic-схем.

Реалізує ERD-структуру Варіанта 13 (Сервери та Інциденти 1:N) та Regex-валідацію.
"""

import re
from datetime import datetime

from pydantic import BaseModel, field_validator
from sqlmodel import Field, Relationship, SQLModel

# =============================================================================
# 1. РЕГУЛЯРНІ ВИРАЗИ (REGEX) ДЛЯ ВАЛІДАЦІЇ ВХІДНИХ ДАНИХ
# =============================================================================
# Валідація IPv4 адреси (від 0.0.0.0 до 255.255.255.255)
IP_REGEX = (
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

# Валідація корпоративного або звичайного Email
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


# =============================================================================
# 2. СУТНІСТЬ 1: СЕРВЕР (SERVER)
# =============================================================================
class ServerBase(SQLModel):
    """Базова модель сервера з загальними полями та валідацією."""

    hostname: str = Field(max_length=100, description="Мережеве ім'я хоста")
    ip_address: str = Field(max_length=15, description="IP-адреса сервера")
    datacenter: str = Field(
        default="Kyiv-DC1", max_length=50, description="Датацентр розміщення"
    )

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        """Перевіряє відповідність IP-адреси формату IPv4 через Regex."""
        if not re.match(IP_REGEX, value):
            raise ValueError("Некоректний формат IP-адреси! Очікується стандарт IPv4.")
        return value


class Server(ServerBase, table=True):
    """Таблиця 'servers' у базі даних PostgreSQL."""

    __tablename__ = "servers"

    id: int | None = Field(default=None, primary_key=True)

    # Відношення 1:N (Один сервер має список інцидентів)
    # cascade_delete=True означає, що при видаленні сервера видаляться і його інциденти
    incidents: list["SecurityIncident"] = Relationship(
        back_populates="server", cascade_delete=True
    )


# =============================================================================
# 3. СУТНІСТЬ 2: ІНЦИДЕНТ БЕЗПЕКИ (SECURITY INCIDENT)
# =============================================================================
class SecurityIncidentBase(SQLModel):
    """Базова модель інциденту з валідацією Email аналітика."""

    title: str = Field(max_length=200, description="Короткий опис інциденту")
    severity: str = Field(
        default="MEDIUM", description="Рівень загрози: LOW, MEDIUM, HIGH, CRITICAL"
    )
    reporter_email: str = Field(
        max_length=100, description="Email аналітика, що зафіксував інцидент"
    )
    server_id: int = Field(
        foreign_key="servers.id", description="ID пов'язаного сервера (FK)"
    )

    @field_validator("reporter_email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Перевіряє коректність синтаксису email за допомогою Regex."""
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Некоректний формат email адреси аналітика!")
        return value


class SecurityIncident(SecurityIncidentBase, table=True):
    """Таблиця 'security_incidents' у базі даних PostgreSQL."""

    __tablename__ = "security_incidents"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Зворотне посилання 1:N (кожен інцидент належить конкретному серверу)
    server: Server | None = Relationship(back_populates="incidents")


# =============================================================================
# 4. DTO (DATA TRANSFER OBJECTS) СХЕМИ ДЛЯ REST API
# =============================================================================
class ServerCreate(ServerBase):
    """Схема даних для створення нового сервера (POST)."""

    pass


class ServerUpdate(BaseModel):
    """Схема даних для часткового оновлення сервера (PUT). All fields optional."""

    hostname: str | None = None
    ip_address: str | None = None
    datacenter: str | None = None


class SecurityIncidentCreate(SecurityIncidentBase):
    """Схема даних для створення нового інциденту (POST)."""

    pass


class SecurityIncidentUpdate(BaseModel):
    """Схема даних для часткового оновлення інциденту (PUT)."""

    title: str | None = None
    severity: str | None = None
    reporter_email: str | None = None
