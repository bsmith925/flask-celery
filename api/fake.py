#api/fake.py
import random
import click
from flask import Blueprint
from faker import Faker
from api.app import db
from api.models import User, Unit, Food, Meal

fake = Blueprint("fake", __name__)
faker = Faker()

@fake.cli.command()
@click.argument("num_units", type=int)
def units(num_units):
    """Create a given number of fake units"""
    units = []
    for _ in range(num_units):
        unit = Unit(name=faker.word(), abbreviation=faker.word()[:3])
        units.append(unit)
    db.session.bulk_save_objects(units)
    db.session.commit()
    print(f"{num_units} units added.")

# Example CLI command: flask fake units 10

@fake.cli.command()
@click.argument("num_foods", type=int)
def foods(num_foods):
    """Create a given number of fake foods"""
    foods = []
    for _ in range(num_foods):
        food = Food(
            name=faker.word(),
            calories=random.randint(50, 500),
            protein=random.randint(0, 50),
            carbs=random.randint(0, 100),
            fats=random.randint(0, 50),
            fiber=random.randint(0, 30),
            sugar=random.randint(0, 50),
            sodium=random.randint(0, 2000)
        )
        foods.append(food)
    db.session.bulk_save_objects(foods)
    db.session.commit()
    print(f"{num_foods} foods added.")

# Example CLI command: flask fake foods 20

@fake.cli.command()
@click.argument("num_meals", type=int)
def meals(num_meals):
    """Create a given number of fake meals"""
    meals = []
    for _ in range(num_meals):
        meal = Meal(name=faker.word())
        meals.append(meal)
    db.session.bulk_save_objects(meals)
    db.session.commit()
    print(f"{num_meals} meals added.")

# Example CLI command: flask fake meals 15

@fake.cli.command()
@click.argument("num_users", type=int)
def users(num_users):
    """Create a given number of fake users"""
    users = []
    for _ in range(num_users):
        user = User(username=faker.user_name(), email=faker.email())
        users.append(user)
    db.session.bulk_save_objects(users)
    db.session.commit()
    print(f"{num_users} users added.")

# Example CLI command: flask fake users 5

@fake.cli.command()
@click.argument("num_users", type=int)
@click.argument("num_meals", type=int)
@click.argument("max_meals_per_user", type=int)
def plan_meals(num_users, num_meals, max_meals_per_user):
    """Plan meals for a given number of users with a max number of meals per user"""
    users = db.session.scalars(User.select().limit(num_users)).all()
    meals = db.session.scalars(Meal.select().limit(num_meals)).all()
    for user in users:
        for _ in range(random.randint(1, max_meals_per_user)):  # Each user has 1 to max_meals_per_user meals
            meal = random.choice(meals)
            user.add_meal(meal.id, meal.name)
    db.session.commit()
    print(f"Meals planned for {num_users} users with up to {max_meals_per_user} meals each.")

# Example CLI command: flask fake plan_meals 5 10 5

@fake.cli.command()
@click.argument("num_users", type=int)
@click.argument("num_units", type=int)
@click.argument("num_foods", type=int)
@click.argument("num_meals", type=int)
@click.argument("max_meals_per_user", type=int)
def generate_data(num_users, num_units, num_foods, num_meals, max_meals_per_user):
    """Create a given number of fake users, units, foods, and meals"""
    units(num_units)
    foods(num_foods)
    meals(num_meals)
    users(num_users)
    plan_meals(num_users, num_meals, max_meals_per_user)
    print(f"{num_users} users, {num_units} units, {num_foods} foods, and {num_meals} meals added.")

# Example CLI command: flask fake generate_data 5 10 20 15 5