from flask_restful import abort

from marshmallow import Schema, fields, ValidationError, validate


class MenuRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=100))

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, messages=error.messages)
