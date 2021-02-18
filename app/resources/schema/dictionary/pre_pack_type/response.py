from models.db import DPrePackType
from app import ma


class PrePackTypeResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = DPrePackType

    id = ma.auto_field()
    name = ma.auto_field()
