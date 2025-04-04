import csv
import requests
import os
from time import sleep
from datetime import datetime
from requests.exceptions import RequestException

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
API_URL = "https://api.github.com/graphql"
PROCESSED_FILE = "processed_repositories.txt"
OUTPUT_CSV = "pull_requests.csv"

def run_query(query, max_retries=5, retry_delay=3):
    attempt = 1
    while attempt <= max_retries:
        print(f"📡 Executando query GraphQL (tentativa {attempt}/{max_retries})...")
        try:
            response = requests.post(API_URL, json={'query': query}, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response.json()
            print(f"⚠️ Erro {response.status_code}: {response.text}")
            if response.status_code >= 500:
                print(f"⏳ Aguardando {retry_delay}s para nova tentativa...\n")
                sleep(retry_delay)
                attempt += 1
            else:
                raise Exception(f"❌ Erro fatal: {response.status_code} {response.text}")
        except RequestException as e:
            print(f"⚠️ Exceção de rede: {e}")
            print(f"⏳ Aguardando {retry_delay}s para nova tentativa...\n")
            sleep(retry_delay)
            attempt += 1
    raise Exception("❌ Falha após múltiplas tentativas.")

def build_query(owner, name, cursor=None):
    after = f', after: "{cursor}"' if cursor else ''
    return f"""
    {{
      repository(owner: "{owner}", name: "{name}") {{
        pullRequests(first: 50, states: [CLOSED, MERGED]{after}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
          pageInfo {{
            hasNextPage
            endCursor
          }}
          nodes {{
            title
            createdAt
            closedAt
            mergedAt
            bodyText
            additions
            deletions
            changedFiles
            reviews {{
              totalCount
            }}
            comments {{
              totalCount
            }}
          }}
        }}
      }}
    }}
    """

def collect_prs(owner, name, max_pages=3):
    prs = []
    cursor = None
    for _ in range(max_pages):
        query = build_query(owner, name, cursor)
        result = run_query(query)
        pr_data = result["data"]["repository"]["pullRequests"]
        cursor = pr_data["pageInfo"]["endCursor"]
        prs.extend(pr_data["nodes"])
        if not pr_data["pageInfo"]["hasNextPage"]:
            break
        sleep(1)
    return prs

def save_valid_pr(pr, repo_name):
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "repo", "title", "created_at", "closed_at", "status",
                "duration_hours", "additions", "deletions", "changed_files",
                "body_length", "review_count", "comment_count"
            ])

        created_at = pr["createdAt"]
        closed_at = pr["closedAt"] or pr["mergedAt"]
        duration = (
            datetime.fromisoformat(closed_at.replace("Z", "+00:00")) -
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        ).total_seconds() / 3600

        status = "merged" if pr["mergedAt"] else "closed"

        writer.writerow([
            repo_name,
            pr["title"],
            created_at,
            closed_at,
            status,
            round(duration, 2),
            pr["additions"],
            pr["deletions"],
            pr["changedFiles"],
            len(pr["bodyText"]),
            pr["reviews"]["totalCount"],
            pr["comments"]["totalCount"]
        ])

def load_processed_repos():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def mark_repo_as_processed(repo_name):
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(repo_name + "\n")

def save_prs_to_csv(repos_csv="repositories.csv", max_pages=3):
    processed = load_processed_repos()

    with open(repos_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        repositories = list(reader)

    for idx, repo in enumerate(repositories, start=1):
        full_name = f"{repo['owner']}/{repo['name']}"
        if full_name in processed:
            print(f"⏩ Já processado: {full_name}")
            continue

        print(f"[{idx}/{len(repositories)}] Buscando PRs de {full_name}...")
        try:
            prs = collect_prs(repo["owner"], repo["name"], max_pages=max_pages)
        except Exception as e:
            print(f"❌ Erro ao buscar PRs de {full_name}: {e}")
            continue  # Tenta o próximo repositório

        count_saved = 0
        for pr in prs:
            if not pr["closedAt"] and not pr["mergedAt"]:
                continue
            if pr["reviews"]["totalCount"] < 1:
                continue
            created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00"))
            closed = pr["closedAt"] or pr["mergedAt"]
            closed = datetime.fromisoformat(closed.replace("Z", "+00:00"))
            if (closed - created).total_seconds() / 3600 < 1:
                continue
            save_valid_pr(pr, full_name)
            count_saved += 1

        print(f"✅ {count_saved} PRs válidos salvos de {full_name}")
        mark_repo_as_processed(full_name)
        sleep(1)

# EXECUTA
save_prs_to_csv()
