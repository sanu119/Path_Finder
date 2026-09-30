from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/login")
def login_page():
    return render_template("login.html")


@main_bp.route("/register")
def register_page():
    return render_template("register.html")


@main_bp.route("/onboarding")
def onboarding():
    return render_template("onboarding.html")


@main_bp.route("/careers")
def careers_page():
    return render_template("careers.html")


@main_bp.route("/gap")
def gap_page():
    return render_template("gap.html")


@main_bp.route("/roadmap/<int:roadmap_id>")
def roadmap_page(roadmap_id):
    return render_template("roadmap.html", roadmap_id=roadmap_id)


@main_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/compare")
def compare_page():
    return render_template("compare.html")


@main_bp.route("/admin-ui")
def admin_page():
    return render_template("admin.html")
