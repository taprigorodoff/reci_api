from models.db import DUnit
from app import ma


class UnitResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = DUnit

    id = ma.auto_field()
    name = ma.auto_field()
