from models.db import Ingredient
from app import ma

from resources.schema.foodstuff.response import FoodstuffResponseSchema
from resources.schema.dictionary.stage.response import StageResponseSchema
from resources.schema.dictionary.unit.response import UnitResponseSchema
from resources.schema.dictionary.pre_pack_type.response import PrePackTypeResponseSchema


class IngredientResponseSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Ingredient

    foodstuff = ma.Pluck(FoodstuffResponseSchema, 'name')
    unit = ma.Pluck(UnitResponseSchema, 'name')
    amount = ma.auto_field()
    stage = ma.Pluck(StageResponseSchema, 'name')
    pre_pack_type = ma.Pluck(PrePackTypeResponseSchema, 'name')
    alternatives = ma.Pluck(FoodstuffResponseSchema, 'name', many=True)

    _links = ma.Hyperlinks({
        'collection': {
            'href': ma.URLFor('ingredientlist', values=dict(dish_id='<dish_id>'))
        },
        'self': {
            'href': ma.URLFor('ingredientdetail', values=dict(dish_id='<dish_id>', id='<id>'))
        }
    })
