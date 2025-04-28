# filter_prs.py

import pandas as pd

# 1. Carrega o CSV completo e faz parsing de datas
df = pd.read_csv('pull_requests.csv', parse_dates=['created_at', 'closed_at'])

# 2. Calcula duração em horas
df['duration_hours'] = (
    df['closed_at'] - df['created_at']
).dt.total_seconds() / 3600

# 3. Aplica filtros:
#    - status “merged” ou “closed”
#    - review_count > 0
#    - duração > 1 hora
mask = (
    df['status'].isin(['merged', 'closed']) &
    (df['review_count'] > 0) &
    (df['duration_hours'] > 1)
)
df_filtered = df[mask]

# 4. Salva o CSV filtrado
df_filtered.to_csv('pull_requests_filtered.csv', index=False)
print(f"PRs filtrados: {len(df_filtered)} de {len(df)}")
