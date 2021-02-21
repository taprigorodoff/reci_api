from flask_restful import Resource
from sqlalchemy import exc
from models.db import Menu, MenuDish

from resources.schema.menu.request import MenuRequestSchema
from resources.schema.menu.response import MenuResponseSchema
from resources.schema.menudish.request import MenuDishRequestSchema
from resources.schema.menudish.response import MenuDishResponseSchema

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class MenuList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read all menus.')
    def get(self):
        menus = Menu.query.order_by(Menu.id.desc()).all()

        return MenuResponseSchema().dump(menus, many=True), 200

    @doc(tags=['menu'], description='Create menu.')
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

        return MenuResponseSchema().dump(menu), 201


class MenuDetail(MethodResource, Resource):
    @doc(tags=['menu'], description='Read menu.')
    def get(self, id):
        menu = Menu.query.filter(Menu.id == id).first_or_404()

        return MenuResponseSchema().dump(menu), 200

    @doc(tags=['menu'], description='Update menu.')
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return MenuResponseSchema().dump(menu), 200

    @doc(tags=['menu'], description='Delete menu.')
    def delete(self, id):
        r = Menu.query.filter(Menu.id == id).first_or_404()

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class MenuDishList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read all menu dishes.')
    def get(self, menu_id):
        menu_dishes = MenuDish.query.filter(MenuDish.menu_id == menu_id).all()

        return MenuDishResponseSchema().dump(menu_dishes, many=True), 200

    @doc(tags=['menu'], description='Create dish ingredient.')
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    # todo документировать коды ошибок
    def post(self, menu_id, **kwargs):

        validation_errors = MenuDishRequestSchema().validate(kwargs)

        menu = Menu.query.filter(Menu.id == menu_id).first()
        for exist_dish in menu.dishes:
            if exist_dish.id == kwargs['dish_id']:
                validation_errors.update(
                    {
                        'dish_id': [
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
        menu_dish.dish_id = kwargs['dish_id']
        menu_dish.portion = kwargs['portion']

        try:
            db.session.add(menu_dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return MenuDishResponseSchema().dump(menu_dish), 201


class MenuDishDetail(MethodResource, Resource):
    @doc(tags=['menu'], description='Read menu dish.')
    def get(self, menu_id, id):
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()
        
        return MenuDishResponseSchema().dump(menu_dish), 200

    @doc(tags=['menu'], description='Update menu dish.')
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    def put(self, menu_id, id, **kwargs):
        validation_errors = MenuDishRequestSchema().validate(kwargs)

        menu = Menu.query.filter(Menu.id == menu_id).first_or_404()
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        if menu_dish.dish_id != kwargs['dish_id']:
            for exist_dish in menu.dishes:
                if exist_dish.id == kwargs['dish_id']:
                    validation_errors.update(
                        {
                            'dish_id': [
                                f'Already added to menu {menu_id}'
                            ]
                        }
                    )

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        menu_dish.dish_id = kwargs['dish_id']
        menu_dish.portion = kwargs['portion']

        try:
            db.session.add(menu_dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return MenuDishResponseSchema().dump(menu_dish), 200

    @doc(tags=['menu'], description='Delete menu dish.')
    def delete(self, menu_id, id):
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        try:
            db.session.add(menu_dish)
            db.session.delete(menu_dish)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class MenuShoppingList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read shopping list for menu.')
    def get(self, menu_id):
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id).first_or_404()
        result = {}

        for ingredient in menu_dish.dish.ingredients:

            good_name = ingredient.foodstuff.name
            if ingredient.alternatives:
                good_name += '/' + '/'.join([i.name for i in ingredient.alternatives])

            store_section = ingredient.foodstuff.store_section.name
            tmp_goods = result.get(store_section, {})
            good = tmp_goods.get(good_name, {})

            if good:
                was_update = False
                for need in good:
                    if need['unit'] == ingredient.unit.name:
                        need['amount'] += ingredient.amount / ingredient.dish.portion * menu_dish.portion
                        was_update = True

                if not was_update:
                    good.append(
                        {
                            'amount': ingredient.amount / ingredient.dish.portion * menu_dish.portion,
                            'unit': ingredient.unit.name
                        }
                    )
            else:
                good = {
                    good_name: [
                        {
                            'amount': ingredient.amount / ingredient.dish.portion * menu_dish.portion,
                            'unit': ingredient.unit.name
                        }
                    ]
                }
                tmp_goods.update(good)

            result.update({store_section: tmp_goods})

        return result, 200
