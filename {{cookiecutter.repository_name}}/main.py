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

            if "issues" in content_types:
                issues_folder = f"{repo}_{state}_issues"
                os.makedirs(issues_folder, exist_ok=True)
                issues = []
                for issue_or_pr in page_issues_or_prs:
                    if "pull_request" not in issue_or_pr:
                        issues.append(issue_or_pr)
                for issue in tqdm(issues, "fetching issues"):
                    issue_number = issue["number"]
                    issue_detail_url = f'{url.split("?")[0]}/{issue_number}'
                    padded_issue_number = f"{issue_number:06d}"
                    issue_filename = (
                        f"{issues_folder}/issue_detail_{padded_issue_number}.json"
                    )
                    if os.path.exists(issue_filename):
                        continue
                    else:
                        issue_detail_response = requests.get(
                            issue_detail_url, headers=headers
                        )
                        if not status_code_checks(issue_detail_response.status_code):
                            break
                        issue_detail_response_json = issue_detail_response.json()
                        if not json_content_check(issue_detail_response_json):
                            break
                        with open(issue_filename, "w") as f:
                            json.dump(issue_detail_response_json, f, indent=4)

            # if "prs" in content_types:
            # prs_folder = f"{repo}_{state}_prs"
            # os.makedirs(prs_folder, exist_ok=True)
            # prs = []
            #     for issue_or_pr in page_issues_or_prs:
            #         if "pull_request" in issue_or_pr:
            #             prs.append(issue_or_pr)
