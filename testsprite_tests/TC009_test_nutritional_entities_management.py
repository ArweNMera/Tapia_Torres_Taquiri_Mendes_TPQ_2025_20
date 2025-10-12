import requests

BASE_URL = "http://localhost:8000"
USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_nutritional_entities_management():
    # Step 1: Authenticate to get JWT token
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_payload = {"usr_usuario": USERNAME, "usr_password": PASSWORD}
    try:
        login_response = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert (
            login_response.status_code == 200
        ), f"Login failed with status {login_response.status_code}"
        login_json = login_response.json()
        access_token = login_json.get("access_token")
        token_type = login_json.get("token_type")
        assert (
            access_token is not None and token_type is not None
        ), "Access token or token type missing in login response"
    except requests.RequestException as e:
        assert False, f"Login request failed: {e}"

    headers = {"Authorization": f"{token_type} {access_token}"}

    # Step 2: Get list of nutritional entities (/api/v1/entidades)
    entidades_url = f"{BASE_URL}/api/v1/entidades"
    try:
        entidades_response = requests.get(
            entidades_url, headers=headers, timeout=TIMEOUT
        )
        assert (
            entidades_response.status_code == 200
        ), f"Failed to get entidades with status {entidades_response.status_code}"
        entidades_json = entidades_response.json()
        assert isinstance(entidades_json, list) or isinstance(
            entidades_json, dict
        ), "Entidades response is not a list or dict as expected"
    except requests.RequestException as e:
        assert False, f"Entidades request failed: {e}"

    # Step 3: Get list of types of nutritional entities (/api/v1/entidades/tipos)
    tipos_url = f"{BASE_URL}/api/v1/entidades/tipos"
    try:
        tipos_response = requests.get(tipos_url, headers=headers, timeout=TIMEOUT)
        assert (
            tipos_response.status_code == 200
        ), f"Failed to get tipos with status {tipos_response.status_code}"
        tipos_json = tipos_response.json()
        assert isinstance(tipos_json, list) or isinstance(
            tipos_json, dict
        ), "Tipos response is not a list or dict as expected"
    except requests.RequestException as e:
        assert False, f"Tipos request failed: {e}"


test_nutritional_entities_management()
