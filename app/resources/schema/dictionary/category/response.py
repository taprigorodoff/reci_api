from models.db import DCategory
from app import ma


class CategoryResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = DCategory

    id = ma.auto_field()
    name = ma.auto_field()
