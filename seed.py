"""Скрипт початкового заповнення бази даних (50+ записів)."""

import random

from sqlmodel import Session, select

from models import SecurityIncident, Server
from repository import engine, init_db


def seed_database() -> None:
    """Заповнює базу даних тестовими серверами та інцидентами."""
    init_db()

    with Session(engine) as session:
        if session.exec(select(Server)).first():
            print("[*] База даних вже містить записи. Пропускаємо заповнення.")
            return

        print("[*] Генерація 10 серверів та 50 інцидентів безпеки...")
        datacenters = ["Kyiv-DC1", "Lviv-DC2", "Odesa-DC1", "Frankfurt-EC1"]
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        servers = []
        for i in range(1, 11):
            server = Server(
                hostname=f"srv-sec-node{i:02d}.local",
                ip_address=f"192.168.1.{10 + i}",
                datacenter=random.choice(datacenters),
            )
            session.add(server)
            servers.append(server)

        session.commit()

        for server in servers:
            session.refresh(server)

        # Цикл з правильними відступами у 4 пробіли
        for j in range(1, 51):
            srv = random.choice(servers)
            assert srv.id is not None  # Вказуємо mypy, що id існує
            incident = SecurityIncident(
                title=f"Виявлено аномальний трафік / Спроба brute-force #{j}",
                severity=random.choice(severities),
                reporter_email=f"analyst{random.randint(1, 5)}@cybersec.ua",
                server_id=srv.id,
            )
            session.add(incident)

        session.commit()
        print("[+] Базу даних успішно заповнено (10 серверів, 50 інцидентів)!")


if __name__ == "__main__":
    seed_database()
