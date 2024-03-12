from fastapi import FastAPI, Form
from fastapi.responses import Response


app = FastAPI()

users = {
    "kirill@user.com": {
        'name': 'Кирилл',
        'password': '1234',
        'balance': 100_000,
    }
}


@app.get('/')
def index_page():
    with open('templates/login.html', 'r', encoding="utf-8") as f:
        login_page = f.read()
    return Response(login_page, media_type="text/html")


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or user['password'] != password:
        return Response('Не пиши сюда!', media_type='text/html')
    return Response(f"Ваш логин {username}, ваш пароль {password}", media_type="text/html")
