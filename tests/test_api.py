import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_supplier_crud(client):
    r = client.post("/suppliers", json={"name": "Acme Steel", "rating": 4.5})
    assert r.status_code == 201
    sid = r.json()["id"]
    assert client.get(f"/suppliers/{sid}").json()["name"] == "Acme Steel"
    r = client.put(f"/suppliers/{sid}", json={"name": "Acme Steel Ltd", "rating": 4.0})
    assert r.json()["name"] == "Acme Steel Ltd"
    assert client.delete(f"/suppliers/{sid}").status_code == 204
    assert client.get(f"/suppliers/{sid}").status_code == 404


def test_duplicate_supplier_rejected(client):
    client.post("/suppliers", json={"name": "Acme"})
    assert client.post("/suppliers", json={"name": "Acme"}).status_code == 409


def test_quote_validation(client):
    sid = client.post("/suppliers", json={"name": "S1"}).json()["id"]
    pid = client.post("/products", json={"name": "Bolt M8"}).json()["id"]
    bad = client.post("/quotes", json={"supplier_id": sid, "product_id": pid, "unit_price": -5, "lead_time_days": 3})
    assert bad.status_code == 422
    missing = client.post("/quotes", json={"supplier_id": 999, "product_id": pid, "unit_price": 5, "lead_time_days": 3})
    assert missing.status_code == 404


def test_quote_filtering(client):
    s1 = client.post("/suppliers", json={"name": "S1"}).json()["id"]
    s2 = client.post("/suppliers", json={"name": "S2"}).json()["id"]
    p = client.post("/products", json={"name": "Bolt"}).json()["id"]
    client.post("/quotes", json={"supplier_id": s1, "product_id": p, "unit_price": 10, "lead_time_days": 5})
    client.post("/quotes", json={"supplier_id": s2, "product_id": p, "unit_price": 9, "lead_time_days": 7})
    assert len(client.get(f"/quotes?product_id={p}").json()) == 2
    assert len(client.get(f"/quotes?supplier_id={s1}").json()) == 1
