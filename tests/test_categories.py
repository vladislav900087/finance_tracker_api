from fastapi.testclient import TestClient
from app.main import main_app
from tests.test_transactions import get_token
import uuid


client = TestClient(main_app)

def random_category():
    uid = uuid.uuid4().hex[:8]

    return {'category_title': f'category_{uid}'}

def test_categories():

    token = get_token()

    new_category = random_category()

    r1 = client.post('/categories/add/', json=new_category, headers={'Authorization': f'Bearer {token}'})

    assert r1.status_code == 200

    r2 = client.get('/categories/all/', headers={'Authorization': f'Bearer {token}'})

    assert r2.status_code == 200

    r3 = client.delete('/categories/delete/', params={'category_name': new_category['category_title']}, headers={'Authorization': f'Bearer {token}'})
    print(r3.status_code)
    print(r3.text)
    assert r2.status_code == 200
