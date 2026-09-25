# Predicao de Diabetes com Kedro

Exercicio de avaliacao de Deployment: Production-Ready Data Science (Insper).

**Grupo:** Willian Miranda e Nicole Cristine

Transformamos o notebook `diabetes-prediction.ipynb` em um projeto Kedro com
quatro pipelines, uma API em FastAPI e um container Docker. O planejamento das
pipelines esta em [`PLANEJAMENTO_PIPELINES.md`](./PLANEJAMENTO_PIPELINES.md).

## Como rodar

```bash
uv sync
uv run kedro run
uv run kedro viz run
```

## Pipelines

- **data_engineering** (11 nos): limpeza, split train/test/validate, imputacao
  pela mediana, tratamento de outliers, features derivadas, encoding e
  RobustScaler. Tudo que e ajustado usa so o split de treino.
- **modelling** (4 nos): baseline com LogisticRegression e RandomForest com
  GridSearchCV (cv=5, roc_auc).
- **refit** (8 nos): reajusta imputadores, limites de outlier, encoders,
  scalers e o modelo com todos os splits.
- **inference** (8 nos): aplica os artefatos de producao nos dados novos.

Dados em `data/01_raw/` (652 linhas para modelagem e 116 para inferencia).

## Resultados

| Modelo | Split | Accuracy | Recall | F1 | ROC AUC |
|---|---|---|---|---|---|
| LogisticRegression | validate | 0.824 | 0.710 | 0.733 | 0.888 |
| RandomForest | validate | 0.835 | 0.774 | 0.762 | 0.890 |

Melhores parametros: `n_estimators=200`, `max_depth=10`,
`min_samples_split=10`, `min_samples_leaf=1`, `class_weight=balanced`.

Nos 116 registros de inferencia (que tem o Outcome): accuracy 0.741,
recall 0.750, ROC AUC 0.822.

## API

```bash
uv run uvicorn diabetes.api:app --port 8000
```

Swagger em http://localhost:8000/docs.

| Rota | Descricao |
|---|---|
| `GET /health` | status e artefatos de producao |
| `GET /datasets` | lista os datasets do catalogo |
| `GET /datasets/{nome}` | retorna um dataset em JSON (`limit`, `offset`) |
| `POST /train` | roda data_engineering, modelling e refit em background |
| `GET /train/{run_id}` | status do treino |
| `POST /batch-inference` | roda a pipeline de inferencia no CSV do catalogo |
| `GET /batch-inference/{run_id}` | status da inferencia em lote |
| `POST /inference` | predicao para registros enviados no corpo |


## Docker

```bash
docker compose up --build
```

A API sobe em http://localhost:8000. 

## Testes

```bash
uv run pytest
uv run ruff check src tests
```
