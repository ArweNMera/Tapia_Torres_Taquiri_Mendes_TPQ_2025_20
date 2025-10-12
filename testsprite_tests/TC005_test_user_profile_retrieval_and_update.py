import requests

BASE_URL = "http://localhost:8000"
USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_user_profile_retrieval_and_update():
    login_url = f"{BASE_URL}/api/v1/auth/login"
    me_url = f"{BASE_URL}/api/v1/usuarios/me"
    profile_url = f"{BASE_URL}/api/v1/usuarios/profile"

    # Step 1: Authenticate user and get JWT token
    login_payload = {"usr_usuario": USERNAME, "usr_password": PASSWORD}
    try:
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert (
            login_resp.status_code == 200
        ), f"Login failed with status {login_resp.status_code}"
        login_data = login_resp.json()
        access_token = login_data.get("access_token")
        token_type = login_data.get("token_type")
        assert (
            access_token is not None and token_type is not None
        ), "Access token or token type missing in login response"
    except Exception as e:
        raise AssertionError(f"Exception during login: {e}")

    headers = {"Authorization": f"{token_type} {access_token}"}

    # Step 2: Retrieve user profile
    try:
        me_resp = requests.get(me_url, headers=headers, timeout=TIMEOUT)
        assert (
            me_resp.status_code == 200
        ), f"Failed to retrieve user profile with status {me_resp.status_code}"
        profile_data = me_resp.json()
        assert isinstance(
            profile_data, dict
        ), "User profile response is not a JSON object"
        # Minimal checks for expected fields (e.g., usr_usuario, usr_email) if present
        assert "usr_usuario" in profile_data, "usr_usuario not in user profile"
    except Exception as e:
        raise AssertionError(f"Exception during profile retrieval: {e}")

    # Step 3: Update user profile with valid data (modify some fields)
    update_payload = profile_data.copy()
    # For test, try updating "usr_nombre" and "usr_apellido" if present or add new fields
    original_nombre = update_payload.get("usr_nombre", "")
    original_apellido = update_payload.get("usr_apellido", "")
    update_payload["usr_nombre"] = (
        original_nombre + "_Updated" if original_nombre else "UpdatedName"
    )
    update_payload["usr_apellido"] = (
        original_apellido + "_Updated" if original_apellido else "UpdatedSurname"
    )

    try:
        update_resp = requests.put(
            profile_url, json=update_payload, headers=headers, timeout=TIMEOUT
        )
        assert (
            update_resp.status_code == 200
        ), f"Failed to update user profile with status {update_resp.status_code}"
        updated_data = update_resp.json()
        assert isinstance(
            updated_data, dict
        ), "User profile update response is not a JSON object"
        assert (
            updated_data.get("usr_nombre") == update_payload["usr_nombre"]
        ), "usr_nombre not updated correctly"
        assert (
            updated_data.get("usr_apellido") == update_payload["usr_apellido"]
        ), "usr_apellido not updated correctly"
    except Exception as e:
        raise AssertionError(f"Exception during profile update: {e}")


test_user_profile_retrieval_and_update()
