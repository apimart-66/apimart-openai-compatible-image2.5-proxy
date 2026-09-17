import os

from openai import OpenAI


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.getenv("OPENAI_BASE_URL", "https://api.apimart.ai/v1"))
stream = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
    messages=[{"role": "user", "content": "Count from one to three."}],
    stream=True,
)
for event in stream:
    delta = event.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
