from typing import Tuple, List

import openai

openai.api_key = "your_api_key"


def generate_tags_and_summary(text: str) -> Tuple[List[str], str]:
    # Generate tags
    sep = ","
    tags_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Generate 3 tags for the following text, split with {sep}:\n{text}",
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )
    tags = [tag.strip() for tag in tags_response.split(',')]
    # Generate summary
    summary_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Create a summary of the following text:\n{text}",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summary = summary_response.choices[0].text.strip()

    return tags, summary
