import requests

from private import github_project


def check_if_user_has_starred_github_project(github_username: str, github_project: str) -> bool:
    stars_url = f"https://github.com/{github_username}?tab=stars"
    print(stars_url)

    try:
        response = requests.get(stars_url)
        response.raise_for_status()
        p = response.text.find(github_project)
        return p > 0

    except requests.exceptions.RequestException as e:
        print(f"Error occurred during web scraping: {e}")
        return False


if __name__ == '__main__':
    username = "daishuge"
    has_starred = check_if_user_has_starred_github_project(username, github_project)
    if has_starred:
        print(f"{username} has starred the project: {github_project}")
    else:
        print(f"{username} has not starred the project: {github_project}")