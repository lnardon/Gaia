import os
import re
import requests

GITHUB_API_URL = "https://api.github.com"


def get_repo_env_vars(repo, token):
    headers = {"Authorization": f"Bearer {token}"}
    env_vars_url = f"{GITHUB_API_URL}/repos/{repo}/actions/secrets"
    response = requests.get(env_vars_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error fetching environment variables: {response.text}")

    env_vars = [secret["name"] for secret in response.json()["secrets"]]
    return env_vars


def scan_for_env_vars(env_vars):
    env_var_pattern = re.compile(r'\b(?:' + '|'.join(env_vars) + r')\b')

    for root, _, files in os.walk("."):
        for file_name in files:
            if file_name.endswith(".yml") or file_name.endswith(".yaml"):
                continue

            file_path = os.path.join(root, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                file_content = file.read()

                for match in env_var_pattern.finditer(file_content):
                    print(f"Warning: Found environment variable {match.group(0)} in {file_path}")


if __name__ == "__main__":
    repo = os.environ["REPO_NAME"]
    token = os.environ["GITHUB_TOKEN"]

    env_vars = get_repo_env_vars(repo, token)
    scan_for_env_vars(env_vars)
