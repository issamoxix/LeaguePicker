import requests
from typing import Optional
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
timeout: int = 8


def handle_request(
    method,
    full_url: str,
    path: str,
    headers,
    response_type: Optional[str] = None,
    payload="{}",
):
    """
    Sends a request to the League Client API and returns the response.

    Args:
        :param method: HTTP method to use for the request (e.g, "GET", "POST").
        full_url (str): The base URL of the League Client API.
        path (str): The path of the specific API endpoint.
        headers: The headers to include in the request.
        response_type(str, optional): Expected response type ["json","text"].
        payload (str, optional): Payload for the request. Defaults to "{}".

    Returns:
        The response from the League Client API.

    Note:
        The `verify` parameter is set to `False` to bypass SSL verification
        Due to the nature of the League Client API.

    """
    response = requests.request(
        method,
        full_url + path,
        timeout=timeout,
        headers=headers,
        verify=False,
        data=payload,
    )
    match response_type:
        case "json":
            return response.json()
        case "text":
            return response.text
        case _:
            return response
