from flask_restful import Resource, abort
from sqlalchemy import exc
from models.db import Foodstuff, DStoreSection, Ingredient
from resources.schema.foodstuff.request import FoodstuffRequestSchema
from resources.schema.foodstuff.filter import FoodstuffFilterSchema
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class FoodstuffList(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read all Foodstuffs.')
    @use_kwargs(FoodstuffFilterSchema(), location=('query'))
    def get(self, **kwargs):

        validation_errors = FoodstuffFilterSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        if 'store_section_id' in kwargs.keys():
            foodstuffs = Foodstuff.query.filter(Foodstuff.store_section_id == kwargs['store_section_id'])\
                .order_by(Foodstuff.name.desc()).all()
        else:
            foodstuffs = Foodstuff.query.order_by(Foodstuff.store_section_id.desc()).all()

        return [foodstuff.as_json() for foodstuff in foodstuffs], 200

    @doc(tags=['foodstuff'], description='Create foodstuff.')
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        foodstuff = Foodstuff()
        foodstuff.name = kwargs['name']
        foodstuff.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(foodstuff)
            db.session.commit()
            return foodstuff.as_json(), 201
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class FoodstuffDetail(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read foodstuff.')
    def get(self, id):
        r = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['foodstuff'], description='Update foodstuff.')
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        foodstuff = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()
        foodstuff.name = kwargs['name']
        foodstuff.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(foodstuff)
            db.session.commit()
            return foodstuff.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['foodstuff'], description='Delete foodstuff.')
    def delete(self, id):
        r = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()

        use_ingredients = Ingredient.query.filter(Ingredient.foodstuff_id == id).all()
        if use_ingredients:
            return {
                       "message": "ingredient already use in dishes"
                   }, 422

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503
