import sys
import os
import json
import pytest

# Ensure app can be imported from repo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_and_health():
    r = client.get('/')
    assert r.status_code == 200
    assert r.json().get('ok') is True


def test_upload_unsupported():
    files = {'file': ('test.txt', b'hello', 'text/plain')}
    r = client.post('/api/upload', files=files)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_transcribe_placeholder_and_llm_not_configured():
    # Test transcribe_audio fallback when no API key
    from app.services.transcribe import transcribe_audio
    txt = await transcribe_audio(b'data', 'audio.mp3')
    assert isinstance(txt, str)
    assert len(txt) > 0

    # Test LLM client fallback when no key is present
    from app.services.llm_client import ask_llm
    res = await ask_llm("Hello")
    assert isinstance(res, str)
    assert len(res) > 0


def test_upload_audio_and_chat_happy_path(monkeypatch):
    # Monkeypatch transcribe_audio to return a known text
    async def fake_transcribe(data, filename):
        return "Document content: The secret number is 42."

    async def fake_ask(prompt):
        # ensure the prompt contains the document text and question
        assert "The secret number is 42" in prompt
        assert "secret number" in prompt
        return "The secret number is 42."

    import app.api as api_mod
    monkeypatch.setattr(api_mod, 'transcribe_audio', fake_transcribe)
    monkeypatch.setattr(api_mod, 'ask_llm', fake_ask)

    files = {'file': ('audio.mp3', b'fake-audio-bytes', 'audio/mpeg')}
    r = client.post('/api/upload', files=files)
    assert r.status_code == 200
    j = r.json()
    assert 'id' in j and 'text' in j
    doc_id = j['id']

    # Ask a question using the uploaded doc_id
    payload = {'doc_id': doc_id, 'question': 'what is the secret number?'}
    r2 = client.post('/api/chat', data=json.dumps(payload), headers={'Content-Type': 'application/json'})
    assert r2.status_code == 200
    j2 = r2.json()
    assert 'answer' in j2 and '42' in j2['answer']


def test_chat_without_doc_returns_400():
    r = client.post('/api/chat', json={'question': 'What is in the doc?'})
    assert r.status_code == 400


def test_summarize_endpoint():
    r = client.post('/api/summarize', data={'text': 'This is a test of summarization.'})
    assert r.status_code == 200
    assert 'summary' in r.json()
