"""Small HTTP client. All database operations go through FastAPI."""
import os
import requests
import streamlit as st

BASE_URL = os.getenv('HELPDESK_API_URL', 'http://127.0.0.1:8080').rstrip('/')

class APIError(Exception):
    pass

def request(method, path, payload=None, params=None, authenticated=True):
    headers = {}
    if authenticated:
        token = st.session_state.get('token')
        if not token:
            raise APIError('Please log in again.')
        headers['Authorization'] = f'Bearer {token}'
    try:
        response = requests.request(method, f'{BASE_URL}{path}', json=payload,
                                    params=params, headers=headers, timeout=15)
    except requests.RequestException as error:
        raise APIError('Cannot reach FastAPI. Is the backend running on port 8080?') from error
    if not response.ok:
        try:
            detail = response.json().get('detail', response.text)
        except ValueError:
            detail = response.text
        if isinstance(detail, list):
            detail = "; ".join(
            f"{item.get('loc', [])}: {item.get('msg', item)}"
            for item in detail
    )
        raise APIError(f'{response.status_code}: {detail}')
    return response.json() if response.content else None

def get(path, params=None):
    return request('GET', path, params=params)

def post(path, payload=None, authenticated=True, params=None):
    return request(
        'POST',
        path,
        payload=payload,
        params=params,
        authenticated=authenticated
    )
def patch(path, payload):
    return request('PATCH', path, payload=payload)
