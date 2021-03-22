from flask_restful import abort
from marshmallow import Schema, fields, ValidationError, validate, types

from models.db import Dish, Ingredient, Foodstuff
from models.db import DStoreSection
from app import db, cache

import typing
import json


class FoodstuffRequestSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(max=50))
    store_section_id = fields.Integer(required=True)

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, messages=error.messages)

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
            store_section_ids = [section['id'] for section in raw]
        else:
            store_section_ids = [section.id for section in db.session.query(DStoreSection.id).all()]

        validation_errors = {}
        if data['store_section_id'] not in store_section_ids:
            validation_errors.update(
                {
                    'store_section_id': [
                        'Bad choice for store_section_id'
                    ]
                }
            )
        return validation_errors
