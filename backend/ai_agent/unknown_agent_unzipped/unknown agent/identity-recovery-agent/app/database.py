"""In-memory store for the demo. Swap for PostgreSQL later."""

records: list[dict] = [
    {
        "record_id": "H-781", "source_type": "HOSPITAL",
        "name": None, "partial_name": None,
        "age": 35, "gender": "male", "clothing": "blue shirt",
        "physical_description": "medium build, black hair",
        "location": "Government Hospital", "origin_location": None,
        "timestamp": "2026-10-08 11:20", "medical_condition": "leg injury",
    },
    {
        "record_id": "R-221", "source_type": "RESCUE",
        "name": None, "partial_name": None,
        "age": 32, "gender": "male", "clothing": "blue shirt",
        "physical_description": "medium build, black hair",
        "location": "Road X", "origin_location": "Road X",
        "timestamp": "2026-10-08 10:40", "medical_condition": None,
    },
    {
        "record_id": "S-442", "source_type": "SHELTER",
        "name": None, "partial_name": "Arun",
        "age": 35, "gender": "male", "clothing": "blue shirt",
        "physical_description": "medium build",
        "location": "Relief Shelter A", "origin_location": "Road X area",
        "timestamp": "2026-10-08 14:30", "medical_condition": None,
    },
    {
        "record_id": "F-901", "source_type": "FAMILY",
        "name": "Arun Kumar", "partial_name": None,
        "age": 34, "gender": "male", "clothing": "blue shirt",
        "physical_description": "medium build, black hair",
        "location": "Road X", "origin_location": None,
        "timestamp": "2026-10-08 10:00", "medical_condition": None,
    },
]

clusters: list[dict] = []
