from app.engine import calculate_gap, classify


def test_classify():
    assert classify(2, 2) == "Matched"
    assert classify(3, 1) == "Partial"
    assert classify(2, 0) == "Missing"


def test_gap_readiness_and_counts():
    required = [
        {"skill_id": 1, "skill_name": "Python", "required_level": 3, "priority": "High"},
        {"skill_id": 2, "skill_name": "SQL", "required_level": 2, "priority": "Medium"},
        {"skill_id": 3, "skill_name": "Git", "required_level": 2, "priority": "Low"},
    ]
    result = calculate_gap(required, {"1": 3, "2": 1})
    assert result["counts"] == {"Matched": 1, "Partial": 1, "Missing": 1}
    assert 0 < result["readiness"] < 100
