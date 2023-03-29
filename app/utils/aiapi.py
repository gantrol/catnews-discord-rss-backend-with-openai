from typing import Tuple, List

import openai
from app.config import settings

openai.api_key = settings.OPEN_AI_KEY


def generate_tags_and_summary(text: str) -> Tuple[List[str], str]:
    tags = generate_tags(text)
    summary = generate_summary(text)

    return tags, summary


def generate_summary(text):
    summary_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Create a summary of the following text:\n{text}",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = summary_response.choices[0].text.strip()
    return summary


def generate_tags(text):
    sep = ","
    tags_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Generate 3 tags for the following text, split with {sep}:\n{text}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    tags = [tag.strip() for tag in tags_response.choices[0].text.split(sep)]
    return tags
