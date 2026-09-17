import os

from openai import OpenAI


client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.apimart.ai/v1"),
)

response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
    messages=[{"role": "user", "content": "Reply with exactly: migration-ok"}],
    stream=False,
)
print(response.choices[0].message.content)
