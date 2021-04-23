from flask_restful import Resource
from sqlalchemy import exc
from flask import send_from_directory, request

from models.db import Dish, Ingredient, Foodstuff
from models.db import DCategory, DStage, DUnit, DPrePackType
from resources.schema.dish.request import DishRequestSchema
from resources.schema.dish.filter import DishFilterSchema
from resources.schema.dish.response import DishesResponseSchema, DishResponseSchema
from common.response_http_codes import response_http_codes

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class DishList(MethodResource, Resource):
    @doc(tags=['dish'], description='Read all dishes.', responses=response_http_codes([200, 400, 503]))
    @use_kwargs(DishFilterSchema(), location=('query'))
    def get(self, **kwargs):
        validation_errors = DishFilterSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        if kwargs:
            conditions = []
            if 'cook_time' in kwargs.keys():
                conditions.append('cook_time <= {}'.format(kwargs['cook_time']))
            if 'all_time' in kwargs.keys():
                conditions.append('all_time <= {}'.format(kwargs['all_time']))
            if 'category_id' in kwargs.keys():
                conditions.append('category_id = {}'.format(kwargs['category_id']))
            if 'foodstuff_ids' in kwargs.keys():
                conditions.append('foodstuff_id in ({})'.format(','.join(str(f) for f in kwargs['foodstuff_ids'])))

            condition = ' AND '.join(str(c) for c in conditions)
            requested_page = ' LIMIT {} OFFSET {}'.format(kwargs['per_page'], kwargs['per_page'] * kwargs['page'])

            query = """SELECT DISTINCT dish.id 
                       FROM dish
                       JOIN dish_categories dc ON dc.dish_id = dish.id
                       FULL JOIN ingredient i ON i.dish_id = dish.id
                       WHERE """ + condition + requested_page

            try:
                result = db.engine.execute(query)
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                return {
                           'messages': e.args
                       }, 503

            dish_ids = [row[0] for row in result]
            dishes = Dish.query.filter(Dish.id.in_(dish_ids)).order_by(Dish.name.desc()).all()
        else:
            dishes = Dish.query.order_by(Dish.name.desc()).all()

        kwargs['page'] += 1
        next_page = request.path + '?' + '&'.join('{}={}'.format(key, kwargs[key]) for key in kwargs)
        if kwargs['page'] <= 2:
            prev_page = None
        else:
            kwargs['page'] -= 2
            prev_page = request.path + '?' + '&'.join('{}={}'.format(key, kwargs[key]) for key in kwargs)

        result = {
            'data': DishesResponseSchema().dump(dishes),
            'pagination': {
                'page': kwargs['page']
            },
            '_links': {
                'self': {
                    'href': request.full_path
                },
                'prev': {
                    'href': prev_page
                },
                'next': {
                    'href': next_page
                }
            }
        }
        return result, 200

    @doc(tags=['dish'], description='Create dish.', responses=response_http_codes([201, 400, 503]))
    @use_kwargs(DishRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = DishRequestSchema().validate(kwargs)
        if Dish.query.filter(Dish.name == kwargs["name"]).first():
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

        return DishResponseSchema().dump(dish), 201


class DishDetail(MethodResource, Resource):
    @doc(tags=['dish'], description='Read dish.', responses=response_http_codes([200, 404]))
    def get(self, id):
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        return DishResponseSchema().dump(dish), 200

    @doc(tags=['dish'], description='Update dish.', responses=response_http_codes([200, 400, 404, 503]))
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

        new_category_list = []
        for category_id in kwargs['categories']:
            new_category_list.append(DCategory.query.get(category_id))
        dish.categories = new_category_list

        try:
            db.session.add(dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return DishResponseSchema().dump(dish), 200

    @doc(tags=['dish'], description='Delete dish.', responses=response_http_codes([204, 400, 404, 503]))
    def delete(self, id):
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        if dish.ingredients:
            return {
                       'messages': {
                           'dish_id': [
                               'Dish has ingredients'
                           ]
                       }
                   }, 422

        try:
            db.session.add(dish)
            db.session.delete(dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class DishImg(MethodResource, Resource):
    @doc(tags=['dish'], description='Read dish img.', responses=response_http_codes([200, 404]))
    def get(self, dish_id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(dish_id))
        return response, 200
