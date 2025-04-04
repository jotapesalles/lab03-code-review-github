# Coleta de Dados de Repositórios e Pull Requests do GitHub

Este projeto contém dois scripts em Python para coletar dados de repositórios populares no GitHub e seus respectivos Pull Requests (PRs). Os dados coletados são salvos em arquivos CSV para posterior análise.

## Índice

- [Descrição](#descrição)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Execução dos Scripts](#execução-dos-scripts)
  - [1. Coleta de Repositórios Populares](#1-coleta-de-repositórios-populares)
  - [2. Coleta de Pull Requests](#2-coleta-de-pull-requests)
- [Estrutura dos Arquivos CSV](#estrutura-dos-arquivos-csv)
- [Observações Importantes](#observações-importantes)
- [Licença](#licença)

## Descrição

O projeto é composto por dois scripts principais:

1. `collect_repositories.py`: Coleta uma lista de repositórios populares no GitHub com base em critérios específicos (por exemplo, número de estrelas) e salva as informações em um arquivo CSV.

2. `collect_pull_requests.py`: Para cada repositório listado no CSV gerado pelo primeiro script, coleta informações detalhadas sobre os Pull Requests e as salva em outro arquivo CSV.

## Pré-requisitos

Antes de executar os scripts, certifique-se de ter instalado:

- Python 3.x
- Bibliotecas Python:
  - `requests`
  - `python-dotenv`

Para instalar as bibliotecas necessárias, execute:

```bash
pip install requests python-dotenv
```

## Configuração

1. **Token de Acesso do GitHub**:

   Os scripts utilizam a API GraphQL do GitHub, que requer autenticação via token pessoal de acesso. Para gerar um token:

   - Acesse [Configurações de Tokens do GitHub](https://github.com/settings/tokens).
   - Clique em "Generate new token".
   - Selecione os escopos necessários (por exemplo, `repo` para acesso a repositórios privados, se necessário).
   - Gere o token e copie-o.

   Crie um arquivo `.env` no diretório do projeto com o seguinte conteúdo:

   ```env
   GITHUB_TOKEN=seu_token_aqui
   ```

   Substitua `seu_token_aqui` pelo token gerado.

2. **Configuração de Variáveis**:

   No início de cada script, há variáveis que podem ser ajustadas conforme a necessidade, como o número máximo de repositórios a serem coletados ou o número máximo de páginas de PRs a serem buscadas. Revise e ajuste essas variáveis conforme necessário.

## Execução dos Scripts

### 1. Coleta de Repositórios Populares

Execute o script `collect_repositories.py` para coletar informações dos repositórios populares:

```bash
python collect_repositories.py
```

Este script:

- Busca repositórios populares no GitHub com base nos critérios definidos.
- Salva as informações dos repositórios no arquivo `repositories.csv`.
- Implementa mecanismos de retry e salvamento incremental para lidar com possíveis falhas de conexão ou interrupções.

### 2. Coleta de Pull Requests

Após coletar os repositórios, execute o script `collect_pull_requests.py` para coletar informações dos Pull Requests:

```bash
python collect_pull_requests.py
```

Este script:

- Lê o arquivo `repositories.csv` para obter a lista de repositórios.
- Para cada repositório, coleta informações detalhadas sobre os Pull Requests.
- Salva os dados coletados no arquivo `pull_requests.csv`.
- Mantém um registro dos repositórios já processados no arquivo `processed_repositories.txt` para evitar duplicações em execuções subsequentes.
- Implementa mecanismos de retry e salvamento incremental para lidar com possíveis falhas de conexão ou interrupções.

## Estrutura dos Arquivos CSV

- **`repositories.csv`**:

  | owner       | name            | stars | url                          |
  |-------------|-----------------|-------|------------------------------|
  | facebook    | react           | 180000| https://github.com/facebook/react |
  | tensorflow  | tensorflow      | 160000| https://github.com/tensorflow/tensorflow |
  | ...         | ...             | ...   | ...                          |

- **`pull_requests.csv`**:

  | repo                | title             | created_at          | closed_at           | status  | duration_hours | additions | deletions | changed_files | body_length | review_count | comment_count |
  |---------------------|-------------------|---------------------|---------------------|---------|----------------|-----------|-----------|---------------|-------------|--------------|---------------|
  | facebook/react      | Fix bug in X      | 2025-04-01T12:00:00Z| 2025-04-02T15:00:00Z| merged  | 27.0           | 10        | 2         | 3             | 150         | 2            | 5             |
  | tensorflow/tensorflow| Add feature Y    | 2025-03-28T08:30:00Z| 2025-03-30T10:45:00Z| closed  | 50.25          | 25        | 5         | 7             | 300         | 3            | 8             |
  | ...                 | ...               | ...                 | ...                 | ...     | ...            | ...       | ...       | ...           | ...         | ...          | ...           |

## Observações Importantes

- **Limites da API**: O GitHub impõe limites de taxa para o uso de sua API. Se você exceder esses limites, poderá ser temporariamente bloqueado. Os scripts implementam pausas (`sleep`) para mitigar esse risco, mas é importante estar ciente dos limites ao executar coletas extensivas.

- **Interrupções e Retomada**: Ambos os scripts foram projetados para lidar com interrupções. Eles salvam progressos intermediários e podem ser retomados do ponto em que pararam, evitando a necessidade de recomeçar do zero.

- **Ambiente Virtual**: Recomenda-se o uso de um ambiente virtual Python para gerenciar as dependências e evitar conflitos com outras instalações. Para criar e ativar um ambiente virtual:

  ```bash
  # No Linux/macOS
  python3 -m venv venv
  source venv/bin/activate

  # No Windows
  python -m venv venv
  venv\Scripts\activate
  ```

  Após ativar o ambiente virtual, instale as dependências conforme mencionado na seção de Pré-requisitos.

## Licença

Este projeto é licenciado sob a [MIT License](LICENSE). 