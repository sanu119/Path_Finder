from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_skills = db.relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    roadmaps = db.relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False, default="")
    education_level = db.Column(db.String(80), default="")
    branch = db.Column(db.String(120), default="")
    year = db.Column(db.String(40), default="")
    interests = db.Column(db.Text, default="")

    user = db.relationship("User", back_populates="profile")


class Career(db.Model):
    __tablename__ = "careers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(40), default="bi-briefcase")

    career_skills = db.relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    roadmaps = db.relationship("Roadmap", back_populates="career")


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80), default="Core")
    description = db.Column(db.Text, default="")

    career_skills = db.relationship("CareerSkill", back_populates="skill", cascade="all, delete-orphan")
    user_skills = db.relationship("UserSkill", back_populates="skill")


class CareerSkill(db.Model):
    __tablename__ = "career_skills"
    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    required_level = db.Column(db.Integer, nullable=False, default=2)
    priority = db.Column(db.String(20), default="Medium", nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)

    career = db.relationship("Career", back_populates="career_skills")
    skill = db.relationship("Skill", back_populates="career_skills")

    __table_args__ = (db.UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),)


class UserSkill(db.Model):
    __tablename__ = "user_skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", back_populates="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    __table_args__ = (db.UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)


class Roadmap(db.Model):
    __tablename__ = "roadmaps"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="roadmaps")
    career = db.relationship("Career", back_populates="roadmaps")
    steps = db.relationship("RoadmapStep", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapStep.order_index")


class RoadmapStep(db.Model):
    __tablename__ = "roadmap_steps"
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmaps.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)
    phase = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, default="")
    duration = db.Column(db.String(60), default="2 weeks")
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=True)
    project = db.Column(db.String(240), default="")
    order_index = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default="Not Started", nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    roadmap = db.relationship("Roadmap", back_populates="steps")
    skill = db.relationship("Skill")
    resource = db.relationship("Resource")


class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), default="Course")
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=True)

    skill = db.relationship("Skill")
