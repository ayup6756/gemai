import os
from google import genai
from google.genai import types

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

contents = []

while True:
    user_input = input("> ")
    contents.append(
        types.UserContent(parts=[
            types.Part.from_text(text=user_input)
        ])
    )

    resp = client.models.generate_content(
        model="gemini-2.0-flash", contents=contents
    )

    print(resp.candidates)
