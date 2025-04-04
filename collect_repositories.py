import requests
import csv
import os
from time import sleep
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
API_URL = "https://api.github.com/graphql"
CHECKPOINT_FILE = "cursor_checkpoint.txt"
OUTPUT_CSV = "repositories.csv"
    
def run_query(query, max_retries=5, retry_delay=3):
    attempt = 1
    while attempt <= max_retries:
        print(f"📡 Executando query GraphQL (tentativa {attempt}/{max_retries})...")
        response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Erro na query ({response.status_code}): {response.text}")
            print(f"⏳ Esperando {retry_delay} segundos antes de tentar novamente...\n")
            sleep(retry_delay)
            attempt += 1
    raise Exception(f"❌ Falha após {max_retries} tentativas.")

def save_repo_to_csv(repo, filename):
    file_exists = os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["owner", "name", "stars", "url"])
        writer.writerow([repo["owner"], repo["name"], repo["stars"], repo["url"]])

def save_cursor(cursor):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        f.write(cursor or "")

def load_cursor():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            cursor = f.read().strip()
            return cursor if cursor else None
    return None

def get_popular_repositories(max_repos=200):
    repos = []
    cursor = load_cursor()
    total_fetched = 0
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, newline="", encoding="utf-8") as f:
            existing_repos = list(csv.reader(f))
            current_count = len(existing_repos) - 1  # Desconta o cabeçalho
    else:
        current_count = 0
        print(f"🗃️ Repositórios já salvos: {current_count}")
    if current_count >= max_repos:
        print(f"✅ Já existem {current_count} repositórios no CSV. Nada a fazer.")
        return []

    remaining = max_repos - current_count
    print(f"Faltam buscar {remaining} repositórios para completar {max_repos}.\n")
    
    print(f"Iniciando coleta de até {max_repos} repositórios com >10000 estrelas...\n")

    while len(repos) + current_count < max_repos:
        after = f', after: "{cursor}"' if cursor else ''
        print(f"🔄 Buscando página de repositórios (cursor: {cursor})")

        query = f"""
        {{
          search(query: "stars:>10000", type: REPOSITORY, first: 10{after}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{ login }}
                  stargazerCount
                  pullRequests(states: [CLOSED, MERGED]) {{
                    totalCount
                  }}
                  url
                }}
              }}
            }}
          }}
        }}
        """

        try:
            result = run_query(query)
        except Exception as e:
            print(f"❌ Erro ao executar a query: {e}")
            print("⚠️ Salvando progresso e encerrando.")
            break

        search_data = result['data']['search']
        for edge in search_data['edges']:
            node = edge['node']
            total_fetched += 1
            print(f"🔍 Verificando ⭐ > 100: {node['owner']['login']}/{node['name']} ({node['stargazerCount']} ⭐)")
            if node['pullRequests']['totalCount'] >= 100:
                print(f"✅ Adicionado: {node['owner']['login']}/{node['name']} - {node['pullRequests']['totalCount']} PRs")
                repo = {
                    'name': node['name'],
                    'owner': node['owner']['login'],
                    'stars': node['stargazerCount'],
                    'url': node['url']
                }
                repos.append(repo)
                save_repo_to_csv(repo, OUTPUT_CSV)
                if len(repos) >= max_repos:
                    break

        cursor = search_data['pageInfo']['endCursor']
        save_cursor(cursor)
        if not search_data['pageInfo']['hasNextPage']:
            print("🚧 Fim da paginação.")
            break
        sleep(1)

    print(f"\n📦 Total de repositórios adicionados nesta execução: {len(repos)}")
    return repos

# Execução principal
get_popular_repositories(max_repos=200)
