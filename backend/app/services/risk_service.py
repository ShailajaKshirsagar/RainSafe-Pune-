"""Rule-based rainfall concern indicator. Deterministic: no randomness, no ML."""
from app.core.config import LIMITATIONS, THRESHOLDS

MEASURES = [
    ("rain_1d_mm", "Daily rainfall"),
    ("rain_3d_mm", "3-day rainfall"),
    ("rain_7d_mm", "7-day rainfall"),
]
LABELS = {
    "low": "Low rainfall-related concern",
    "moderate": "Moderate rainfall-related concern",
    "high": "High rainfall-related concern",
    "unknown": "Not enough data to assess",
}


def assess(rain_1d, rain_3d, rain_7d, thresholds=None) -> dict:
    """Compare rainfall with thresholds. None means 'missing' (never 0)."""
    thresholds = thresholds or THRESHOLDS
    values = {"rain_1d_mm": rain_1d, "rain_3d_mm": rain_3d, "rain_7d_mm": rain_7d}
    missing = [k for k, v in values.items() if v is None]

    if len(missing) == len(values):
        category, triggered = "unknown", []
    else:
        category, triggered = "low", []
        for level in ("high", "moderate"):  # check the most serious first
            hits = []
            for key, name in MEASURES:
                limit = thresholds[level][key]
                v = values[key]
                if v is not None and v >= limit:
                    hits.append(f"{name} {v:.1f} mm is at or above the "
                                f"{level} threshold of {limit:g} mm")
            if hits:
                category, triggered = level, hits
                break

    return {
        "category": category,
        "label": LABELS[category],
        "measurements": values,
        "missing_measurements": missing,
        "triggered_rules": triggered,
        "thresholds_used": thresholds,
        "methodology": (
            "Rule-based rainfall indicator. Daily, 3-day and 7-day rainfall are "
            "compared with project-defined thresholds; the highest level triggered "
            "wins. It is not a validated flood-prediction model."
        ),
        "limitations": LIMITATIONS,
    }
