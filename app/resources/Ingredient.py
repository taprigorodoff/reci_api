from flask_restful import Resource
from sqlalchemy import exc
from models.db import Dish, Ingredient, Foodstuff

from resources.schema.ingredient.request import IngredientRequestSchema

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class IngredientList(MethodResource, Resource):
    @doc(tags=['ingredient'], description='Create dish ingredient.')
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

    @doc(tags=['ingredient'], description='Read dish ingredients.')
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
    @doc(tags=['ingredient'], description='Read dish ingredient.')
    def get(self, dish_id, id):
        ri = Ingredient.query.filter(Ingredient.id == id,
                                           Ingredient.dish_id == dish_id).first_or_404()
        return ri.as_json(), 200

    @doc(tags=['ingredient'], description='Update dish ingredient.')
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

    @doc(tags=['ingredient'], description='Delete dish ingredient.')
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

