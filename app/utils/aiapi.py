from typing import Tuple, List

import openai
from app.config import settings

openai.api_key = settings.OPEN_AI_KEY


def generate_tags_and_summary(text: str) -> Tuple[List[str], str]:
    # Generate tags
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
    # Generate summary
    summary_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Create a summary of the following text:\n{text}",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = summary_response.choices[0].text.strip()

    return tags, summary
