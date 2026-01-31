import sys
import os
import io
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
import app.api as api_mod

client = TestClient(app)


def test_pdf_upload_success_and_exception(monkeypatch):
    # Create fake PDF reader with pages that return text
    class FakePage:
        def __init__(self, t):
            self._t = t
        def extract_text(self):
            return self._t

    class FakeReader:
        def __init__(self, data):
            self.pages = [FakePage('Hello PDF')]

    monkeypatch.setattr(api_mod, 'PyPDF2', api_mod.PyPDF2)
    monkeypatch.setattr(api_mod, 'PyPDF2', api_mod.PyPDF2)
    # Monkeypatch PdfReader to our fake
    monkeypatch.setattr(api_mod, 'PyPDF2', api_mod.PyPDF2)
    monkeypatch.setattr(api_mod.PyPDF2, 'PdfReader', lambda b: FakeReader(b))

    files = {'file': ('doc.pdf', b'%PDF-1.4 fake', 'application/pdf')}
    r = client.post('/api/upload', files=files)
    assert r.status_code == 200
    j = r.json()
    assert j['text'] == 'Hello PDF'

    # Now force PdfReader to raise to cover exception path
    def raise_reader(b):
        raise Exception('bad pdf')
    monkeypatch.setattr(api_mod.PyPDF2, 'PdfReader', raise_reader)
    r2 = client.post('/api/upload', files=files)
    assert r2.status_code == 200
    assert r2.json()['text'] == ''


def test_chat_askllm_raises_returns_500(monkeypatch):
    # Create a stored doc
    doc_id = 'test-doc-1'
    api_mod.UPLOAD_STORE[doc_id] = {'filename': 'f', 'text': 'abc'}

    async def raise_llm(prompt):
        raise RuntimeError('llm down')

    monkeypatch.setattr(api_mod, 'ask_llm', raise_llm)
    r = client.post('/api/chat', json={'doc_id': doc_id, 'question': 'q'})
    assert r.status_code == 500
    assert 'error' in r.json()


def test_health_endpoint_env(monkeypatch):
    # When OPENAI_API_KEY unset
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json().get('llm_configured') is False

    # When set
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    r2 = client.get('/api/health')
    assert r2.status_code == 200
    assert r2.json().get('llm_configured') is True


def test_llm_client_exception_path(monkeypatch):
    # Ensure ask_llm returns placeholder when OpenAI client fails
    import app.services.llm_client as llm_mod
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')

    class FakeOpenAI:
        def __init__(self, api_key=None, base_url=None):
            raise RuntimeError('init fail')

    monkeypatch.setattr(llm_mod, 'OpenAI', FakeOpenAI)

    import asyncio
    res = asyncio.get_event_loop().run_until_complete(llm_mod.ask_llm('hi'))
    assert isinstance(res, str)
    assert '[LLM' in res


def test_transcribe_success_and_exception(monkeypatch):
    import app.services.transcribe as trans_mod
    # Set key to simulate path
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')

    class FakeResp:
        def __init__(self, text):
            self.text = text

    # Monkeypatch OpenAI object with audio.transcriptions.create
    class FakeOpenAI:
        def __init__(self, api_key=None):
            self.audio = type('A', (), {'transcriptions': type('T', (), {'create': staticmethod(lambda file, model: FakeResp('transcribed text'))})})()

    monkeypatch.setattr(trans_mod, 'OpenAI', FakeOpenAI)
    import asyncio
    res = asyncio.get_event_loop().run_until_complete(trans_mod.transcribe_audio(b'd', 'f.mp3'))
    assert isinstance(res, str)
    assert 'transcribed' in res

    # Now make OpenAI raise
    class BadOpenAI:
        def __init__(self, api_key=None):
            raise RuntimeError('boom')

    monkeypatch.setattr(trans_mod, 'OpenAI', BadOpenAI)
    res2 = asyncio.get_event_loop().run_until_complete(trans_mod.transcribe_audio(b'd', 'f.mp3'))
    assert isinstance(res2, str)
    assert res2.startswith('[')
