from api.app import db
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import orm as so
from alchemical import Model
from typing import Optional
from api.dates import naive_utcnow
import jwt
from flask import current_app, url_for
import secrets

class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class Token(Model):
    __tablename__ = 'tokens'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    access_token: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    access_expiration: so.Mapped[datetime]
    refresh_token: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    refresh_expiration: so.Mapped[datetime]
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey('users.id'), index=True)

    user: so.Mapped['User'] = so.relationship(back_populates='tokens')

    @property
    def access_token_jwt(self):
        return jwt.encode({'token': self.access_token},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = naive_utcnow() + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = naive_utcnow() + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self, delay=None):
        if delay is None:  # pragma: no branch
            # 5 second delay to allow simultaneous requests
            delay = 5 if not current_app.testing else 0
        self.access_expiration = naive_utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = naive_utcnow() + timedelta(seconds=delay)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = naive_utcnow() - timedelta(days=1)
        db.session.execute(Token.delete().where(
            Token.refresh_expiration < yesterday))

    @staticmethod
    def from_jwt(access_token_jwt):
        access_token = None
        try:
            access_token = jwt.decode(access_token_jwt,
                                      current_app.config['SECRET_KEY'],
                                      algorithms=['HS256'])['token']
            return db.session.scalar(Token.select().filter_by(
                access_token=access_token))
        except jwt.PyJWTError:
            pass
        
class User(Model, Updateable):
    __tablename__ = "users"
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), nullable=False, index=True, unique=True
    )
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    first_active: so.Mapped[datetime] = so.mapped_column(default=naive_utcnow)
    last_active: so.Mapped[datetime] = so.mapped_column(default=naive_utcnow)
    tokens: so.WriteOnlyMapped['Token'] = so.relationship(back_populates="user")
    meals: so.Mapped[Optional[dict]] = so.mapped_column(sa.JSON, default={})

    def add_meal(self, meal_id, meal_name):
        meal = self.meals.get(meal_id)
        if meal:
            meal['count'] += 1
            meal['last_use'] = (naive_utcnow() - datetime(1970, 1, 1)).total_seconds() / 60
        else:
            self.meals[meal_id] = {
                'meal_name': meal_name,
                'count': 1,
                'last_use': (naive_utcnow() - datetime(1970, 1, 1)).total_seconds() / 60
            }

    def remove_meal(self, meal_id):
        meal = self.meals.get(meal_id)
        if meal:
            meal['count'] -= 1
            if meal['count'] <= 0:
                del self.meals[meal_id]

    def __repr__(self):
        return f"<User {self.username}>"

class Meal(Model):
    __tablename__ = 'meals'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    last_used: so.Mapped[datetime] = so.mapped_column(default=naive_utcnow)
    use_count: so.Mapped[int] = so.mapped_column(default=0)
    is_vegan: so.Mapped[bool] = so.mapped_column(default=False)

    def update_usage(self):
        self.last_used = naive_utcnow()
        self.use_count += 1

    @staticmethod
    def get_frequently_used(user_id, limit=10):
        user = db.session.scalar(User.select().filter_by(id=user_id))
        if user and user.meals:
            meals = sorted(user.meals.values(), key=lambda x: (-x['count'], -x['last_use']))
            return meals[:limit]
        return []

class Food(Model):
    __tablename__ = 'foods'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), nullable=False)
    nutrition: so.Mapped[Optional[dict]] = so.mapped_column(sa.JSON, default={})

    def set_nutrition(self, calories=None, protein=None, carbs=None, fats=None):
        nutrition_data = {
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats
        }
        self.nutrition = nutrition_data

    def get_nutrition(self):
        return self.nutrition

class Unit(Model):
    __tablename__ = 'units'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    abbreviation: so.Mapped[str] = so.mapped_column(sa.String(16), nullable=False)


