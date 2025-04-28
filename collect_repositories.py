# collect_repositories.py

import os
import csv
import requests
from time import sleep
from dotenv import load_dotenv

# Carrega variáveis de ambiente de .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v4+json"
}
API_URL = "https://api.github.com/graphql"
CHECKPOINT_FILE = "cursor_checkpoint.txt"
OUTPUT_CSV = "repositories.csv"

def run_query(query, max_retries=5, retry_delay=3):
    """Executa a query GraphQL com retries."""
    for attempt in range(1, max_retries+1):
        print(f"📡 Execução GraphQL (tentativa {attempt}/{max_retries})...")
        resp = requests.post(API_URL, json={"query": query}, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        print(f"⚠️ Erro {resp.status_code}: {resp.text}")
        if resp.status_code >= 500:
            sleep(retry_delay)
        else:
            resp.raise_for_status()
    raise Exception("❌ Falha após múltiplas tentativas de GraphQL.")

def save_repo_to_csv(owner, name, stars, url):
    """Anexa uma linha ao repositories.csv (cria cabeçalho se preciso)."""
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["owner", "name", "stars", "url"])
        writer.writerow([owner, name, stars, url])

def save_cursor(cursor):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(cursor or "")

def load_cursor():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            c = f.read().strip()
            return c if c else None
    return None

def get_popular_repositories(max_repos=200):
    cursor = load_cursor()
    added = 0

    # Conta quantos já foram salvos
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
            current = len(list(csv.reader(f))) - 1
    else:
        current = 0

    print(f"📦 Já há {current} repositórios no CSV.")
    if current >= max_repos:
        print("✅ Limite atingido. Nada a fazer.")
        return

    while current + added < max_repos:
        after = f', after: "{cursor}"' if cursor else ""
        query = f'''
        {{
          search(query: "stars:>10000", type: REPOSITORY, first: 10{after}) {{
            pageInfo {{ hasNextPage endCursor }}
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{ login }}
                  stargazerCount
                  pullRequests(states: [CLOSED, MERGED]) {{ totalCount }}
                  url
                }}
              }}
            }}
          }}
        }}
        '''
        data = run_query(query)["data"]["search"]
        for edge in data["edges"]:
            node = edge["node"]
            owner = node["owner"]["login"]
            name = node["name"]
            stars = node["stargazerCount"]
            pr_count = node["pullRequests"]["totalCount"]
            url = node["url"]

            if pr_count >= 100:
                print(f"➕ Salvando: {owner}/{name} ({stars} ⭐, {pr_count} PRs)")
                save_repo_to_csv(owner, name, stars, url)
                added += 1
                if current + added >= max_repos:
                    break

        cursor = data["pageInfo"]["endCursor"]
        save_cursor(cursor)
        if not data["pageInfo"]["hasNextPage"]:
            print("🚧 Fim da paginação.")
            break
        sleep(1)

    print(f"✅ Total adicionados agora: {added}")

if __name__ == "__main__":
    get_popular_repositories(max_repos=200)
