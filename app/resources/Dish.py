from flask_restful import Resource
from sqlalchemy import exc
from flask import send_from_directory, request

from models.db import Dish, Ingredient, Foodstuff
from models.db import DCategory, DStage, DUnit, DPrePackType
from resources.schema.dish.request import DishRequestSchema
from resources.schema.dish.filter import DishFilterSchema
from resources.schema.dish.response import DishesResponseSchema, DishResponseSchema

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class DishList(MethodResource, Resource):
    @doc(tags=['dish'], description='Read all dishes.')
    @use_kwargs(DishFilterSchema(), location=('query'))
    def get(self, **kwargs):
        '''
        Get method represents a GET API method
        '''
        validation_errors = DishFilterSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        page = kwargs.pop('page')
        per_page = 5

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
            query = """SELECT DISTINCT dish.id 
                       FROM dish
                       JOIN dish_categories dc ON dc.dish_id = dish.id
                       FULL JOIN ingredient i ON i.dish_id = dish.id
                       WHERE """ + condition

            result = db.engine.execute(query)

            dish_ids = [row[0] for row in result]
            dishes = Dish.query.filter(Dish.id.in_(dish_ids)).order_by(Dish.name.desc()).paginate(page, per_page, False)
        else:
            dishes = Dish.query.order_by(Dish.name.desc()).paginate(page, per_page, False)

        current_full_path = request.full_path
        if page < dishes.pages:
            next_page = current_full_path.replace('page={}'.format(page), 'page={}'.format(dishes.page + 1))
        else:
            next_page = None
        last_page = current_full_path.replace('page={}'.format(page), 'page={}'.format(dishes.pages))

        result = {
            'data': DishesResponseSchema().dump(dishes.items),
            'pagination': {
                'total': dishes.total,
                'page': dishes.page,
                'pages': dishes.pages,
            },
            '_links': {
                'self': {
                    'href': current_full_path
                },
                'next': {
                    'href': next_page
                },
                'last': {
                    'href': last_page
                }
            }
        }
        return result, 200

    @doc(tags=['dish'], description='Create dish.')
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
    @doc(tags=['dish'], description='Read dish.')
    def get(self, id):
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        return DishResponseSchema().dump(dish), 200

    @doc(tags=['dish'], description='Update dish.')
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

    @doc(tags=['dish'], description='Delete dish.')
    def delete(self, id):
        dish = Dish.query.filter(Dish.id == id).first_or_404()
        if dish.ingredients:
            return {
                       'messages': {
                           'dish_id': [
                               'Dish has ingredients'
                           ]
                       }
                   }, 400

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
    @doc(tags=['dish'], description='Read dish img.')
    def get(self, dish_id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(dish_id))
        return response
