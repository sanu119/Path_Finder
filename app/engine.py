LEVELS = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
LEVEL_NAMES = {1: "Beginner", 2: "Intermediate", 3: "Advanced"}


def normalize_level(value):
    if isinstance(value, int):
        return max(0, min(3, value))
    return LEVELS.get(str(value).title(), 0)


def classify(required_level, current_level):
    required = normalize_level(required_level)
    current = normalize_level(current_level)
    if current >= required:
        return "Matched"
    if current > 0:
        return "Partial"
    return "Missing"


def calculate_gap(required_skills, current_skills):
    current = {int(k): normalize_level(v) for k, v in current_skills.items()}
    results = []
    weighted_total = 0
    weighted_current = 0
    for item in required_skills:
        sid = int(item["skill_id"])
        required = normalize_level(item["required_level"])
        level = current.get(sid, 0)
        status = classify(required, level)
        priority = str(item.get("priority", "Medium")).lower()
        weight = {"high": 3, "medium": 2, "low": 1}.get(priority, 2)
        weighted_total += required * weight
        weighted_current += min(level, required) * weight
        results.append({**item, "current_level": level, "current_level_name": LEVEL_NAMES.get(level, "Not Set"), "required_level_name": LEVEL_NAMES.get(required, "Advanced"), "status": status, "priority": item.get("priority", "Medium")})
    readiness = round((weighted_current / weighted_total) * 100) if weighted_total else 0
    counts = {"Matched": 0, "Partial": 0, "Missing": 0}
    for r in results:
        counts[r["status"]] += 1
    return {"readiness": readiness, "counts": counts, "skills": results}
