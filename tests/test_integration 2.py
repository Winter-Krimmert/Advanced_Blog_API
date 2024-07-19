import pytest
from app import create_app, db
from models import User, Post, Comment
from faker import Faker

#to run integration tests
# pytest test_integration.py


fake = Faker()

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

def test_create_user(test_client):
    request_body = {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password()
    }

    response = test_client.post('/register', json=request_body)

    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'

def test_create_post(test_client):
    user = User(name=fake.name(), username=fake.user_name(), email=fake.email(), password=fake.password())
    db.session.add(user)
    db.session.commit()

    request_body = {
        "title": fake.sentence(),
        "content": fake.text()
    }

    response = test_client.post('/posts', json=request_body, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201

def test_update_post(test_client):
    user = User(name=fake.name(), username=fake.user_name(), email=fake.email(), password=fake.password())
    db.session.add(user)
    db.session.commit()

    post = Post(title=fake.sentence(), content=fake.text(), user_id=user.id)
    db.session.add(post)
    db.session.commit()

    update_data = {
        "title": "Updated Title"
    }

    response = test_client.put(f'/posts/{post.id}', json=update_data, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json['title'] == update_data['title']

def test_delete_post(test_client):
    user = User(name=fake.name(), username=fake.user_name(), email=fake.email(), password=fake.password())
    db.session.add(user)
    db.session.commit()

    post = Post(title=fake.sentence(), content=fake.text(), user_id=user.id)
    db.session.add(post)
    db.session.commit()

    response = test_client.delete(f'/posts/{post.id}', headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 204
    assert Post.query.get(post.id) is None
