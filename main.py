"""Головний модуль FastAPI веб-інтерфейсу REST API."""

from collections.abc import Sequence

from fastapi import FastAPI, HTTPException, status

from models import (
    Server,
    ServerCreate,
    ServerUpdate,
)
from repository import AbstractServerRepository, PostgresServerRepository, init_db

app = FastAPI(
    title="CyberSecurity Asset Management REST API",
    description="Лабораторна робота №4 (Варіант 13: Сервери та Інциденти)",
    version="1.0.0",
)

repo: AbstractServerRepository = PostgresServerRepository()


@app.on_event("startup")
def on_startup() -> None:
    """Автоматична ініціалізація БД при запуску сервера."""
    init_db()


@app.get(
    "/servers",
    response_model=list[Server],
    status_code=status.HTTP_200_OK,
    summary="Отримати список усіх серверів",
)
def get_all_servers() -> Sequence[Server]:
    """GET: Повертає список усіх серверів разом із їхніми інцидентами з БД."""
    return repo.get_all()


@app.get(
    "/servers/{server_id}",
    response_model=Server,
    status_code=status.HTTP_200_OK,
    summary="Отримати один сервер за ID",
)
def get_server_by_id(server_id: int) -> Server:
    """GET: Повертає один сервер або 404, якщо його не існує."""
    server = repo.get_by_id(server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сервер з ID {server_id} не знайдено у базі даних!",
        )
    return server


@app.post(
    "/servers",
    response_model=Server,
    status_code=status.HTTP_201_CREATED,
    summary="Створити новий сервер (з Regex-валідацією IP)",
)
def create_server(server_data: ServerCreate) -> Server:
    """POST: Перевіряє IP-адресу через Regex і зберігає новий сервер у БД."""
    return repo.create(server_data)


@app.put(
    "/servers/{server_id}",
    response_model=Server,
    status_code=status.HTTP_200_OK,
    summary="Оновити дані сервера за ID",
)
def update_server(server_id: int, server_data: ServerUpdate) -> Server:
    """PUT: Оновлює поля сервера або повертає 404."""
    updated_server = repo.update(server_id, server_data)
    if not updated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сервер з ID {server_id} не знайдено у базі даних!",
        )
    return updated_server


@app.delete(
    "/servers/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити сервер за ID",
)
def delete_server(server_id: int) -> None:
    """DELETE: Видаляє сервер із бази даних (каскадно видаляючи його інциденти)."""
    success = repo.delete(server_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сервер з ID {server_id} не знайдено у базі даних!",
        )
    return None
