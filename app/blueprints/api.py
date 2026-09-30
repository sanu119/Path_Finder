from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.engine import calculate_gap, LEVEL_NAMES, normalize_level
from app.models import Career, CareerSkill, Profile, Resource, Roadmap, RoadmapStep, Skill, UserSkill

api_bp = Blueprint("api", __name__)


def fail(message, status=400):
    return jsonify({"success": False, "error": message}), status


def require_json():
    return request.get_json(silent=True) or {}


def career_json(c):
    return {"id": c.id, "name": c.name, "category": c.category, "description": c.description, "icon": c.icon, "skill_count": len(c.career_skills)}


def skill_json(s):
    return {"id": s.id, "name": s.name, "category": s.category, "description": s.description}


@api_bp.get("/profile")
@login_required
def get_profile():
    p = current_user.profile or Profile(user_id=current_user.id)
    return jsonify({"success": True, "profile": {"name": p.name, "education_level": p.education_level, "branch": p.branch, "year": p.year, "interests": p.interests}})


@api_bp.put("/profile")
@login_required
def update_profile():
    data = require_json()
    p = current_user.profile or Profile(user_id=current_user.id)
    p.name = str(data.get("name", p.name)).strip()[:120]
    p.education_level = str(data.get("education_level", p.education_level)).strip()[:80]
    p.branch = str(data.get("branch", p.branch)).strip()[:120]
    p.year = str(data.get("year", p.year)).strip()[:40]
    p.interests = str(data.get("interests", p.interests)).strip()[:500]
    db.session.add(p)
    db.session.commit()
    return jsonify({"success": True, "message": "Profile saved."})


@api_bp.post("/profile/skills")
@login_required
def update_user_skill():
    data = require_json()
    skill_id, level = data.get("skill_id"), normalize_level(data.get("level"))
    skill = db.session.get(Skill, int(skill_id)) if skill_id else None
    if not skill or level not in (1, 2, 3):
        return fail("A valid skill and proficiency level are required.")
    us = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill.id).first()
    if not us:
        us = UserSkill(user_id=current_user.id, skill_id=skill.id)
        db.session.add(us)
    us.level = level
    db.session.commit()
    return jsonify({"success": True})


@api_bp.get("/skills")
def skills():
    q = str(request.args.get("q", "")).strip()
    query = Skill.query
    if q:
        query = query.filter(or_(Skill.name.ilike(f"%{q}%"), Skill.category.ilike(f"%{q}%")))
    return jsonify({"success": True, "skills": [skill_json(s) for s in query.order_by(Skill.name).all()]})


@api_bp.get("/careers")
def careers():
    q = str(request.args.get("q", "")).strip()
    category = str(request.args.get("category", "")).strip()
    query = Career.query
    if q:
        query = query.filter(or_(Career.name.ilike(f"%{q}%"), Career.description.ilike(f"%{q}%")))
    if category:
        query = query.filter_by(category=category)
    items = query.order_by(Career.name).all()
    return jsonify({"success": True, "careers": [career_json(c) for c in items], "categories": sorted({c.category for c in Career.query.all()})})


@api_bp.get("/careers/<int:career_id>")
def career_detail(career_id):
    c = db.session.get(Career, career_id)
    if not c:
        return fail("Career not found.", 404)
    links = sorted(c.career_skills, key=lambda x: x.order_index)
    return jsonify({"success": True, "career": career_json(c), "skills": [{"id": x.skill.id, "name": x.skill.name, "category": x.skill.category, "required_level": x.required_level, "required_level_name": LEVEL_NAMES[x.required_level], "priority": x.priority, "order_index": x.order_index} for x in links]})


@api_bp.get("/careers/<int:career_id>/skills")
def career_skills(career_id):
    c = db.session.get(Career, career_id)
    if not c:
        return fail("Career not found.", 404)
    return career_detail(career_id)


@api_bp.post("/gap-analysis")
@login_required
def gap_analysis():
    data = require_json()
    career_id = data.get("career_id")
    if not career_id:
        return fail("career_id is required.")
    career = db.session.get(Career, int(career_id))
    if not career:
        return fail("Career not found.", 404)
    current = {str(us.skill_id): us.level for us in current_user.user_skills}
    required = [{"skill_id": cs.skill_id, "skill_name": cs.skill.name, "required_level": cs.required_level, "priority": cs.priority} for cs in career.career_skills]
    result = calculate_gap(required, current)
    result["career"] = career_json(career)
    return jsonify({"success": True, **result})


@api_bp.post("/roadmaps/generate")
@login_required
def generate_roadmap():
    data = require_json()
    career_id = data.get("career_id")
    if not career_id:
        return fail("career_id is required.")
    career = db.session.get(Career, int(career_id))
    if not career:
        return fail("Career not found.", 404)

    roadmap = Roadmap(user_id=current_user.id, career_id=career.id, title=f"{career.name} Roadmap")
    db.session.add(roadmap)
    db.session.flush()
    current = {us.skill_id: us.level for us in current_user.user_skills}
    ordered = sorted(career.career_skills, key=lambda x: (-{'High': 3, 'Medium': 2, 'Low': 1}.get(x.priority, 2), x.order_index))
    phases = [("Foundation", 0), ("Intermediate", 1), ("Advanced", 2), ("Projects", 3), ("Internship / Job Ready", 4)]
    for i, cs in enumerate(ordered):
        level = current.get(cs.skill_id, 0)
        if level >= cs.required_level:
            phase = "Projects"
        elif level == 0 and cs.required_level >= 2:
            phase = "Foundation" if i < 4 else "Intermediate"
        else:
            phase = "Intermediate" if cs.required_level <= 2 else "Advanced"
        resource = Resource.query.filter_by(skill_id=cs.skill_id).first()
        step = RoadmapStep(
            roadmap_id=roadmap.id,
            skill_id=cs.skill_id,
            phase=phase,
            title=f"Build {cs.skill.name}",
            description=f"Reach {LEVEL_NAMES[cs.required_level]} level in {cs.skill.name} with focused practice.",
            duration="1–2 weeks" if cs.required_level <= 2 else "2–3 weeks",
            resource_id=resource.id if resource else None,
            project=f"Build a small {cs.skill.name} project and document it on GitHub.",
            order_index=i,
        )
        db.session.add(step)
    db.session.commit()
    return jsonify({"success": True, "roadmap_id": roadmap.id, "message": "Personalized roadmap generated."}), 201


def roadmap_payload(r):
    completed = sum(s.status == "Completed" for s in r.steps)
    total = len(r.steps)
    return {"id": r.id, "title": r.title, "career": career_json(r.career), "created_at": r.created_at.isoformat(), "progress": round(completed / total * 100) if total else 0,
            "steps": [{"id": s.id, "phase": s.phase, "title": s.title, "description": s.description, "duration": s.duration, "project": s.project, "status": s.status, "completed_at": s.completed_at.isoformat() if s.completed_at else None, "skill": skill_json(s.skill) if s.skill else None, "resource": {"title": s.resource.title, "url": s.resource.url, "type": s.resource.resource_type} if s.resource else None} for s in r.steps]}


@api_bp.get("/roadmaps")
@login_required
def roadmaps():
    return jsonify({"success": True, "roadmaps": [roadmap_payload(r) for r in Roadmap.query.filter_by(user_id=current_user.id).order_by(Roadmap.updated_at.desc()).all()]})


@api_bp.get("/roadmaps/<int:roadmap_id>")
@login_required
def get_roadmap(roadmap_id):
    r = db.session.get(Roadmap, roadmap_id)
    if not r or r.user_id != current_user.id:
        return fail("Roadmap not found.", 404)
    return jsonify({"success": True, "roadmap": roadmap_payload(r)})


@api_bp.patch("/roadmaps/steps/<int:step_id>")
@login_required
def update_step(step_id):
    step = db.session.get(RoadmapStep, step_id)
    if not step or step.roadmap.user_id != current_user.id:
        return fail("Step not found.", 404)
    status = str((require_json()).get("status", "")).strip()
    if status not in {"Not Started", "In Progress", "Completed"}:
        return fail("Invalid status.")
    step.status = status
    step.completed_at = datetime.utcnow() if status == "Completed" else None
    db.session.commit()
    return jsonify({"success": True, "status": step.status})


@api_bp.get("/compare")
def compare():
    a = request.args.get("career_a", type=int)
    b = request.args.get("career_b", type=int)
    if not a or not b:
        return fail("career_a and career_b are required.")
    ca, cb = db.session.get(Career, a), db.session.get(Career, b)
    if not ca or not cb:
        return fail("One or both careers were not found.", 404)
    sa = {x.skill_id: x for x in ca.career_skills}
    sb = {x.skill_id: x for x in cb.career_skills}
    ids = sorted(set(sa) | set(sb))
    rows = []
    for sid in ids:
        skill = db.session.get(Skill, sid)
        rows.append({"skill": skill.name, "career_a": LEVEL_NAMES[sa[sid].required_level] if sid in sa else "—", "career_b": LEVEL_NAMES[sb[sid].required_level] if sid in sb else "—", "overlap": sid in sa and sid in sb})
    overlap = len(set(sa) & set(sb))
    return jsonify({"success": True, "career_a": career_json(ca), "career_b": career_json(cb), "overlap": overlap, "total_unique_skills": len(ids), "skills": rows})
