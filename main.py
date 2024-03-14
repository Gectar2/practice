import base64
import hmac
import hashlib

from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = '251ab5630436796f0091262ff7680380'
PASSWORD_SALT = '161ab0000436123f0091262ff7480381'


def sing_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split('.')
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sing_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest().lower()
    stored_password_hash = users[username]['password'].lower()
    return password_hash == stored_password_hash


users = {
    "kirill@user.com": {
        'name': 'Кирилл',
        'password': '8cb3e6b88ba5c2d1898dd95b55b07d39fdc7a5de75d3ae6a8440291df3974bed',
        'balance': 100_000,
    }
}


@app.get('/')
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r', encoding="utf-8") as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key='username')
        return response
    try:
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key='username')
        return response
    return Response(f'Привет {users[valid_username]["name"]}', media_type="text/html")


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response('Не пиши сюда!', media_type='text/html')

    response = Response(f"Ваш логин {username}, ваш пароль {password}", media_type="text/html")
    username_signed = base64.b64encode(username.encode()).decode() + '.' + sing_data(username)
    response.set_cookie(key='username', value=username_signed)
    return response
