from faker import Faker

from app.extension import db
from app.factories.base_factory import BaseFactory
from app.models import Post, User

fake = Faker()


class PostFactory:
    def make_data():
        """Return fake post data (not saved to DB)."""

        user = User.query.order_by(db.func.random()).first()
        user_id = user.id if user else 1

        return {
            "title": fake.unique.sentence(nb_words=6),
            "description": fake.text(max_nb_chars=500),
            "status": fake.random_element(elements=(0, 1)),
            "create_user_id": user_id,
            "updated_user_id": user_id,
            "deleted_user_id": None,
        }

    def create():
        return BaseFactory.create_one(PostFactory.make_data, Post)

    def create_many(count=10):
        return BaseFactory.create_many(PostFactory.make_data, Post, count)
