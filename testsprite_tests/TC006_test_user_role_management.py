import requests

BASE_URL = "http://localhost:8000"
USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_user_role_management():
    session = requests.Session()
    token_type = None
    access_token = None
    # Authenticate and retrieve JWT token
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_payload = {
        "usr_usuario": USERNAME,
        "usr_password": PASSWORD,
    }
    try:
        login_resp = session.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token_data = login_resp.json()
        access_token = token_data.get("access_token")
        token_type = token_data.get("token_type")
        assert access_token and token_type, "Login response missing token information"

        headers = {
            "Authorization": f"{token_type} {access_token}",
            "Content-Type": "application/json",
        }

        # Create a new role
        create_role_url = f"{BASE_URL}/api/v1/usuarios/roles"
        role_data = {"rol_nombre": "test_role_api_tc006"}

        create_role_resp = session.post(
            create_role_url, json=role_data, headers=headers, timeout=TIMEOUT
        )
        assert create_role_resp.status_code in (
            200,
            201,
        ), f"Role creation failed: {create_role_resp.text}"
        created_role = create_role_resp.json()
        created_role_id = (
            created_role.get("rol_id")
            or created_role.get("id")
            or created_role.get("role_id")
        )
        assert (
            created_role_id is not None
        ), f"Created role ID not found in response: {created_role}"

        # Register new user for testing role change
        register_user_url = f"{BASE_URL}/api/v1/usuarios/register"
        test_user_data = {
            "usr_usuario": "test_user_api_tc006",
            "usr_email": "test_user_api_tc006@example.com",
            "usr_password": "TestPassword123!",
            "usr_nombre": "Test",
            "usr_apellido": "User",
        }
        register_resp = session.post(
            register_user_url, json=test_user_data, headers=headers, timeout=TIMEOUT
        )
        assert register_resp.status_code in (
            200,
            201,
        ), f"User registration failed: {register_resp.text}"
        registered_user = register_resp.json()
        usr_id = registered_user.get("usr_id") or registered_user.get("id")
        assert (
            usr_id is not None
        ), f"Registered user ID not found in response: {registered_user}"

        try:
            # Change the user's role to the newly created role
            change_role_url = f"{BASE_URL}/api/v1/usuarios/{usr_id}/role"
            change_role_payload = {"rol_id": created_role_id}
            change_role_resp = session.put(
                change_role_url,
                json=change_role_payload,
                headers=headers,
                timeout=TIMEOUT,
            )

            assert change_role_resp.status_code in (
                200,
                204,
            ), f"Changing user role failed: {change_role_resp.text}"

        finally:
            pass

    finally:
        if token_type and access_token:
            logout_url = f"{BASE_URL}/api/v1/auth/logout"
            logout_resp = session.post(
                logout_url,
                headers={"Authorization": f"{token_type} {access_token}"},
                timeout=TIMEOUT,
            )
            assert logout_resp.status_code in (
                200,
                204,
            ), f"Logout failed: {logout_resp.text}"


test_user_role_management()
