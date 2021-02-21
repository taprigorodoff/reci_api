from models.db import Menu
from app import ma


class MenuResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Menu

    name = ma.auto_field()

    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('menudetail', values=dict(id='<id>'))
        },
        'dishes': {
            'href': ma.URLFor('menudishlist', values=dict(menu_id='<id>'))
        }
    })
