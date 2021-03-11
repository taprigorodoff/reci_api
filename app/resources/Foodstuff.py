from flask import request
from flask_restful import Resource
from sqlalchemy import exc
from models.db import Foodstuff, DStoreSection, Ingredient
from resources.schema.foodstuff.request import FoodstuffRequestSchema
from resources.schema.foodstuff.filter import FoodstuffFilterSchema
from resources.schema.foodstuff.response import FoodstuffsResponseSchema, FoodstuffResponseSchema
from common.response_http_codes import response_http_codes
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class FoodstuffList(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read all Foodstuffs.', responses=response_http_codes([200, 400]))
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

        current_full_path = request.full_path
        result = {
            'data': FoodstuffsResponseSchema().dump(foodstuffs),
            '_links': {
                'self': {
                    'href': current_full_path
                }
            }
        }
        return result, 200

    @doc(tags=['foodstuff'], description='Create foodstuff.', responses=response_http_codes([201, 400, 503]))
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)

        if Foodstuff.query.filter(Foodstuff.name == kwargs["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )

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
            return FoodstuffResponseSchema().dump(foodstuff), 201
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class FoodstuffDetail(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read foodstuff.', responses=response_http_codes([200, 404]))
    def get(self, id):
        foodstuff = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()
        return FoodstuffResponseSchema().dump(foodstuff), 200

    @doc(tags=['foodstuff'], description='Update foodstuff.', responses=response_http_codes([200, 400, 404, 503]))
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)
        foodstuff = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()

        if foodstuff.name != kwargs["name"]:
            if Foodstuff.query.filter(Foodstuff.name == kwargs["name"]).first():
                validation_errors.update(
                    {
                        'name': [
                            'Already exist'
                        ]
                    }
                )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        foodstuff.name = kwargs['name']
        foodstuff.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(foodstuff)
            db.session.commit()
            return FoodstuffResponseSchema().dump(foodstuff), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['foodstuff'], description='Delete foodstuff.', responses=response_http_codes([204, 404, 422, 503]))
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
