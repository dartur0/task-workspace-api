import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool, 
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_register_user_success():
    response = client.post("/auth/register", json={
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data
    assert "password" not in data 


def test_login_user_success():
    client.post("/auth/register", json={
        "email": "loginuser@example.com",
        "full_name": "Login User",
        "password": "loginpassword123"
    })
    
    response = client.post("/auth/login", data={
        "username": "loginuser@example.com",
        "password": "loginpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "full_name": "Wrong Pass User",
        "password": "realpassword123"
    })
    
    response = client.post("/auth/login", data={
        "username": "wrongpass@example.com",
        "password": "WRONGpassword!"
    })
    assert response.status_code == 401

def test_create_workspace_unauthorized():
    response = client.post("/workspaces/", json={"title": "Secret Workspace"})
    assert response.status_code == 401


def test_create_and_get_workspace_success():
    client.post("/auth/register", json={
        "email": "owner@example.com",
        "full_name": "Owner User",
        "password": "password123"
    })
    login_res = client.post("/auth/login", data={
        "username": "owner@example.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    ws_res = client.post("/workspaces/", json={"title": "Dev Team"}, headers=headers)
    assert ws_res.status_code == 201
    assert ws_res.json()["title"] == "Dev Team"

    list_res = client.get("/workspaces/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["title"] == "Dev Team"