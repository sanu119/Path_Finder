from functools import wraps
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Career, CareerSkill, Skill

admin_bp = Blueprint("admin", __name__)


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapped


def payload():
    return request.get_json(silent=True) or {}


@admin_bp.get("")
def admin_root():
    return "<h2>Pathfinder Admin API</h2><p>Use /admin-ui after logging in as an administrator.</p>"


@admin_bp.get("/careers")
@admin_required
def list_careers():
    return jsonify({"success": True, "careers": [{"id": c.id, "name": c.name, "category": c.category, "description": c.description, "skill_count": len(c.career_skills)} for c in Career.query.order_by(Career.name).all()]})


@admin_bp.post("/careers")
@admin_required
def create_career():
    d = payload()
    name, category = str(d.get("name", "")).strip(), str(d.get("category", "")).strip()
    if not name or not category:
        return jsonify({"success": False, "error": "Name and category are required."}), 400
    if Career.query.filter_by(name=name).first():
        return jsonify({"success": False, "error": "Career already exists."}), 409
    c = Career(name=name, category=category, description=str(d.get("description", "")).strip(), icon=str(d.get("icon", "bi-briefcase")))
    db.session.add(c)
    db.session.commit()
    return jsonify({"success": True, "career": {"id": c.id, "name": c.name}}), 201


@admin_bp.put("/careers/<int:career_id>")
@admin_required
def edit_career(career_id):
    c = db.session.get(Career, career_id)
    if not c:
        return jsonify({"success": False, "error": "Career not found."}), 404
    d = payload()
    c.name = str(d.get("name", c.name)).strip()
    c.category = str(d.get("category", c.category)).strip()
    c.description = str(d.get("description", c.description)).strip()
    c.icon = str(d.get("icon", c.icon)).strip()
    if not c.name or not c.category:
        return jsonify({"success": False, "error": "Name and category are required."}), 400
    db.session.commit()
    return jsonify({"success": True, "message": "Career updated."})


@admin_bp.delete("/careers/<int:career_id>")
@admin_required
def delete_career(career_id):
    c = db.session.get(Career, career_id)
    if not c:
        return jsonify({"success": False, "error": "Career not found."}), 404
    if c.roadmaps:
        return jsonify({"success": False, "error": "Cannot delete a career already used by roadmaps."}), 409
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True})


@admin_bp.get("/skills")
@admin_required
def list_skills():
    return jsonify({"success": True, "skills": [{"id": s.id, "name": s.name, "category": s.category} for s in Skill.query.order_by(Skill.name).all()]})


@admin_bp.post("/skills")
@admin_required
def create_skill():
    d = payload()
    name = str(d.get("name", "")).strip()
    if not name:
        return jsonify({"success": False, "error": "Skill name is required."}), 400
    if Skill.query.filter_by(name=name).first():
        return jsonify({"success": False, "error": "Skill already exists."}), 409
    s = Skill(name=name, category=str(d.get("category", "Core")).strip(), description=str(d.get("description", "")).strip())
    db.session.add(s)
    db.session.commit()
    return jsonify({"success": True, "skill": {"id": s.id, "name": s.name}}), 201


@admin_bp.put("/skills/<int:skill_id>")
@admin_required
def edit_skill(skill_id):
    s = db.session.get(Skill, skill_id)
    if not s:
        return jsonify({"success": False, "error": "Skill not found."}), 404
    d = payload()
    s.name = str(d.get("name", s.name)).strip()
    s.category = str(d.get("category", s.category)).strip()
    s.description = str(d.get("description", s.description)).strip()
    if not s.name:
        return jsonify({"success": False, "error": "Skill name is required."}), 400
    db.session.commit()
    return jsonify({"success": True})


@admin_bp.delete("/skills/<int:skill_id>")
@admin_required
def delete_skill(skill_id):
    s = db.session.get(Skill, skill_id)
    if not s:
        return jsonify({"success": False, "error": "Skill not found."}), 404
    if s.career_skills:
        return jsonify({"success": False, "error": "Remove this skill from careers before deleting it."}), 409
    db.session.delete(s)
    db.session.commit()
    return jsonify({"success": True})


@admin_bp.get("/career-skills/<int:career_id>")
@admin_required
def get_career_skills(career_id):
    c = db.session.get(Career, career_id)
    if not c:
        return jsonify({"success": False, "error": "Career not found."}), 404
    return jsonify({"success": True, "skills": [{"id": x.id, "skill_id": x.skill_id, "name": x.skill.name, "required_level": x.required_level, "priority": x.priority, "order_index": x.order_index} for x in sorted(c.career_skills, key=lambda x: x.order_index)]})


@admin_bp.post("/career-skills")
@admin_required
def add_career_skill():
    d = payload()
    career_id, skill_id = d.get("career_id"), d.get("skill_id")
    if not career_id or not skill_id:
        return jsonify({"success": False, "error": "career_id and skill_id are required."}), 400
    if CareerSkill.query.filter_by(career_id=career_id, skill_id=skill_id).first():
        return jsonify({"success": False, "error": "Skill already attached to career."}), 409
    cs = CareerSkill(career_id=int(career_id), skill_id=int(skill_id), required_level=max(1, min(3, int(d.get("required_level", 2)))), priority=str(d.get("priority", "Medium")), order_index=int(d.get("order_index", 0)))
    db.session.add(cs)
    db.session.commit()
    return jsonify({"success": True, "id": cs.id}), 201


@admin_bp.put("/career-skills/<int:link_id>")
@admin_required
def edit_career_skill(link_id):
    cs = db.session.get(CareerSkill, link_id)
    if not cs:
        return jsonify({"success": False, "error": "Career skill not found."}), 404
    d = payload()
    cs.required_level = max(1, min(3, int(d.get("required_level", cs.required_level))))
    cs.priority = str(d.get("priority", cs.priority))
    cs.order_index = int(d.get("order_index", cs.order_index))
    db.session.commit()
    return jsonify({"success": True})


@admin_bp.delete("/career-skills/<int:link_id>")
@admin_required
def delete_career_skill(link_id):
    cs = db.session.get(CareerSkill, link_id)
    if not cs:
        return jsonify({"success": False, "error": "Career skill not found."}), 404
    db.session.delete(cs)
    db.session.commit()
    return jsonify({"success": True})
