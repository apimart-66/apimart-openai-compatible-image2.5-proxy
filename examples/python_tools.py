import json
import os

from openai import OpenAI


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.getenv("OPENAI_BASE_URL", "https://api.apimart.ai/v1"))
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
    messages=[{"role": "user", "content": "What is the weather in Singapore? Use the tool."}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Return current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }],
)
for call in response.choices[0].message.tool_calls or []:
    print(call.id, call.function.name, json.loads(call.function.arguments))
