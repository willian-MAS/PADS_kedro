"""Pipeline de refit: artefatos de producao ajustados em todos os splits."""

from kedro.pipeline import Node, Pipeline

from diabetes.pipelines.data_engineering.nodes import (
    add_engineered_features,
    clip_outliers,
    fit_encoders,
    fit_imputers,
    fit_outlier_thresholds,
    fit_scalers,
    impute_missing_values,
)

from .nodes import refit_model


def create_pipeline(**kwargs) -> Pipeline:
    """Monta a pipeline de refit dos artefatos de producao."""
    return Pipeline(
        [
            Node(
                func=fit_imputers,
                inputs=[
                    "split_diabetes_data",
                    "params:columns",
                    "params:refit_imputers",
                ],
                outputs="production_imputers",
                name="refit_imputers",
            ),
            Node(
                func=impute_missing_values,
                inputs=["split_diabetes_data", "production_imputers"],
                outputs="refit_imputed_data",
                name="refit_impute_missing_values",
            ),
            Node(
                func=fit_outlier_thresholds,
                inputs=[
                    "refit_imputed_data",
                    "params:columns",
                    "params:refit_outliers",
                ],
                outputs="production_outlier_thresholds",
                name="refit_outlier_thresholds",
            ),
            Node(
                func=clip_outliers,
                inputs=["refit_imputed_data", "production_outlier_thresholds"],
                outputs="refit_clipped_data",
                name="refit_clip_outliers",
            ),
            Node(
                func=add_engineered_features,
                inputs=["refit_clipped_data", "params:feature_engineering"],
                outputs="refit_featured_data",
                name="refit_add_engineered_features",
            ),
            Node(
                func=fit_encoders,
                inputs=[
                    "refit_featured_data",
                    "params:columns",
                    "params:refit_encoders",
                ],
                outputs="production_encoders",
                name="refit_encoders",
            ),
            Node(
                func=fit_scalers,
                inputs=[
                    "refit_featured_data",
                    "params:columns",
                    "params:refit_scalers",
                ],
                outputs="production_scalers",
                name="refit_scalers",
            ),
            Node(
                func=refit_model,
                inputs=[
                    "master_table",
                    "params:columns",
                    "optimized_model",
                    "params:refit_model",
                ],
                outputs="production_model",
                name="refit_model",
            ),
        ]
    )
