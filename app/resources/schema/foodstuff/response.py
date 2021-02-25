from models.db import Foodstuff
from app import ma

from resources.schema.dictionary.store_section.response import StoreSectionResponseSchema


class FoodstuffsResponseSchema(ma.SQLAlchemySchema):

    def __init__(self):
        super(FoodstuffsResponseSchema, self).__init__()
        self.many = True

    class Meta:
        model = Foodstuff
        include_relationships = True
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    store_section = ma.Pluck(StoreSectionResponseSchema, 'name')

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('foodstuffdetail', values=dict(id='<id>'))
        }
    })


class FoodstuffResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Foodstuff

    id = ma.auto_field()
    name = ma.auto_field()
    store_section = ma.Pluck(StoreSectionResponseSchema, 'name')

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('foodstuffdetail', values=dict(id='<id>'))
        }
    })
