import os

ORG = "{{cookiecutter.github_organization}}"
REPO = "{{cookiecutter.github_repository}}"
LLM_FRAMEWORK = "{{cookiecutter.llm_framework}}"

BOTS = [
    "GPUtester",
    "dependabot[bot]",
    "github-actions[bot]",
]

try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
except KeyError:
    print("env var OPENAI_API_KEY not found")
    OPENAI_API_KEY = ""
try:
    GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
except KeyError:
    print("env var GITHUB_API_TOKEN not found")
    GITHUB_API_TOKEN = ""


# Helper functions
def chat_response(content):
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": content}],
    )
    return response.choices[0].message.content


def num_tokens_from_string(
    string: str,
    encoding_name: str = "cl100k_base",
) -> int:
    """Returns the number of tokens in a text string."""
    import tiktoken

    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def agent_response(agent, content):
    return agent.invoke(content)["output"]


def scrape_gh(org: str = ORG, repo: str = REPO) -> None:
    """Puts data into 4 folders: open_issues, closed_issues, open_prs, closed_prs"""
    import requests
    import json

    from tqdm.auto import tqdm
    open_issues_folder = f"{repo}_open_issues"
    closed_issues_folder = f"{repo}_closed_issues"
