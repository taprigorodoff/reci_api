from models.db import MenuDish
from app import ma

from resources.schema.dish.response import DishResponseSchema


class MenuDishResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = MenuDish

    dish = ma.Pluck(DishResponseSchema, 'name')
    portion = ma.auto_field()

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('menudishdetail', values=dict(menu_id='<menu_id>', id='<id>'))
        },
        'collection': {
            'href': ma.URLFor('menudishlist', values=dict(menu_id='<menu_id>'))
        },
        'menu': {
            'href': ma.URLFor('menudetail', values=dict(id='<menu_id>'))
        }
    })
