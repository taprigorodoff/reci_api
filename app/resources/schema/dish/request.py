from flask_restful import abort

from models.db import DCategory, DStage, DUnit, DPrePackType
from app import db, cache

from marshmallow import Schema, fields, ValidationError, validate, types
import typing
import json


class DishRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(max=100))
    description = fields.String(required=True)
    portion = fields.Integer(required=True, description='The number of servings for which the recipe is calculated')
    cook_time = fields.Integer(required=True, description='Active cooking time, in minutes')
    all_time = fields.Integer(required=True, description='All cooking time, in minutes')
    categories = fields.List(cls_or_instance=fields.Integer(), required=True)

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, messages=error.messages)

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
        for category_id in data['categories']:
            if category_id not in category_ids:
                validation_errors.update(
                    {
                        'categories': [
                            'bad choice for category_id'
                        ]
                    }
                )

        return validation_errors
