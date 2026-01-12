# app/factories/base_factory.py
from app.extension import db
from app.utils.decorators import static_all_methods


@static_all_methods
class BaseFactory:

    def create_one(make_func):
        obj = make_func()
        db.session.add(obj)
        db.session.commit()
        return obj

    def create_many(make_func, count=1):
        objects = []
        for _ in range(count):
            obj = make_func()
            db.session.add(obj)
            objects.append(obj)

        db.session.commit()
        return objects
