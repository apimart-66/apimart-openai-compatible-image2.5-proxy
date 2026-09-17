import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  baseURL: process.env.OPENAI_BASE_URL ?? "https://api.apimart.ai/v1",
});

const response = await client.chat.completions.create({
  model: process.env.OPENAI_MODEL ?? "gpt-5-mini",
  messages: [{ role: "user", content: "Reply with exactly: migration-ok" }],
  stream: false,
});

console.log(response.choices[0].message.content);
