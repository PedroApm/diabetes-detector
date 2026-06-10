import json
import pickle

# pyrefly: ignore [missing-import]
import functions_framework
import numpy as np
from tensorflow import keras

# ---------------------------------------------------------------------------
# Global model / scaler – loaded once per cold start
# ---------------------------------------------------------------------------
_model = None
_scaler = None


def _load_artifacts():
    """Lazy-load the Keras model and the scikit-learn scaler."""
    global _model, _scaler
    if _model is None:
        _model = keras.models.load_model("diabetes_model.h5")
    if _scaler is None:
        with open("scaler.pkl", "rb") as f:
            _scaler = pickle.load(f)


# ---------------------------------------------------------------------------
# CORS helpers
# ---------------------------------------------------------------------------
_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


# ---------------------------------------------------------------------------
# Cloud Function entry point
# ---------------------------------------------------------------------------
@functions_framework.http
def predict(request):
    """HTTP Cloud Function for diabetes prediction."""

    # ---- preflight ---------------------------------------------------
    if request.method == "OPTIONS":
        return ("", 204, _CORS_HEADERS)

    # ---- only POST is allowed ----------------------------------------
    if request.method != "POST":
        return (
            json.dumps({"error": "Method not allowed"}),
            405,
            {**_CORS_HEADERS, "Content-Type": "application/json"},
        )

    # ---- parse body --------------------------------------------------
    try:
        body = request.get_json(silent=True) or {}
    except Exception:
        body = {}

    fields = [
        "pregnancies",
        "glucose",
        "blood_pressure",
        "skin_thickness",
        "insulin",
        "bmi",
        "diabetes_pedigree",
        "age",
    ]

    missing = [f for f in fields if f not in body]
    if missing:
        return (
            json.dumps({"error": f"Missing fields: {', '.join(missing)}"}),
            400,
            {**_CORS_HEADERS, "Content-Type": "application/json"},
        )

    # ---- inference ---------------------------------------------------
    _load_artifacts()

    try:
        features = np.array([[float(body[f]) for f in fields]])
    except (ValueError, TypeError):
        return (
            json.dumps({"error": "All fields must be numeric values"}),
            400,
            {**_CORS_HEADERS, "Content-Type": "application/json"},
        )

    scaled = _scaler.transform(features)
    probability = float(_model.predict(scaled)[0][0])

    label = "Diabético" if probability >= 0.5 else "No diabético"

    result = {
        "label": label,
        "probability": round(probability * 100, 2),
    }

    return (
        json.dumps(result),
        200,
        {**_CORS_HEADERS, "Content-Type": "application/json"},
    )
