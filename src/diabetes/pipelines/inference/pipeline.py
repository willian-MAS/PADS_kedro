"""Pipeline de inferencia, usando os artefatos de producao."""

from kedro.pipeline import Node, Pipeline

from diabetes.pipelines.data_engineering.nodes import (
    add_engineered_features,
    clean_data,
    clip_outliers,
    impute_missing_values,
    transform_encoders,
    transform_scalers,
)

from .nodes import predict, to_dataframe


def create_pipeline(**kwargs) -> Pipeline:
    """Monta a pipeline de inferencia (batch em CSV e online via API)."""
    return Pipeline(
        [
            Node(
                func=to_dataframe,
                inputs="raw_inference_data",
                outputs="raw_inference_dataframe",
                name="to_dataframe",
            ),
            Node(
                func=clean_data,
                inputs=["raw_inference_dataframe", "params:columns"],
                outputs="cleaned_inference_data",
                name="clean_inference_data",
            ),
            Node(
                func=impute_missing_values,
                inputs=["cleaned_inference_data", "production_imputers"],
                outputs="imputed_inference_data",
                name="impute_inference_data",
            ),
            Node(
                func=clip_outliers,
                inputs=["imputed_inference_data", "production_outlier_thresholds"],
                outputs="clipped_inference_data",
                name="clip_inference_data",
            ),
            Node(
                func=add_engineered_features,
                inputs=["clipped_inference_data", "params:feature_engineering"],
                outputs="featured_inference_data",
                name="engineer_inference_features",
            ),
            Node(
                func=transform_encoders,
                inputs=["featured_inference_data", "production_encoders"],
                outputs="encoded_inference_data",
                name="encode_inference_data",
            ),
            Node(
                func=transform_scalers,
                inputs=["encoded_inference_data", "production_scalers"],
                outputs="scaled_inference_data",
                name="scale_inference_data",
            ),
            Node(
                func=predict,
                inputs=["production_model", "scaled_inference_data"],
                outputs="inference_predictions",
                name="predict",
            ),
        ]
    )
