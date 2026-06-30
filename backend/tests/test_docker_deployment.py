from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_backend_dockerfile_runs_uvicorn():
    content = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM python:" in content
    assert "pip install" in content
    assert "uvicorn" in content
    assert "app.main:app" in content


def test_frontend_nginx_proxies_api_and_supports_history_fallback():
    nginx_conf = (ROOT / "frontend" / "nginx.conf").read_text(encoding="utf-8")
    dockerfile = (ROOT / "frontend" / "Dockerfile").read_text(encoding="utf-8")

    assert "FROM node:" in dockerfile
    assert "FROM nginx:" in dockerfile
    assert "npm" in dockerfile and "build" in dockerfile
    assert "proxy_pass http://backend:8000" in nginx_conf
    assert "try_files $uri $uri/ /index.html" in nginx_conf


def test_compose_defines_postgres_backend_and_frontend_services():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "postgres:" in compose
    assert "backend:" in compose
    assert "frontend:" in compose
    assert "postgres_data:" in compose
    assert "postgresql+psycopg://" in compose
    assert "8000" in compose
    assert "${FRONTEND_PORT:-8080}:80" in compose
