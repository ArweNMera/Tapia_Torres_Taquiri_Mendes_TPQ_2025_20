import requests

BASE_URL = "http://localhost:8000"
USERNAME = "72890842@continental.edu.pe"
PASSWORD = "qwni0W6"
TIMEOUT = 30


def test_allergy_types_and_assignment():
    # Authenticate user to get Bearer token
    auth_url = f"{BASE_URL}/api/v1/auth/login"
    auth_payload = {"usr_usuario": USERNAME, "usr_password": PASSWORD}
    auth_resp = requests.post(auth_url, json=auth_payload, timeout=TIMEOUT)
    assert (
        auth_resp.status_code == 200
    ), f"Authentication failed with status {auth_resp.status_code}"
    auth_data = auth_resp.json()
    assert "access_token" in auth_data
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: GET allergy types
    allergy_types_url = f"{BASE_URL}/api/v1/alergias/tipos"
    get_resp = requests.get(allergy_types_url, headers=headers, timeout=TIMEOUT)
    assert get_resp.status_code == 200
    allergy_types_list = get_resp.json()
    assert isinstance(allergy_types_list, list)

    # Step 2: POST create a new allergy type
    new_allergy_payload = {"nombre": "Test Allergy Type TC008"}
    # Because schema is not fully defined for body, assume 'nombre' field is required for allergy type creation
    # Common practice: The API likely expects a JSON with at least a name or description

    # We'll try to create allergy type with the minimal valid payload
    post_resp = requests.post(
        allergy_types_url, json=new_allergy_payload, headers=headers, timeout=TIMEOUT
    )
    assert (
        post_resp.status_code == 201
    ), f"Failed to create allergy type, status {post_resp.status_code}"
    created_allergy = post_resp.json()
    assert "id" in created_allergy, "Created allergy type response missing 'id'"

    allergy_type_id = created_allergy["id"]

    try:
        # Step 3: Create a child to assign allergy if none available
        children_url = f"{BASE_URL}/api/v1/children"
        # Get current children list
        children_resp = requests.get(children_url, headers=headers, timeout=TIMEOUT)
        assert children_resp.status_code == 200
        children_list = children_resp.json()
        if not children_list:
            # Create a child profile
            create_child_payload = {
                "nin_nombres": "TC008 Test Child",
                "nin_fecha_nac": "2018-01-01",
                "nin_sexo": "M",
            }
            child_create_resp = requests.post(
                children_url,
                json=create_child_payload,
                headers=headers,
                timeout=TIMEOUT,
            )
            assert child_create_resp.status_code == 201
            child = child_create_resp.json()
            nin_id = child["id"]
            child_created = True
        else:
            nin_id = children_list[0]["id"]
            child_created = False

        # Step 4: Assign allergy to child: POST /api/v1/children/{nin_id}/allergies
        assign_allergy_url = f"{BASE_URL}/api/v1/children/{nin_id}/allergies"
        assign_payload = {"alergia_tipo_id": allergy_type_id}
        assign_resp = requests.post(
            assign_allergy_url, json=assign_payload, headers=headers, timeout=TIMEOUT
        )
        assert (
            assign_resp.status_code == 201
        ), f"Failed to assign allergy to child, status {assign_resp.status_code}"
        assigned_data = assign_resp.json()
        assert assigned_data.get("alergia_tipo_id") == allergy_type_id
        assert assigned_data.get("nin_id") == nin_id

        # Step 5: GET child's allergies to verify assignment
        get_allergies_url = f"{BASE_URL}/api/v1/children/{nin_id}/allergies"
        get_allergies_resp = requests.get(
            get_allergies_url, headers=headers, timeout=TIMEOUT
        )
        assert get_allergies_resp.status_code == 200
        allergies_for_child = get_allergies_resp.json()
        assert any(
            a.get("alergia_tipo_id") == allergy_type_id for a in allergies_for_child
        ), "Assigned allergy type not found in child's allergies"

    finally:
        # Cleanup: delete the created allergy type
        delete_allergy_url = f"{BASE_URL}/api/v1/alergias/tipos/{allergy_type_id}"
        del_resp = requests.delete(delete_allergy_url, headers=headers, timeout=TIMEOUT)
        # If delete endpoint is not supported or deletion failed, do not raise
        # Just acknowledge
        if del_resp.status_code not in (200, 204, 404):
            print(
                f"Warning: Failed to delete allergy type {allergy_type_id}, status {del_resp.status_code}"
            )

        # Cleanup: delete the child if created
        if "child_created" in locals() and child_created:
            delete_child_url = f"{BASE_URL}/api/v1/children/{nin_id}"
            del_child_resp = requests.delete(
                delete_child_url, headers=headers, timeout=TIMEOUT
            )
            if del_child_resp.status_code not in (200, 204, 404):
                print(
                    f"Warning: Failed to delete child {nin_id}, status {del_child_resp.status_code}"
                )


test_allergy_types_and_assignment()
