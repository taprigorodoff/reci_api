from models.db import Dish
from app import ma

from resources.schema.dictionary.category.response import CategoryResponseSchema


class DishesResponseSchema(ma.SQLAlchemySchema):

    def __init__(self):
        super(DishesResponseSchema, self).__init__()
        self.many = True

    class Meta:
        model = Dish

    id = ma.auto_field()
    name = ma.auto_field()
    cook_time = ma.auto_field()
    all_time = ma.auto_field()
    portion = ma.auto_field()
    categories = ma.Pluck(CategoryResponseSchema, 'name', many=True)

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('dishdetail', values=dict(id='<id>'))
        }
    })


class DishResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Dish

    name = ma.auto_field()
    description = ma.auto_field()
    portion = ma.auto_field()
    cook_time = ma.auto_field()
    all_time = ma.auto_field()
    categories = ma.Pluck(CategoryResponseSchema, 'name', many=True)

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('dishdetail', values=dict(id='<id>'))
        },
        'ingredients': {
            'href': ma.URLFor('ingredientlist', values=dict(dish_id='<id>'))
        },
        'img': {
            'href': ma.URLFor('dishimg', values=dict(dish_id='<id>'))
        }
    })
