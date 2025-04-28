# analyze_data.py

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# 1. Carregamento e preparação
df = pd.read_csv(
    'pull_requests_filtered.csv',
    parse_dates=['created_at', 'closed_at']
)
df['duration_hours'] = (
    df['closed_at'] - df['created_at']
).dt.total_seconds() / 3600

# Codifica merged como 1 e closed como 0
df['merged_flag'] = (df['status'] == 'merged').astype(int)

# 2. Estatísticas descritivas
metrics = [
    'additions',
    'deletions',
    'changed_files',
    'duration_hours',
    'review_count',
    'comment_count',
    'participant_count'
]

print("\n--- Medianas por Status (0 = closed, 1 = merged) ---")
print(df.groupby('merged_flag')[metrics].median())

# 3. Correlações de Spearman
print("\n--- Correlações Spearman ---")
for m in metrics:
    corr_s, p_s = spearmanr(df[m], df['merged_flag'])
    corr_r, p_r = spearmanr(df[m], df['review_count'])
    print(
        f"{m:15s} | status_corr={corr_s:.3f} (p={p_s:.3f})"
        f" | review_corr={corr_r:.3f} (p={p_r:.3f})"
    )

# 4. Visualizações

# Boxplot de duração por status
plt.figure()
plt.boxplot([
    df[df['merged_flag'] == 1]['duration_hours'],
    df[df['merged_flag'] == 0]['duration_hours']
])
plt.xticks([1, 2], ['Merged', 'Closed'])
plt.ylabel('Horas')
plt.title('Duração por Status')
plt.savefig('plots/duration_boxplot.png')
plt.close()

# Scatter: changed_files vs review_count
plt.figure()
plt.scatter(df['changed_files'], df['review_count'])
plt.xlabel('Arquivos Alterados')
plt.ylabel('Número de Reviews')
plt.title('Changed Files vs Review Count')
plt.savefig('plots/review_scatter.png')
plt.close()
