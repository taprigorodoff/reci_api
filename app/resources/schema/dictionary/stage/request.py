from flask_restful import abort
from models.db import DStage
from marshmallow import Schema, fields, ValidationError, validate, types
import typing


class StageRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=50))

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, messages=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:
        validation_errors = {}
        if DStage.query.filter(DStage.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors
