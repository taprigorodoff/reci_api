from flask_restful import abort

from models.db import Dish, Ingredient, Foodstuff
from models.db import DCategory, DStage, DUnit, DPrePackType
from app import db

from marshmallow import Schema, fields, ValidationError, validate, types
import typing


class DishRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=100))
    description = fields.String(required=True, description="API type of awesome API")
    portion = fields.Integer(required=True, description="API type of awesome API")
    cook_time = fields.Integer(required=True, description="API type of awesome API")
    all_time = fields.Integer(required=True, description="API type of awesome API")
    categories = fields.List(cls_or_instance=fields.Integer(),
                             required=True,
                             description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:
        categories_ids = [cat.id for cat in db.session.query(DCategory.id).all()]  # todo кэш
        validation_errors = {}
        for category_id in data['categories']:
            if category_id not in categories_ids:
                validation_errors.update(
                    {
                        'categories': [
                            'bad choice for category_id'
                        ]
                    }
                )
        if Dish.query.filter(Dish.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors
