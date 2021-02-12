from flask_restful import abort
from marshmallow import Schema, fields, ValidationError, validate, types

from models.db import Dish, Ingredient, Foodstuff
from models.db import DStoreSection
from app import db, cache

import typing
import json


class FoodstuffRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=50))
    store_section_id = fields.Integer(required=True, description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:

        cached_store_section = cache.get('view//store_section')
        if cached_store_section:
            raw = json.loads(cached_store_section.response[0])
            store_section_ids = [cat['id'] for cat in raw]
        else:
            store_section_ids = [cat.id for cat in db.session.query(DStoreSection.id).all()]

        validation_errors = {}
        if data['store_section_id'] not in store_section_ids:
            validation_errors.update(
                {
                    'store_section_id': [
                        'Bad choice for store_section_id'
                    ]
                }
            )
        if Foodstuff.query.filter(Foodstuff.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors
