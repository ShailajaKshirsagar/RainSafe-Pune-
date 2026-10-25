"""Safety advice per category. Kept separate so it is easy to edit.
These are general precautions, NOT official alerts."""

GENERAL = [
    "Follow official weather warnings (IMD) and Pune Municipal Corporation instructions.",
]
BY_CATEGORY = {
    "low": [
        "No special rainfall-related precautions indicated by this indicator.",
        "Still check official forecasts before travelling in the monsoon season.",
    ],
    "moderate": [
        "Drive carefully and allow extra travel time during heavy showers.",
        "Avoid waterlogged underpasses and low-lying roads.",
        "Keep away from overflowing drains and water channels.",
    ],
    "high": [
        "Do not walk or drive through visibly flooded roads.",
        "Keep away from overflowing drains, nullahs and river banks.",
        "Avoid non-essential travel during intense rainfall.",
        "Avoid contact with potentially contaminated floodwater.",
        "Keep phone charged and emergency contacts handy.",
    ],
    "unknown": ["Rainfall data is incomplete, so no assessment was made."],
}


def get_advisories(category: str) -> list:
    return BY_CATEGORY.get(category, BY_CATEGORY["unknown"]) + GENERAL
