# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# import asyncio

# load_dotenv()

# def _get_openai_key():
#     return os.getenv('OPENAI_API_KEY')

# async def ask_llm(prompt: str) -> str:
#     """Call OpenAI Chat Completions using the new openai-python client.
#     Reads OPENAI_API_KEY at call time so env changes are respected.
#     """
#     key = _get_openai_key()
#     if not key:
#         return "[LLM not configured: set OPENAI_API_KEY in .env or environment and restart]"

#     loop = asyncio.get_running_loop()

#     def _call():
#         client = OpenAI(api_key=key)
#         resp = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=512,
#         )
#         # resp.choices may be list of dict-like or objects depending on client
#         if hasattr(resp, 'choices') and resp.choices:
#             choice = resp.choices[0]
#             # Try object-style access then dict-like
#             try:
#                 return choice.message.content
#             except Exception:
#                 try:
#                     return choice.get('message', {}).get('content') or choice.get('text','')
#                 except Exception:
#                     return str(choice)
#         return str(resp)

#     return await loop.run_in_executor(None, _call)

# async def summarize_text(text: str) -> str:
#     prompt = f"Summarize the following text in 3 bullet points:\n\n{text}"
#     return await ask_llm(prompt)


import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio

load_dotenv()

def _get_openai_key():
    return os.getenv("OPENAI_API_KEY")

async def ask_llm(prompt: str) -> str:
    key = _get_openai_key()
    if not key:
        return "[LLM not configured]"

    loop = asyncio.get_running_loop()

    def _call():
        try:
            client = OpenAI(
                api_key=key,
                base_url="https://openrouter.ai/api/v1"
            )

            resp = client.chat.completions.create(
                model="arcee-ai/trinity-large-preview:free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "AI Document Q&A"
                }
            )

            return resp.choices[0].message.content
        except Exception:
            # If the API key is missing/invalid or any error occurs, return a safe placeholder
            return "[LLM not configured or authentication failed]"

    return await loop.run_in_executor(None, _call)


async def summarize_text(text: str) -> str:
    prompt = f"Summarize the following text in 3 bullet points:\n\n{text}"
    return await ask_llm(prompt)