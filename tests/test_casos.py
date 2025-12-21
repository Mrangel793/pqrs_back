import pytest
from fastapi.testclient import TestClient


def test_list_casos(client, auth_headers):
    """Test listar casos"""
    response = client.get("/api/v1/casos/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_create_caso(client, auth_headers):
    """Test crear caso"""
    caso_data = {
        "tipo": "peticion",
        "asunto": "Solicitud de información",
        "descripcion": "Requiero información sobre...",
        "prioridad": "media"
    }

    response = client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "peticion"
    assert data["asunto"] == "Solicitud de información"
    assert "numero_caso" in data
    assert data["numero_caso"].startswith("PQR-")


def test_get_caso(client, auth_headers):
    """Test obtener caso por ID"""
    # Primero crear un caso
    caso_data = {
        "tipo": "queja",
        "asunto": "Queja sobre servicio",
        "descripcion": "El servicio no cumplió con lo esperado",
        "prioridad": "alta"
    }

    create_response = client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)
    caso_id = create_response.json()["id"]

    # Obtener el caso
    response = client.get(f"/api/v1/casos/{caso_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == caso_id
    assert data["tipo"] == "queja"


def test_update_caso(client, auth_headers):
    """Test actualizar caso"""
    # Crear caso
    caso_data = {
        "tipo": "reclamo",
        "asunto": "Reclamo por cobro",
        "descripcion": "Cobro indebido",
        "prioridad": "media"
    }

    create_response = client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)
    caso_id = create_response.json()["id"]

    # Actualizar
    update_data = {
        "estado": "en_proceso",
        "prioridad": "alta"
    }

    response = client.put(f"/api/v1/casos/{caso_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "en_proceso"
    assert data["prioridad"] == "alta"


def test_delete_caso(client, auth_headers):
    """Test eliminar caso"""
    # Crear caso
    caso_data = {
        "tipo": "peticion",
        "asunto": "Test caso a eliminar",
        "descripcion": "Este caso será eliminado",
        "prioridad": "baja"
    }

    create_response = client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)
    caso_id = create_response.json()["id"]

    # Eliminar
    response = client.delete(f"/api/v1/casos/{caso_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verificar que no existe
    get_response = client.get(f"/api/v1/casos/{caso_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_filter_casos_by_tipo(client, auth_headers):
    """Test filtrar casos por tipo"""
    # Crear varios casos
    tipos = ["peticion", "queja", "reclamo"]
    for tipo in tipos:
        caso_data = {
            "tipo": tipo,
            "asunto": f"Test {tipo}",
            "descripcion": f"Descripción de {tipo}",
            "prioridad": "media"
        }
        client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)

    # Filtrar por tipo
    response = client.get("/api/v1/casos/?tipo=queja", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(caso["tipo"] == "queja" for caso in data["items"])


def test_pagination(client, auth_headers):
    """Test paginación de casos"""
    # Crear varios casos
    for i in range(15):
        caso_data = {
            "tipo": "peticion",
            "asunto": f"Caso {i}",
            "descripcion": f"Descripción {i}",
            "prioridad": "media"
        }
        client.post("/api/v1/casos/", json=caso_data, headers=auth_headers)

    # Primera página
    response = client.get("/api/v1/casos/?page=1&page_size=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["page"] == 1

    # Segunda página
    response = client.get("/api/v1/casos/?page=2&page_size=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["page"] == 2
