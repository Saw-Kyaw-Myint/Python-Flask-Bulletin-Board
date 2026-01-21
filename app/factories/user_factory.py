# app/factories/user_factory.py
from faker import Faker

from app.factories.base_factory import BaseFactory
from app.models import User
from app.utils.hash import hash_password

fake = Faker()


class UserFactory:

    def make_data():
        """Return fake user data (not saved to DB)."""

        return {
            "name": fake.name(),
            "email": fake.unique.email(),
            "password": hash_password("Password123@"),
            "phone": "09451340513",
            "address": fake.address(),
        }

    def create():
        return BaseFactory.create_one(UserFactory.make_data, User)

    def create_many(count=10):
        return BaseFactory.create_many(UserFactory.make_data, User, count)
