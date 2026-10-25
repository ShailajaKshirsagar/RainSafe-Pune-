"""Representative Pune locations. Coordinates are APPROXIMATE points chosen
from general knowledge for map demonstration; verify on OpenStreetMap.
They do NOT represent flood-prone areas or measured data."""

AREAS = [
    {"id": "shivajinagar", "name": "Shivajinagar", "latitude": 18.5308, "longitude": 73.8475},
    {"id": "pune-station", "name": "Pune Railway Station", "latitude": 18.5289, "longitude": 73.8744},
    {"id": "kothrud", "name": "Kothrud", "latitude": 18.5074, "longitude": 73.8077},
    {"id": "hadapsar", "name": "Hadapsar", "latitude": 18.5089, "longitude": 73.9259},
    {"id": "katraj", "name": "Katraj", "latitude": 18.4575, "longitude": 73.8677},
    {"id": "baner", "name": "Baner", "latitude": 18.5590, "longitude": 73.7868},
    {"id": "khadakwasla", "name": "Khadakwasla Dam", "latitude": 18.4425, "longitude": 73.7686},
]
EXTRA = {
    "rainfall_basis": "city_centre_dataset",
    "coordinate_note": "Approximate representative point; not a measurement site.",
    "rainfall_note": ("Rainfall shown is from the Pune city-centre dataset, "
                      "not measured at this location."),
}


def list_areas():
    return [{**a, **EXTRA} for a in AREAS]


def get_area(area_id):
    return next((a for a in list_areas() if a["id"] == area_id), None)
