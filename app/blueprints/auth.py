import re
from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_user, logout_user
from app import db
from app.models import User, Profile


auth_bp = Blueprint("auth", __name__)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not EMAIL_RE.match(email):
        return error("Enter a valid email address.")
    if len(password) < 8:
        return error("Password must be at least 8 characters.")
    if User.query.filter_by(email=email).first():
        return error("An account with this email already exists.", 409)
    user = User(email=email)
    user.set_password(password)
    user.profile = Profile(name=str(data.get("name", "")).strip())
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=False)
    return jsonify({"success": True, "message": "Account created.", "user": {"id": user.id, "email": user.email}}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error("Invalid email or password.", 401)
    login_user(user, remember=bool(data.get("remember")))
    session.permanent = False
    return jsonify({"success": True, "message": "Welcome back.", "user": {"id": user.id, "email": user.email, "role": user.role}})


@auth_bp.post("/logout")
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out."})


@auth_bp.get("/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False})
    return jsonify({"authenticated": True, "user": {"id": current_user.id, "email": current_user.email, "role": current_user.role}})
