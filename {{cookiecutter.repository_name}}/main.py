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
def status_code_checks(status_code: int) -> bool:
    if status_code == 200:
        return True
    elif status_code == 403 or status_code == 429:
        print("hit rate limit. breaking")
        return False
    else:
        print(f"status code: {status_code}. breaking")
        return False


def json_content_check(json_content) -> bool:
    if not json_content:
        print("no content found. breaking")
        return False
    else:
        return True


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


# Core functions
def scrape_gh(
    org: str = ORG,
    repo: str = REPO,
    states: list[str] = ["open", "closed"],
    content_types: list[str] = ["issues", "prs"],
    verbose: bool = False,
) -> None:
    """
    Puts data into 4 folders: open_issues, closed_issues, open_prs, closed_prs
    GitHub shares the same structure for issues and PRs
    Note: not tested for only open issues for example
    """
    import requests
    import json

    from tqdm.auto import tqdm

    GH_API_URL_PREFIX = f"https://api.github.com/repos/{org}/{repo}/"
    headers = {"Authorization": f"token {GITHUB_API_TOKEN}"}

    for state in states:
        page = 1
        while True:
            # the issues endpoint is misnomer and contains issues and prs.
            # This returns a high level overview of the issue or pr such as:
            # the user, the body, body reactions e.g. +1 and whether it's a pr or issue
            gh_api_url_suffix = f"issues?state={state}&per_page=100&page={page}"
            url = f"{GH_API_URL_PREFIX}{gh_api_url_suffix}"
            response = requests.get(url, headers=headers)
            if not status_code_checks(response.status_code):
                break
            # list of ~100 issues or prs from most recent to oldest
            page_issues_or_prs = response.json()
            if not json_content_check(page_issues_or_prs):
                break

            for content_type in content_types:
                folder = f"{repo}_{state}_{content_type}"
                os.makedirs(folder, exist_ok=True)
                if content_type == "issues":
                    endpoint = "issues"
                    page_issues_or_prs_filtered = [
                        issue
                        for issue in page_issues_or_prs
                        if "pull_request" not in issue
                    ]
                else:
                    endpoint = "pulls"
                    page_issues_or_prs_filtered = [
                        issue for issue in page_issues_or_prs if "pull_request" in issue
                    ]

                for issue_or_pr in tqdm(
                    page_issues_or_prs_filtered, f"fetching {content_type}"
                ):
                    number = issue_or_pr["number"]
                    padded_number = f"{number:06d}"
                    filename = (
                        f"{folder}/{content_type[:-1]}_detail_{padded_number}.json"
                    )
                    if os.path.exists(filename):
                        continue
                    else:
                        detail_url = f"{GH_API_URL_PREFIX}{endpoint}/{number}"
                        if verbose:
                            print(detail_url)
                        detail_response = requests.get(
                            detail_url, headers=headers, timeout=10
                        )
                        if not status_code_checks(detail_response.status_code):
                            break
                        detail_response_json = detail_response.json()
                        if not json_content_check(detail_response_json):
                            break
                        # There is also a timeline API that could be included.
                        # This contains information on cross posting issues or prs
                        with open(filename, "w") as f:
                            json.dump(detail_response_json, f, indent=4)
    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=str, default=False)
    args = parser.parse_args()
    scrape_gh(verbose=args.verbose)
