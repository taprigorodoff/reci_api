from flask_restful import abort

from models.db import Dish, Ingredient, Foodstuff
from models.db import DCategory, DStage, DUnit, DPrePackType
from app import db, cache

from marshmallow import Schema, fields, ValidationError, validate, types
import typing
import json


class DishFilterSchema(Schema):
    cook_time = fields.Integer(required=False, description="API type of awesome API")
    all_time = fields.Integer(required=False, description="API type of awesome API")
    category_id = fields.Integer(required=False, description="API type of awesome API")
    foodstuff_ids = fields.List(cls_or_instance=fields.Integer(), required=False, description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:

        cached_category = cache.get('view//category')
        if cached_category:
            raw = json.loads(cached_category.response[0])
            category_ids = [unit['id'] for unit in raw]
        else:
            category_ids = [category.id for category in db.session.query(DCategory.id).all()]

        validation_errors = {}
        if 'category_id' in data.keys():
            if data['category_id'] not in category_ids:
                validation_errors.update(
                    {
                        'categories': [
                            'bad choice for category_id'
                        ]
                    }
                )

        return validation_errors
