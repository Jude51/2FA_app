import pytest
from app import app,db
@pytest.fixture
def client():
    app.config['TESTING']=True
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()
def test_register(client):
    response = client.post('/register', data={
    'username': 'testuser',
    'password': 'testpass'
        })
    assert response.status_code == 302
def test_register_duplicate(client):
    client.post('/register', data={'username':'Alex','password':'123'})
    response = client.post('/register', data={'username':'Alex','password':'56'})
    assert response.status_code == 200
def test_login(client):
    client.post('/register', data={'username':'Alex','password':'123'})
    response=client.post('/login',data={'username':'Alex','password':'123'})
    assert response.status_code==302
def test_login_wrong_password(client):
    client.post('/register',data={'username':'Alex','password':'123'})
    response=client.post('/login',data={'username':'Alex','password':'456'})
    assert response.status_code == 200
def test_login_nonexistent(client):
    client.post('/register',data={'usernaeme':'Alex','password':'123'})
    response=client.post('/login',data={'username':'rtt','password':'123'})
    assert response.status_code == 200
