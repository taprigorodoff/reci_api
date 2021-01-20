from flask_restful import Resource, reqparse
from sqlalchemy import exc
from resources.models import Ingredient, DStoreSection
from app import db


class IngredientList(Resource):
    def get(self):
        r = Ingredient.query.order_by(Ingredient.id.desc()).all()
        results = {}

        for ob in r:
            ingredient = ob.as_json()
            store_section = ingredient.pop('store_section', 'other')['name']
            tmp_ingredients = results.get(store_section, [])
            tmp_ingredients.append(ingredient)
            results.update({store_section: tmp_ingredients})

        return results, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('store_section_id')
        args = parser.parse_args()

        ingredient = Ingredient()
        ingredient.name = args['name']
        ingredient.store_section_id = args['store_section_id']

        try:
            db.session.add(ingredient)
            db.session.commit()
            return ingredient.as_json(), 201
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 400


class IngredientDetail(Resource):
    def get(self, id):
        r = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        return r.as_json(), 200

    def put(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('store_section_id')
        args = parser.parse_args()

        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        ingredient.name = args['name']
        ingredient.store_section_id = args['store_section_id']

        try:
            db.session.add(ingredient)
            db.session.commit()
            return ingredient.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 400


class StoreSectionList(Resource):
    def get(self):
        r = DStoreSection.query.order_by(DStoreSection.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    def post(self):
        # todo проверить на существование
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()

        section = DStoreSection()
        section.name = args['name']
        db.session.add(section)
        db.session.commit()
        return section.as_json(), 201


class StoreSectionDetail(Resource):
    def get(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        return r.as_json(), 200

    def put(self, id):
        #todo проверить на существование
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        section = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        section.name = args['name']

        db.session.add(section)
        db.session.commit()
        return section.as_json(), 201

    def delete(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.store_section_id == id).all()
        if ingredients:
            return {
                       "code": 0,  # todo придумать коды
                       "message": "store section already use"
                   }, 422

        db.session.add(r)
        db.session.delete(r)
        db.session.commit()

        return '', 204
