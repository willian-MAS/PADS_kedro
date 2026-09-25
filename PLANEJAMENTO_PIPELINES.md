# Planejamento das pipelines

## O notebook

O notebook trata os zeros de Glucose, BloodPressure, SkinThickness, Insulin e
BMI como faltantes e preenche com a mediana, trunca outliers (quantis
0.05/0.95 com 1.5 x IQR), cria 8 variaveis novas (faixas de idade, IMC e
glicose, combinacoes idade x IMC e idade x glicose, score de insulina e os
produtos glicose x insulina e glicose x gravidez), faz encoding, aplica
RobustScaler e compara 9 modelos com GridSearchCV.

O principal problema para producao é que mediana, limites de outlier,
encoders e scaler são calculados com a base inteira antes do
`train_test_split`, ou seja, com vazamento de informacao do teste. Alem disso
nada disso fica salvo para ser aplicado em um registro novo.

## Desenho

```
data_engineering:
  raw -> clean_data -> add_split_column
      -> fit_imputers / impute_missing_values
      -> fit_outlier_thresholds / clip_outliers
      -> add_engineered_features
      -> fit_encoders / encode_categorical_features
      -> fit_scalers / scale_numerical_features -> master_table

modelling:
  master_table -> train_baseline_model -> evaluate_baseline_model
  master_table -> optimize_hyperparameters -> evaluate_optimized_model

refit:
  mesmas funcoes de fit da data_engineering, com todos os splits
  + refit_model -> production_model

inference:
  dados novos -> clean -> impute -> clip -> features -> encode -> scale -> predict
  (usando os artefatos production_*)
```

## Decisoes

- Cada `fit_*` recebe `split_to_fit`: `[train]` na modelagem e
  `[train, test, validate]` no refit. A mesma funcao serve aos dois casos.
- Splits: train para ajuste, test para comparar os modelos, validate como
  holdout final. Baseline e RandomForest treinam no mesmo split.
- Imputacao e limites de outlier viram artefatos salvos em `06_models`, para
  a inferencia aplicar exatamente o mesmo tratamento.
- O modelo e escolhido pelo `class_path` no YAML.
- Label encoding nas categoricas derivadas (o modelo final e de arvores) e
  valor -1 para categorias que nao apareceram no treino.
- `class_weight: balanced` no grid porque a base tem 65% de negativos.
- Na celula do notebook que cria `NEW_AGE_BMI_NOM`, as duas ultimas condicoes
  usam `BMI > 18.5` e sobrescrevem as anteriores. Aqui a combinacao e feita
  concatenando as faixas ja calculadas.

## Artefatos de producao

`production_imputers`, `production_outlier_thresholds`, `production_encoders`,
`production_scalers` e `production_model`, todos em `data/06_models/`.
