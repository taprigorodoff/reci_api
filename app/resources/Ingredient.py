from flask_restful import Resource
from sqlalchemy import exc
from models.db import Dish, Ingredient, Foodstuff

from resources.schema.ingredient.request import IngredientRequestSchema
from resources.schema.ingredient.response import IngredientResponseSchema
from common.response_http_codes import response_http_codes

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class IngredientList(MethodResource, Resource):

    @doc(tags=['ingredient'], description='Read dish ingredients.', responses=response_http_codes([200, 404]))
    def get(self, dish_id):
        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()

        return IngredientResponseSchema().dump(dish.ingredients, many=True), 200

    @doc(tags=['ingredient'], description='Create dish ingredient.', responses=response_http_codes([201, 400, 503]))
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    def post(self, dish_id, **kwargs):

        validation_errors = IngredientRequestSchema().validate(kwargs)

        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()
        stage_id = None
        if 'stage_id' in kwargs.keys():
            stage_id = kwargs['stage_id']

        for exist_ingredient in dish.ingredients:
            if exist_ingredient.foodstuff_id == kwargs['foodstuff_id'] and exist_ingredient.stage_id == stage_id:
                validation_errors.update(
                    {
                        'foodstuff_id': [
                            f'Already added to dish {dish_id}'
                        ]
                    }
                )
            for alternative_ingredient in exist_ingredient.alternatives:
                if alternative_ingredient.id == kwargs['foodstuff_id'] and exist_ingredient.stage_id == stage_id:
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

        ingredient = Ingredient()
        ingredient.dish_id = dish_id
        ingredient.foodstuff_id = kwargs['foodstuff_id']
        ingredient.amount = kwargs['amount']
        ingredient.unit_id = kwargs['unit_id']
        if 'pre_pack_type_id' in kwargs.keys():
            ingredient.pre_pack_type_id = kwargs['pre_pack_type_id']
        if 'stage_id' in kwargs.keys():
            ingredient.stage_id = kwargs['stage_id']

        if 'alternative_ids' in kwargs.keys():
            for alternative_id in kwargs['alternative_ids']:
                ingredient.alternatives.append(Foodstuff.query.get(alternative_id))

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return IngredientResponseSchema().dump(ingredient), 201


class IngredientDetail(MethodResource, Resource):
    @doc(tags=['ingredient'], description='Read dish ingredient.', responses=response_http_codes([200, 404]))
    def get(self, dish_id, id):
        ingredient = Ingredient.query.filter(Ingredient.id == id,
                                             Ingredient.dish_id == dish_id).first_or_404()

        return IngredientResponseSchema().dump(ingredient), 200

    @doc(tags=['ingredient'], description='Update dish ingredient.', responses=response_http_codes([200, 400, 503]))
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    def put(self, dish_id, id, **kwargs):

        dish = Dish.query.filter(Dish.id == dish_id).first_or_404()
        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()

        if int(ingredient.dish_id) != int(dish_id):
            return {
                       'messages': {
                           'ingredient_id': [
                               f'ingredient {id} is not connected with dish {dish_id}'
                           ]
                       }
                   }, 422

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
                for alternative_ingredient in exist_ingredient.alternatives:
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
            ingredient.alternatives = new_ingredient_alternatives
        else:
            ingredient.alternatives = []

        try:
            db.session.add(ingredient)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return IngredientResponseSchema().dump(ingredient), 200

    @doc(tags=['ingredient'], description='Delete dish ingredient.', responses=response_http_codes([204, 400, 404, 503]))
    def delete(self, dish_id, id):
        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        if int(ingredient.dish_id) != int(dish_id):
            return {
                       'messages': {
                           'ingredient_id': [
                               f'ingredient {id} is not connected with dish {dish_id}'
                           ]
                       }
                   }, 422

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
