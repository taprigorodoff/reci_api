from flask_restful import Resource, abort
from flask import send_from_directory
from sqlalchemy import exc
from resources.models import Dish, Ingredient, Foodstuff
from resources.models import DCategory, DStage, DUnit, DPrePackType
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
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


class DishList(MethodResource, Resource):
    @doc(description='Read all dishes.')
    def get(self):
        '''
        Get method represents a GET API method
        '''
        r = Dish.query.order_by(Dish.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create dish.')
    @use_kwargs(DishRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = DishRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        dish = Dish()
        dish.name = kwargs['name']
        dish.description = kwargs['description']
        dish.portion = kwargs['portion']
        dish.cook_time = kwargs['cook_time']
        dish.all_time = kwargs['all_time']
        for category_id in kwargs['categories']:
            category = DCategory.query.get(category_id)
            if category:
                dish.categories.append(category)

        try:
            db.session.add(dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return dish.as_json(), 200


class DishDetail(MethodResource, Resource):
    @doc(description='Read dish.')
    def get(self, id):
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        return dish.as_full_json(), 200

    @doc(description='Update dish.')
    @use_kwargs(DishRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = DishRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        dish.name = kwargs['name']
        dish.description = kwargs['description']
        dish.portion = kwargs['portion']
        dish.cook_time = kwargs['cook_time']
        dish.all_time = kwargs['all_time']
        for category_id in kwargs['categories']:
            category = DCategory.query.get(category_id)
            if category:
                dish.categories.append(category)

        try:
            db.session.add(dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return dish.as_json(), 200

    @doc(description='Delete dish.')
    def delete(self, id):
        r = Dish.query.filter(Dish.id == id).first_or_404()
        db.session.add(r)
        db.session.delete(r)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return '', 204


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

        unit_ids = [cat.id for cat in db.session.query(DUnit.id).all()]  # todo кэш
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

        
class IngredientList(MethodResource, Resource):
    @doc(description='Create dish ingredient.')
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    #todo документировать коды ошибок
    def post(self, dish_id, **kwargs):

        validation_errors = IngredientRequestSchema().validate(kwargs)

        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()

        for exist_ingredient in dish.ingredients:
            if exist_ingredient.foodstuff_id == kwargs['foodstuff_id']:
                validation_errors.update(
                    {
                        'foodstuff_id': [
                            f'Already added to dish {dish_id}'
                        ]
                    }
                )
            for alternative_ingredient in exist_ingredient.ingredient_alternatives:
                if alternative_ingredient.id == kwargs['foodstuff_id']:
                    validation_errors.update(
                        {
                            'foodstuff_id': [
                                f'Already added as alternative to dish {dish_id}'
                            ]
                        }
                    )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        ri = Ingredient()
        ri.dish_id = dish_id
        ri.foodstuff_id = kwargs['foodstuff_id']
        ri.amount = kwargs['amount']
        ri.unit_id = kwargs['unit_id']
        if 'pre_pack_type_id' in kwargs.keys():
            ri.pre_pack_type_id = kwargs['pre_pack_type_id']
        if 'stage_id' in kwargs.keys():
            ri.stage_id = kwargs['stage_id']

        if 'alternative_ids' in kwargs.keys():
            for alternative_id in kwargs['alternative_ids']:
                ri.ingredient_alternatives.append(Foodstuff.query.get(alternative_id))

        db.session.add(ri)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return ri.as_json(), 200

    @doc(description='Read dish ingredients.')
    def get(self, dish_id):
        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()
        ingredients = {}
        for ob in dish.ingredients:
            ingredient = ob.as_json()

            stage_name = ingredient.pop('stage')

            tmp_ingredients = ingredients.get(stage_name, [])
            tmp_ingredients.append(ingredient)
            ingredients.update({stage_name: tmp_ingredients})

        return ingredients, 200


class IngredientDetail(MethodResource, Resource):
    @doc(description='Read dish ingredient.')
    def get(self, dish_id, id):
        ri = Ingredient.query.filter(Ingredient.id == id,
                                           Ingredient.dish_id == dish_id).first_or_404()
        return ri.as_json(), 200

    @doc(description='Update dish ingredient.')
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    def put(self, dish_id, id, **kwargs):

        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()
        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()

        if not dish:
            return {
                       'messages': f'dish {dish_id} is not found'
                   }, 404

        if ingredient.dish_id != dish_id:
            return {
                       'messages': f'ingredient {id} is not connected with dish {dish_id}'
                   }, 400

        validation_errors = IngredientRequestSchema().validate(kwargs)

        if ingredient.foodstuff_id != kwargs['foodstuff_id']:

            for exist_ingredient in dish.ingredients:
                if exist_ingredient.foodstuff_id == kwargs['foodstuff_id']:
                    validation_errors.update(
                        {
                            'foodstuff_id': [
                                f'Already added to dish {dish_id}'
                            ]
                        }
                    )
                for alternative_ingredient in exist_ingredient.ingredient_alternatives:
                    if alternative_ingredient.id == kwargs['foodstuff_id']:
                        validation_errors.update(
                            {
                                'foodstuff_id': [
                                    f'Already added as alternative to dish {dish_id}'
                                ]
                            }
                        )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        ingredient.foodstuff_id = kwargs['foodstuff_id']
        ingredient.amount = kwargs['amount']
        ingredient.unit_id = kwargs['unit_id']
        if 'pre_pack_type_id' in kwargs.keys():
            ingredient.pre_pack_type_id = kwargs['pre_pack_type_id']
        else:
            ingredient.pre_pack_type_id = None
        if 'stage_id' in kwargs.keys():
            ingredient.stage_id = kwargs['stage_id']
        else:
            ingredient.stage_id = None

        if 'alternative_ids' in kwargs.keys():
            new_ingredient_alternatives = []
            for alternative_id in kwargs['alternative_ids']:
                new_ingredient_alternatives.append(Foodstuff.query.get(alternative_id))
            ingredient.ingredient_alternatives = new_ingredient_alternatives
        else:
            ingredient.ingredient_alternatives = []

        db.session.add(ingredient)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return ingredient.as_json(), 201

    @doc(description='Delete dish ingredient.')
    def delete(self, dish_id, id):
        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        if ingredient.dish_id != dish_id:
            return {
                       'messages': f'ingredient {id} is not connected with dish {dish_id}'
                   }, 400

        try:
            db.session.add(ingredient)
            db.session.delete(ingredient)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503


class DishImg(MethodResource, Resource):
    @doc(description='Read dish img.')
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
