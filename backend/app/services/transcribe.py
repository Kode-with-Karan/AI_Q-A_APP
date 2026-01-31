import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _get_openai_key():
    return os.getenv('OPENAI_API_KEY')

async def transcribe_audio(data: bytes, filename: str) -> str:
    # Save to temp file then call OpenAI Whisper (sync HTTP wrapped in async)
    import asyncio
    loop = asyncio.get_running_loop()
    def _sync_transcribe():
        with tempfile.NamedTemporaryFile(delete=False, suffix=filename) as f:
            f.write(data)
            tmp_path = f.name
        try:
            key = _get_openai_key()
            # Use OpenAI's transcription API if a key is provided
            if key:
                try:
                    client = OpenAI(api_key=key)
                    with open(tmp_path, "rb") as audio_file:
                        # Use a stable transcription model name like 'whisper-1'
                        resp = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                    # Try object-style then dict-style access
                    return getattr(resp, 'text', None) or (resp.get('text') if isinstance(resp, dict) else None) or str(resp)
                except Exception:
                    # If transcription fails (e.g. invalid key), return placeholder
                    return "[transcription placeholder]"
            # Fallback: return placeholder
            return "[transcription placeholder]"
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    return await loop.run_in_executor(None, _sync_transcribe)
