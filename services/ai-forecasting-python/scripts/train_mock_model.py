"""
Train a small Scikit-Learn model that learns priority -> speed (km/h).
Express -> 60, Standard -> 30. Outputs a .joblib file for model_loader.
"""
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

_project_root = Path(__file__).resolve().parent.parent


class PrioritySpeedPredictor:
    """Wrapper so loaded model has predict(priority: str) -> float for API compatibility."""

    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    def predict(self, priority: str) -> float:
        return float(self.pipeline.predict([[priority]])[0])


def main() -> None:
    # Synthetic training data: priority -> speed (km/h)
    X = [["Express"], ["Standard"]] * 10
    y = [60.0, 30.0] * 10
    X = np.array(X)
    y = np.array(y)

    preprocessor = ColumnTransformer(
        [("priority", OneHotEncoder(handle_unknown="ignore"), [0])],
        remainder="passthrough",
    )
    pipeline = Pipeline(
        [
            ("preprocess", preprocessor),
            ("regressor", Ridge(alpha=1.0)),
        ]
    )
    pipeline.fit(X, y)

    wrapper = PrioritySpeedPredictor(pipeline)
    model_dir = _project_root / "models"
    model_dir.mkdir(exist_ok=True)
    model_path = model_dir / "speed_model.joblib"
    joblib.dump(wrapper, model_path)
    print(f"Saved model to {model_path}")


if __name__ == "__main__":
    main()
