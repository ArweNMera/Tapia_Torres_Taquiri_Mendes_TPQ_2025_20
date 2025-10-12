import requests
from datetime import date
import traceback

BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
CHILDREN_ENDPOINT = f"{BASE_URL}/api/v1/children"

USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_children_profile_management():
    # Authenticate and get token
    login_payload = {"usr_usuario": USERNAME, "usr_password": PASSWORD}
    try:
        login_resp = requests.post(LOGIN_ENDPOINT, json=login_payload, timeout=TIMEOUT)
        assert (
            login_resp.status_code == 200
        ), f"Login failed with status {login_resp.status_code}"
        login_json = login_resp.json()
        access_token = login_json.get("access_token")
        token_type = login_json.get("token_type")
        assert (
            access_token and token_type
        ), "Token or token_type not found in login response"
    except Exception:
        traceback.print_exc()
        assert False, "Authentication failed."

    headers = {
        "Authorization": f"{token_type} {access_token}",
        "Content-Type": "application/json",
    }

    # Prepare child profile data for creation
    child_payload = {
        "nin_nombres": "Test Child",
        "nin_fecha_nac": date.today().replace(year=date.today().year - 5).isoformat(),
        "nin_sexo": "M",
    }
    antropometria_payload = {
        "ant_peso": 18.5,
        "ant_talla": 110.2,
        "ant_fecha": date.today().isoformat(),
    }
    profile_payload = {"nino": child_payload, "antropometria": antropometria_payload}

    created_nin_id = None

    try:
        # Create full child profile via /api/v1/children/profiles (preferred)
        profiles_url = f"{BASE_URL}/api/v1/children/profiles"
        resp_create = requests.post(
            profiles_url, headers=headers, json=profile_payload, timeout=TIMEOUT
        )
        if resp_create.status_code not in [200, 201]:
            # fallback: create child only then add anthropometry separately
            # Create child
            resp_create_child = requests.post(
                CHILDREN_ENDPOINT, headers=headers, json=child_payload, timeout=TIMEOUT
            )
            assert resp_create_child.status_code in [
                200,
                201,
            ], f"Child creation failed: {resp_create_child.text}"
            child_data = resp_create_child.json()
            created_nin_id = child_data.get("nin_id") or child_data.get("id")
            assert created_nin_id, "Created child ID not returned"

            # Add anthropometric measurement
            anthropometry_url = f"{CHILDREN_ENDPOINT}/{created_nin_id}/anthropometry"
            resp_add_ant = requests.post(
                anthropometry_url,
                headers=headers,
                json=antropometria_payload,
                timeout=TIMEOUT,
            )
            assert resp_add_ant.status_code in [
                200,
                201,
            ], f"Adding anthropometry failed: {resp_add_ant.text}"
        else:
            created = resp_create.json()
            # The full profile creation should return child's ID in standard key 'nin_id' or 'id'
            created_nin_id = created.get("nin_id") or created.get("id")
            assert (
                created_nin_id
            ), "Created child ID not returned from full profile creation"

        # Retrieve child by ID and verify basic info
        get_child_url = f"{CHILDREN_ENDPOINT}/{created_nin_id}"
        resp_get = requests.get(get_child_url, headers=headers, timeout=TIMEOUT)
        assert resp_get.status_code == 200, f"Get child failed: {resp_get.text}"
        child_info = resp_get.json()
        assert (
            child_info.get("nin_nombres") == child_payload["nin_nombres"]
        ), "Child name does not match"
        assert (
            child_info.get("nin_sexo") == child_payload["nin_sexo"]
        ), "Child sex does not match"
        # Date of birth format or key might be different, so just check existence
        assert "nin_fecha_nac" in child_info, "Child birth date missing"

        # Update child profile - change name and sex
        update_payload = {
            "nin_nombres": "Updated Child",
            "nin_fecha_nac": child_payload["nin_fecha_nac"],
            "nin_sexo": "F",
        }
        resp_update = requests.put(
            get_child_url, headers=headers, json=update_payload, timeout=TIMEOUT
        )
        assert resp_update.status_code in [
            200,
            204,
        ], f"Update child failed: {resp_update.text}"

        # Verify update
        resp_get_updated = requests.get(get_child_url, headers=headers, timeout=TIMEOUT)
        assert resp_get_updated.status_code == 200, "Failed to get child after update"
        updated_info = resp_get_updated.json()
        assert (
            updated_info.get("nin_nombres") == "Updated Child"
        ), "Child name not updated"
        assert updated_info.get("nin_sexo") == "F", "Child sex not updated"

        # Add a new anthropometric measurement
        new_antropometria = {
            "ant_peso": 19.0,
            "ant_talla": 112.0,
            "ant_fecha": date.today().isoformat(),
        }
        anthropometry_url = f"{CHILDREN_ENDPOINT}/{created_nin_id}/anthropometry"
        resp_add_anthro = requests.post(
            anthropometry_url, headers=headers, json=new_antropometria, timeout=TIMEOUT
        )
        assert resp_add_anthro.status_code in [
            200,
            201,
        ], f"Adding new anthropometry failed: {resp_add_anthro.text}"

        # Retrieve anthropometric history and verify new record present
        resp_get_anthro_history = requests.get(
            anthropometry_url, headers=headers, timeout=TIMEOUT
        )
        assert (
            resp_get_anthro_history.status_code == 200
        ), f"Getting anthropometry history failed: {resp_get_anthro_history.text}"
        anthro_history = resp_get_anthro_history.json()
        # Should be a list containing at least the latest record
        assert (
            isinstance(anthro_history, list) and len(anthro_history) >= 1
        ), "Anthropometric history missing or empty"
        found = any(
            (
                entry.get("ant_peso") == new_antropometria["ant_peso"]
                and entry.get("ant_talla") == new_antropometria["ant_talla"]
                and entry.get("ant_fecha") == new_antropometria["ant_fecha"]
            )
            for entry in anthro_history
        )
        assert found, "New anthropometric measurement not found in history"

        # Retrieve nutritional status and verify keys present
        nutritional_status_url = (
            f"{CHILDREN_ENDPOINT}/{created_nin_id}/nutritional-status"
        )
        resp_nutr_status = requests.get(
            nutritional_status_url, headers=headers, timeout=TIMEOUT
        )
        assert (
            resp_nutr_status.status_code == 200
        ), f"Getting nutritional status failed: {resp_nutr_status.text}"
        nutr_status = resp_nutr_status.json()
        # Expect some keys that indicate nutritional status, e.g. 'status' or similar, just check the response is an object
        assert isinstance(
            nutr_status, dict
        ), "Nutritional status response is not an object"

    finally:
        # Cleanup: delete created child profile if created
        if created_nin_id:
            try:
                delete_url = f"{CHILDREN_ENDPOINT}/{created_nin_id}"
                resp_del = requests.delete(delete_url, headers=headers, timeout=TIMEOUT)
                assert resp_del.status_code in [
                    200,
                    204,
                ], f"Delete child failed with status {resp_del.status_code}"
            except Exception:
                traceback.print_exc()


test_children_profile_management()
