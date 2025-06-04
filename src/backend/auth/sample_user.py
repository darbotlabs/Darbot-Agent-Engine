# Thought into existence by Darbot
import os
import logging

# Get environment variables for auth details or use defaults
def get_env_or_default(key, default_value):
    value = os.environ.get(key)
    if not value:
        logging.debug(f"Environment variable {key} not found, using default value")
        return default_value
    return value

# Base mock user dictionary with standard headers
sample_user = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en",
    "Client-Ip": get_env_or_default("MOCK_CLIENT_IP", "127.0.0.1"),
    "Content-Length": "192",
    "Content-Type": "application/json",
    "Cookie": get_env_or_default("MOCK_AUTH_SESSION", "AppServiceAuthSession=mock-session-token"),    "Disguised-Host": get_env_or_default("HOST_NAME", "darbot-studio-cat.azurewebsites.net"),
    "Host": get_env_or_default("HOST_NAME", "darbot-studio-cat.azurewebsites.net"),
    "Max-Forwards": "10",
    "Origin": get_env_or_default("ORIGIN_URL", "http://localhost:3000"),
    "Referer": get_env_or_default("REFERER_URL", "http://localhost:3000/"),
    "Sec-Ch-Ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Traceparent": get_env_or_default("TRACEPARENT", "00-0000000000000000000000000000000-0000000000000000-00"),
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "Was-Default-Hostname": get_env_or_default("HOST_NAME", "localhost"),    "X-Appservice-Proto": get_env_or_default("APP_SERVICE_PROTO", "https"),
    "X-Arr-Log-Id": get_env_or_default("ARR_LOG_ID", "00000000-0000-0000-0000-000000000000"),
    "X-Arr-Ssl": get_env_or_default("ARR_SSL", ""),
    "X-Client-Ip": get_env_or_default("CLIENT_IP", "127.0.0.1"),
    "X-Client-Port": get_env_or_default("CLIENT_PORT", "0"),
    "X-Forwarded-For": get_env_or_default("FORWARDED_FOR", "127.0.0.1"),
    "X-Forwarded-Proto": get_env_or_default("FORWARDED_PROTO", "https"),
    "X-Forwarded-Tlsversion": get_env_or_default("FORWARDED_TLS", "1.2"),    "X-Ms-Client-Principal": get_env_or_default("CLIENT_PRINCIPAL", "azure-ad-user"),
    "X-Ms-Client-Principal-Id": get_env_or_default("CLIENT_PRINCIPAL_ID", "ebb01e50-f389-4f45-84a3-8d588f0b5bab"),
    "X-Ms-Client-Principal-Idp": get_env_or_default("CLIENT_PRINCIPAL_IDP", "aad"),
    "X-Ms-Client-Principal-Name": get_env_or_default("CLIENT_PRINCIPAL_NAME", "dayour@microsoft.com"),
    "X-Ms-Token-Aad-Id-Token": get_env_or_default("AAD_ID_TOKEN", "azure-ad-token"),
    "X-Original-Url": get_env_or_default("ORIGINAL_URL", "/api"),
    "X-Site-Deployment-Id": get_env_or_default("SITE_DEPLOYMENT_ID", "local"),
    "X-Waws-Unencoded-Url": get_env_or_default("UNENCODED_URL", "/api"),
}
