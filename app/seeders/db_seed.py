# app/seeders/user_seeder.py
from app.factories.user_factory import UserFactory


def run():
    UserFactory.create_many(50)
