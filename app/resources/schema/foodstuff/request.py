from flask_restful import abort

from models.db import Dish, Ingredient, Foodstuff
from models.db import DStoreSection
from app import db

from marshmallow import Schema, fields, ValidationError, validate, types
import typing


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
        store_section_ids = [cat.id for cat in db.session.query(DStoreSection.id).all()]  # todo кэш
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
