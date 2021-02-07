from flask_restful import Resource, abort
from sqlalchemy import exc
from resources.models import Recipe
from resources.models import Menu, MenuDish
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields, ValidationError, validate, types
import typing


class MenuRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=100))

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)


class MenuList(MethodResource, Resource):
    @doc(description='Read all menus.')
    def get(self):
        r = Menu.query.order_by(Menu.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create menu.')
    @use_kwargs(MenuRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = MenuRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        menu = Menu()
        menu.name = kwargs['name']

        try:
            db.session.add(menu)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return menu.as_json(), 200


class MenuDetail(MethodResource, Resource):
    @doc(description='Read menu.')
    def get(self, id):
        r = Menu.query.filter(Menu.id == id).first_or_404()
        return r.as_json(), 200

    @doc(description='Update menu.')
    @use_kwargs(MenuRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = MenuRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        menu = Menu.query.filter(Menu.id == id).first_or_404()
        menu.name = kwargs['name']

        try:
            db.session.add(menu)
            db.session.commit()
            return menu.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(description='Delete menu.')
    def delete(self, id):
        r = Menu.query.filter(Menu.id == id).first_or_404()

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class MenuDishRequestSchema(Schema):
    recipe_id = fields.Integer(required=True, description="API type of awesome API")
    portion = fields.Integer(required=True, description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:
        validation_errors = {}
        recipe = Recipe.query.filter(Recipe.id == data['recipe_id']).first()
        if not recipe:
            validation_errors.update(
                {
                    'recipe_id': [
                        'Bad choice for recipe_id'
                    ]
                }
            )

        return validation_errors


class MenuDishList(MethodResource, Resource):
    @doc(description='Read all menu dishes.')
    def get(self, menu_id):
        r = MenuDish.query.filter(MenuDish.menu_id == menu_id).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create recipe ingredient.')
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    # todo документировать коды ошибок
    def post(self, menu_id, **kwargs):

        validation_errors = MenuDishRequestSchema().validate(kwargs)

        menu = Menu.query.filter(Menu.id == menu_id).first()
        for exist_dish in menu.dishes:
            if exist_dish.id == kwargs['recipe_id']:
                validation_errors.update(
                    {
                        'recipe_id': [
                            f'Already added to menu {menu_id}'
                        ]
                    }
                )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        menu_dish = MenuDish()
        menu_dish.menu_id = menu_id
        menu_dish.recipe_id = kwargs['recipe_id']
        menu_dish.portion = kwargs['portion']

        try:
            db.session.add(menu_dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return menu_dish.as_json(), 200

class MenuDishDetail(MethodResource, Resource):
    @doc(description='Read menu dish.')
    def get(self, menu_id, id):
        r = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()
        return r.as_json(), 200

    @doc(description='Update menu dish.')
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    def put(self, menu_id, id, **kwargs):
        validation_errors = MenuDishRequestSchema().validate(kwargs)

        menu = Menu.query.filter(Menu.id == menu_id).first_or_404()
        for exist_dish in menu.dishes:
            if exist_dish.id == kwargs['recipe_id']:
                validation_errors.update(
                    {
                        'recipe_id': [
                            f'Already added to menu {menu_id}'
                        ]
                    }
                )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        menu_dish.recipe_id = kwargs['recipe_id']
        menu_dish.portion = kwargs['portion']

        try:
            db.session.add(menu_dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return menu_dish.as_json(), 200

    @doc(description='Delete menu dish.')
    def delete(self, menu_id, id):
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        try:
            db.session.add(menu_dish)
            db.session.delete(menu_dish)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503
