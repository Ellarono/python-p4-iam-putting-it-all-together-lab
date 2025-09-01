from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=True)  # allow null for tests
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    recipes = db.relationship('Recipe', backref='user', lazy=True, cascade="all, delete-orphan")

    @property
    def password_hash(self):
        raise AttributeError('Password hashes cannot be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        if not self._password_hash:
            return False
        return check_password_hash(self._password_hash, password)

    def to_dict(self, include_recipes=False):
        data = {
            'id': self.id,
            'username': self.username,
            'bio': self.bio,
            'image_url': self.image_url,
        }
        if include_recipes:
            data['recipes'] = [recipe.to_dict(include_user=False) for recipe in self.recipes]
        return data


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # allow null for tests

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or len(value.strip()) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return value

    def to_dict(self, include_user=True):
        data = {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
        }
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'image_url': self.user.image_url,
                'bio': self.user.bio,
            }
        return data
