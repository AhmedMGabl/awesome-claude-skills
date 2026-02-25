---
name: python-flask
description: Python Flask patterns covering routing, blueprints, request handling, Jinja2 templates, Flask-SQLAlchemy, authentication, error handling, and testing.
---

# Python Flask

This skill should be used when building web applications with Python Flask. It covers routing, blueprints, templates, database integration, authentication, and testing.

## When to Use This Skill

Use this skill when you need to:

- Build web applications and APIs with Flask
- Organize code with blueprints
- Use Jinja2 templates for server rendering
- Integrate SQLAlchemy for database access
- Implement authentication and error handling

## Setup

```bash
pip install flask flask-sqlalchemy flask-migrate flask-cors
```

## Basic Application

```python
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

@app.route("/api/users", methods=["GET"])
def list_users():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    users = User.query.paginate(page=page, per_page=limit)
    return jsonify({
        "users": [u.to_dict() for u in users.items],
        "total": users.total,
        "page": page,
    })

@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        abort(400, description="Missing required fields")
    user = User(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

## Blueprints

```python
# blueprints/users.py
from flask import Blueprint, jsonify, request

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

@users_bp.route("/", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# app.py
from blueprints.users import users_bp
app.register_blueprint(users_bp)
```

## Database Models

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Error Handling

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500
```

## Authentication Decorator

```python
from functools import wraps
from flask import request, g
import jwt

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            abort(401, description="Missing token")
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            g.user_id = payload["sub"]
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")
        return f(*args, **kwargs)
    return decorated

@app.route("/api/profile")
@login_required
def get_profile():
    user = User.query.get(g.user_id)
    return jsonify(user.to_dict())
```

## Testing

```python
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_user(client):
    response = client.post("/api/users", json={"name": "Alice", "email": "alice@example.com"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Alice"

def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404
```

## Additional Resources

- Flask: https://flask.palletsprojects.com/
- Flask-SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/
- Flask Tutorial: https://flask.palletsprojects.com/en/stable/tutorial/
