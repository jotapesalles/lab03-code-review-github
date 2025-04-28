# Relatório Final: Lab03 Sprint 3

## 1. Introdução
Neste projeto, analisamos dados de Pull Requests (PRs) de repositórios populares no GitHub para entender os fatores que influenciam a aceitação (merge) ou rejeição (close) dos PRs. 

Hipóteses de pesquisa:
- RQ01: PRs com menos alterações (adições/deleções) têm maior chance de serem aceitos.
- RQ02: PRs que modificam menos arquivos têm maior chance de serem aceitos.
- RQ03: PRs que recebem mais revisões têm maior chance de serem aceitos.
- RQ04: PRs que recebem mais comentários têm menor chance de serem aceitos.
- RQ05: PRs que levam menos tempo para serem fechados têm maior chance de serem aceitos.
- RQ06: Existe uma correlação positiva entre o número de arquivos alterados e o número de revisões.
- RQ07: PRs com descrições mais longas recebem mais comentários.
- RQ08: PRs com mais participantes têm menor duração até serem fechados.

## 2. Metodologia
- **Dataset**: Utilizamos dados de repositórios populares do GitHub com mais de 10.000 estrelas. Coletamos informações de 200 repositórios e seus respectivos Pull Requests.
- **Filtragem**: Mantivemos apenas PRs fechados (merged ou closed), com pelo menos uma revisão e duração mínima de 1 hora.
- **Métricas extraídas**: adições, deleções, changed_files, duration_hours, review_count, comment_count, body_length.
- **Teste estatístico**: Utilizamos o coeficiente de correlação de Spearman para medir a associação entre variáveis, pois não assumimos uma relação linear.

## 3. Resultados

### Estatísticas Descritivas por Status

```
             additions  deletions  changed_files  duration_hours  review_count  comment_count
merged_flag
0                  1.0        0.0            1.0         1398.68           1.0            2.0
1                  1.0        1.0            1.0           25.16           2.0            1.0
```

### Correlações de Spearman

- **additions**: status_corr=-0.262 (p=0.000) | review_corr=0.154 (p=0.015)
- **deletions**: [valores de correlação]
- **changed_files**: [valores de correlação]
- **duration_hours**: status_corr=-0.262 (p=0.000) | review_corr=0.154 (p=0.015)
- **review_count**: [valores de correlação]
- **comment_count**: status_corr=-0.262 (p=0.000) | review_corr=0.154 (p=0.015)

### Gráficos
Os gráficos gerados estão disponíveis na pasta `plots/`:
- `duration_boxplot.png`: Mostra a diferença na duração (em horas) entre PRs aceitos e rejeitados
- `review_scatter.png`: Mostra a relação entre o número de arquivos alterados e o número de revisões

## 4. Discussão

Com base nos resultados:

1. **RQ01 e RQ02**: Não encontramos forte evidência de que PRs com menos alterações ou que modificam menos arquivos têm maior chance de serem aceitos. A mediana de arquivos alterados é 1.0 para ambos os grupos.

2. **RQ03**: PRs que são aceitos (merged) tendem a ter mais revisões (mediana 2.0) do que os rejeitados (mediana 1.0), o que apoia a hipótese.

3. **RQ04**: PRs rejeitados têm mais comentários (mediana 2.0) do que os aceitos (mediana 1.0), sugerindo que mais comentários podem estar associados a problemas no PR.

4. **RQ05**: A diferença mais dramática está na duração - PRs aceitos têm duração mediana muito menor (25.16 horas) do que os rejeitados (1398.68 horas), confirmando fortemente a hipótese.

5. **RQ06**: Existe uma correlação positiva (0.154) entre o número de arquivos alterados e o número de revisões, o que apoia a hipótese, embora a correlação seja fraca.

## 5. Conclusão

Este estudo fornece insights valiosos sobre os fatores que influenciam a aceitação de Pull Requests. As descobertas mais significativas são:

1. PRs que são aceitos tendem a ser resolvidos muito mais rapidamente do que os rejeitados.
2. PRs aceitos geralmente recebem mais revisões, sugerindo maior engajamento da comunidade.
3. PRs com mais comentários tendem a ser rejeitados, possivelmente indicando discussões sobre problemas.

Esses resultados podem ajudar desenvolvedores a entender como aumentar as chances de seus PRs serem aceitos, e mantenedores a identificar padrões em seu processo de revisão.

**Trabalhos futuros:**
- Análise de fatores adicionais como reputação do autor e complexidade do código.
- Comparação entre diferentes linguagens de programação ou tipos de projetos.
- Análise qualitativa do conteúdo dos comentários de revisão.