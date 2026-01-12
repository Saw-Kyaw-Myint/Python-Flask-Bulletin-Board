# app/factories/user_factory.py
from faker import Faker

from app.factories.base_factory import BaseFactory
from app.models import User

fake = Faker()


class UserFactory:

    def make():
        return User(
            name=fake.name(),
            email=fake.unique.email(),
        )

    def create():
        return BaseFactory.create_one(UserFactory.make)

    def create_many(count=10):
        return BaseFactory.create_many(UserFactory.make, count)
