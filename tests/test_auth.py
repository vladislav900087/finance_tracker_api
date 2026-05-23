from app.main import main_app
from fastapi.testclient import TestClient
import uuid
import secrets
import string
import random

client = TestClient(main_app)

def generate_random_password(length=16):

    alphabet = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(secrets.choice(alphabet) for _ in range(length))

    return password


def random_user():

    uid = uuid.uuid4().hex[:8]
    password = generate_random_password()

    user = {'username': f'user_{uid}', 'password': password, 'email': f'{uid}@example.com', 'full_name': f'Test-name {uid}'}

    return user

def test_register_and_login():

    user = random_user()

    r1 = client.post('/auth/register', json=user)

    assert r1.status_code == 200

    r2 = client.post('/auth/token', data={'username': user['username'], 'password': user['password']})

    assert r2.status_code == 200
















