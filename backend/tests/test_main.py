import pytest
from fastapi.testclient import TestClient
import sys
import os

# Configure path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_root():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_upload_unsupported():
    files = {'file': ('test.txt', b'hello', 'text/plain')}
    r = client.post('/api/upload', files=files)
    assert r.status_code == 400

@pytest.mark.asyncio
async def test_summarize_endpoint():
    r = client.post('/api/summarize', data={'text': 'This is a test of summarization.'})
    assert r.status_code == 200
    assert 'summary' in r.json()
