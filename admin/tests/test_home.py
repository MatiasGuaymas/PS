from src.web import create_app

app = create_app()
app.testing = True
client = app.test_client()

def test_home():
    response = client.get('/')
    assert response.status_code == 200
    assert "¡Hola mundo!".encode("utf-8") in response.data