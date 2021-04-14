from flask_restful import Resource
from sqlalchemy import exc
from models.db import Menu, MenuDish

from resources.schema.menu.request import MenuRequestSchema
from resources.schema.menu.response import MenuResponseSchema
from resources.schema.menudish.request import MenuDishRequestSchema
from resources.schema.menudish.response import MenuDishResponseSchema
from common.response_http_codes import response_http_codes

from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class MenuList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read all menus.', responses=response_http_codes([200]))
    def get(self):
        menus = Menu.query.order_by(Menu.id.desc()).all()

        return MenuResponseSchema().dump(menus, many=True), 200

    @doc(tags=['menu'], description='Create menu.', responses=response_http_codes([201, 400, 503]))
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
    @doc(tags=['menu'], description='Read menu.', responses=response_http_codes([200, 404]))
    def get(self, id):
        menu = Menu.query.filter(Menu.id == id).first_or_404()

        return MenuResponseSchema().dump(menu), 200

    @doc(tags=['menu'], description='Update menu.', responses=response_http_codes([200, 400, 404, 503]))
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

    @doc(tags=['menu'], description='Delete menu.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        menu = Menu.query.filter(Menu.id == id).first_or_404()

        uses = MenuDish.query.filter(MenuDish.menu_id == id).all()
        if uses:
            return {
                       'messages': {
                           'menu_id': [
                               'Menu already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(menu)
            db.session.delete(menu)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class MenuDishList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read all menu dishes.', responses=response_http_codes([200]))
    def get(self, menu_id):
        menu_dishes = MenuDish.query.filter(MenuDish.menu_id == menu_id).all()

        return MenuDishResponseSchema().dump(menu_dishes, many=True), 200

    @doc(tags=['menu'], description='Create dish ingredient.', responses=response_http_codes([201, 400, 422, 503]))
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    def post(self, menu_id, **kwargs):
        validation_errors = MenuDishRequestSchema().validate(kwargs)

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        menu = Menu.query.filter(Menu.id == menu_id).first()
        for exist_dish in menu.dishes:
            if exist_dish.id == kwargs['dish_id']:
                return {
                           'messages': {
                               'dish_id': [
                                   f'Already added to menu {menu_id}'
                               ]
                           }
                       }, 422

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
    @doc(tags=['menu'], description='Read menu dish.', responses=response_http_codes([200, 404]))
    def get(self, menu_id, id):
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        return MenuDishResponseSchema().dump(menu_dish), 200

    @doc(tags=['menu'], description='Update menu dish.', responses=response_http_codes([200, 400, 422, 503]))
    @use_kwargs(MenuDishRequestSchema(), location=('json'))
    def put(self, menu_id, id, **kwargs):
        validation_errors = MenuDishRequestSchema().validate(kwargs)

        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        menu = Menu.query.filter(Menu.id == menu_id).first_or_404()
        menu_dish = MenuDish.query.filter(MenuDish.menu_id == menu_id, MenuDish.id == id).first_or_404()

        if menu_dish.dish_id != kwargs['dish_id']:
            for exist_dish in menu.dishes:
                if exist_dish.id == kwargs['dish_id']:
                    return {
                           'messages': {
                               'dish_id': [
                                   f'Already added to menu {menu_id}'
                               ]
                           }
                       }, 422

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

    @doc(tags=['menu'], description='Delete menu dish.', responses=response_http_codes([204, 404, 503]))
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
    @doc(tags=['menu'], description='Read shopping list for menu.', responses=response_http_codes([200, 404]))
    def get(self, menu_id):
        menu = Menu.query.filter(Menu.id == menu_id).first_or_404()
        result = {}

        for menu_dish in menu.menu_dishes:
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


class MenuPrePackList(MethodResource, Resource):
    @doc(tags=['menu'], description='Read pre_pack list for menu.', responses=response_http_codes([200, 404]))
    def get(self, menu_id):
        menu = Menu.query.filter(Menu.id == menu_id).first_or_404()
        result = {}

        for menu_dish in menu.menu_dishes:
            dish_name = menu_dish.dish.name
            dish_pre_packs = result.get(dish_name, {})

            for ingredient in menu_dish.dish.ingredients:
                if ingredient.pre_pack_type:
                    foodstuff_name = ingredient.foodstuff.name
                    pre_pack_type = ingredient.pre_pack_type.name

                    tmp_foodstuffs = dish_pre_packs.get(pre_pack_type, {})
                    foodstuff = tmp_foodstuffs.get(foodstuff_name, {})

                    if foodstuff:
                        was_update = False
                        for need in foodstuff:
                            if need['unit'] == ingredient.unit.name:
                                need['amount'] += ingredient.amount / ingredient.dish.portion * menu_dish.portion
                                was_update = True

                        if not was_update:
                            foodstuff.append(
                                {
                                    'amount': ingredient.amount / ingredient.dish.portion * menu_dish.portion,
                                    'unit': ingredient.unit.name
                                }
                            )
                    else:
                        foodstuff = {
                            foodstuff_name: [
                                {
                                    'amount': ingredient.amount / ingredient.dish.portion * menu_dish.portion,
                                    'unit': ingredient.unit.name
                                }
                            ]
                        }
                        tmp_foodstuffs.update(foodstuff)

                    dish_pre_packs.update({pre_pack_type: tmp_foodstuffs})

            if dish_pre_packs:
                dish_pre_packs.update({'portion': menu_dish.portion})
                result.update({dish_name: dish_pre_packs})

        return result, 200
