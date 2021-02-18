from models.db import DStage
from app import ma


class StageResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = DStage

    id = ma.auto_field()
    name = ma.auto_field()
