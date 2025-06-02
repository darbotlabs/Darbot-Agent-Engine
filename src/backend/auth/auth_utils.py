import base64
import json
import logging


def get_authenticated_user_details(request_headers):
    user_object = {}

    # check the headers for the Principal-Id (the guid of the signed in user)
    if "x-ms-client-principal-id" not in request_headers:
        logging.info("No user principal found in headers")
        # if it's not, assume we're in development mode and return a default user
        from . import sample_user

        raw_user_object = sample_user.sample_user
    else:
        # if it is, get the user details from the EasyAuth headers
        raw_user_object = {k: v for k, v in request_headers.items()}

    normalized_headers = {k.lower(): v for k, v in raw_user_object.items()}
    user_object["user_principal_id"] = normalized_headers.get(
        "x-ms-client-principal-id"
    )
    user_object["user_name"] = normalized_headers.get("x-ms-client-principal-name")
    user_object["auth_provider"] = normalized_headers.get("x-ms-client-principal-idp")
    user_object["auth_token"] = normalized_headers.get("x-ms-token-aad-id-token")
    user_object["client_principal_b64"] = normalized_headers.get(
        "x-ms-client-principal"
    )
    user_object["aad_id_token"] = normalized_headers.get("x-ms-token-aad-id-token")
    # Extract user roles from claims if present
    user_object["roles"] = []
    if user_object["client_principal_b64"]:
        try:
            import base64, json

            decoded = base64.b64decode(user_object["client_principal_b64"])
            claims = json.loads(decoded)
            # Azure Static Web Apps puts roles in 'roles' or 'userRoles'
            user_object["roles"] = claims.get("roles") or claims.get("userRoles") or []
        except Exception as ex:  # nosec B110
            logging.warning("Failed to decode user roles from client principal: %s", ex)
    return user_object


# RBAC utility: check if user has a required role
def user_has_role(user_object, required_roles):
    """Return True if user has any of the required roles."""
    user_roles = user_object.get("roles") or []
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    return any(role in user_roles for role in required_roles)


def get_tenantid(client_principal_b64):
    logger = logging.getLogger(__name__)
    tenant_id = ""
    if client_principal_b64:
        try:
            # Decode the base64 header to get the JSON string
            decoded_bytes = base64.b64decode(client_principal_b64)
            decoded_string = decoded_bytes.decode("utf-8")
            # Convert the JSON string1into a Python dictionary
            user_info = json.loads(decoded_string)
            # Extract the tenant ID
            tenant_id = user_info.get("tid")  # 'tid' typically holds the tenant ID
        except Exception as ex:
            logger.exception(ex)
    return tenant_id
