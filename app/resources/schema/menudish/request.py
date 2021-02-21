from flask_restful import abort

from models.db import Dish

from marshmallow import Schema, fields, ValidationError, validate, types

import typing


class MenuDishRequestSchema(Schema):
    dish_id = fields.Integer(required=True, description="API type of awesome API")
    portion = fields.Integer(required=True, description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
            self,
            data: typing.Mapping,
            *,
            many: typing.Optional[bool] = None,
            partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:
        validation_errors = {}
        dish = Dish.query.filter(Dish.id == data['dish_id']).first()
        if not dish:
            validation_errors.update(
                {
                    'dish_id': [
                        'Bad choice for dish_id'
                    ]
                }
            )

        return validation_errors
