import requests

timeout: int = 8


def handle_request(
    method, full_url: str, path: str, headers, response_type, payload="{}"
):
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
