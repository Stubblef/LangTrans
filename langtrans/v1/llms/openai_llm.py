from openai import OpenAI

def chat(prompt):
    client = OpenAI(api_key="sk-92425ed67bf24c5cb836804edddb2062", base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        )
    return response.choices[0].message.content