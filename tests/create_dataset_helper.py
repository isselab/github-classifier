import pandas as pd
import requests


def fetch_repositories(topic, max_repos=100):
    url = f'https://api.github.com/search/repositories?q={topic}&sort=stars&order=desc'
    repositories = []
    page = 1

    while len(repositories) < max_repos:
        response = requests.get(url, params={'page': page, 'per_page': 30})
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()
        repositories.extend(data.get('items', []))

        if 'items' not in data or len(data['items']) == 0:
            break

        page += 1

    return [repo['html_url'] for repo in repositories[:max_repos]]


def save_to_excel(urls, filename='repositories.xlsx'):
    df = pd.DataFrame(urls, columns=['Repository URL'])
    df.to_excel(filename, index=False)


def main():
    # Set your desired topic and maximum number of repositories here
    topic = "machine learning"  # Change this to your desired topic
    max_repos = 100  # Change this to your desired maximum number of repositories

    print(f"Fetching repositories for topic: {topic}")
    urls = fetch_repositories(topic, max_repos)

    if urls:
        save_to_excel(urls)
        print(f"Saved {len(urls)} repository URLs to 'repositories.xlsx'")
    else:
        print("No repositories found.")


if __name__ == "__main__":
    main()
