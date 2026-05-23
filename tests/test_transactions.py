
from fastapi.testclient import TestClient
from app.main import main_app
from tests.test_auth import random_user
import uuid
import random


client = TestClient(main_app)



def get_token():

    user = random_user()

    r1 = client.post('/auth/register', json=user)
    assert r1.status_code == 200
    r2 = client.post('/auth/token', data={'username': user['username'], 'password': user['password']})
    assert r2.status_code == 200
    token = r2.json()['access_token']

    return token



def random_transaction():

    uid = uuid.uuid4().hex[:8]

    amount = random.randint(1, 100)


    types = ['income', 'expense']

    transaction = {'title': f'transaction_{uid}', 'amount': amount, 'type': random.choice(types), 'category_title': None}

    return transaction

def auto_update_transaction(transaction: dict):
    uid = uuid.uuid4().hex[:8]
    types = ['income', 'expense']
    amount = random.randint(1, 100)
    new_title = transaction['title'] + f'{uid}'

    new_transaction = {'transaction_title': transaction['title'], 'title': new_title, 'amount': amount, 'type': random.choice(types), 'category_title': None}
    return new_transaction


def test_transactions():
    token = get_token()
    # add new transaction
    transaction = random_transaction()
    r1 = client.post('/transactions/add', json=transaction, headers={'Authorization': f'Bearer {token}'})
    assert r1.status_code == 200
    # update current transaction
    new_transaction = auto_update_transaction(transaction)
    r2 = client.post('/transactions/update', json=new_transaction, headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    # get all user transactions
    r3 = client.get('/transactions/all/', headers={'Authorization': f'Bearer {token}'})
    assert r3.status_code == 200
    # get users transaction stats
    r4 = client.get('/transactions/stats/', headers={'Authorization': f'Bearer {token}'})
    assert r4.status_code == 200

