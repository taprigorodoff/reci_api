from models.db import DStoreSection
from app import ma


class StoreSectionResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = DStoreSection

    id = ma.auto_field()
    name = ma.auto_field()
