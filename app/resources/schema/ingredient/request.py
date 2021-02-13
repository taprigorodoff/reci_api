from flask_restful import abort

from models.db import Dish, Ingredient, Foodstuff
from models.db import DCategory, DStage, DUnit, DPrePackType
from app import db, cache

from marshmallow import Schema, fields, ValidationError, validate, types

import typing
import json


class IngredientRequestSchema(Schema):
    foodstuff_id = fields.Integer(required=True, description="API type of awesome API")
    amount = fields.Float(required=True, description="API type of awesome API")
    unit_id = fields.Integer(required=True, description="API type of awesome API")
    pre_pack_type_id = fields.Integer(required=False, description="API type of awesome API") #nullable=True,
    stage_id = fields.Integer(required=False, description="API type of awesome API") #nullable=True,
    alternative_ids = fields.List(cls_or_instance=fields.Integer(),
                             required=False,
                             description="API type of awesome API") #nullable=True,

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:

        cached_unit = cache.get('view//unit')
        if cached_unit:
            raw = json.loads(cached_unit.response[0])
            unit_ids = [unit['id'] for unit in raw]
        else:
            unit_ids = [cat.id for cat in db.session.query(DUnit.id).all()]

        pre_pack_type_ids = [cat.id for cat in db.session.query(DPrePackType.id).all()]  # todo кэш
        stage_ids = [cat.id for cat in db.session.query(DStage.id).all()]  # todo кэш

        # todo посмотреть (в джанго?) куда убрать влидацию
        validation_errors = {}
        if data['unit_id'] not in unit_ids:
            validation_errors.update(
                {
                    'unit_id': [
                        'Bad choice for unit_id'
                    ]
                }
            )

        if 'pre_pack_type_id' in data.keys() and data['pre_pack_type_id'] not in pre_pack_type_ids:
            validation_errors.update(
                {
                    'pre_pack_type_id': [
                        'Bad choice for pre_pack_type_id'
                    ]
                }
            )

        if 'stage_id' in data.keys() and data['stage_id'] not in stage_ids:
            validation_errors.update(
                {
                    'stage_id': [
                        'Bad choice for stage_id'
                    ]
                }
            )

        foodstuff = Foodstuff.query.filter(Foodstuff.id == data['foodstuff_id']).first()
        if not foodstuff:
            validation_errors.update(
                {
                    'foodstuff_id': [
                        'Bad choice for foodstuff_id'
                    ]
                }
            )
        if 'alternative_ids' in data.keys():
            for alternative_id in data['alternative_ids']:
                foodstuff = Foodstuff.query.filter(Foodstuff.id == alternative_id).first()

                if not foodstuff:
                    validation_errors.update(
                        {
                            'alternative_id': [
                                'Bad choice for alternative_id'
                            ]
                        }
                    )

        return validation_errors
