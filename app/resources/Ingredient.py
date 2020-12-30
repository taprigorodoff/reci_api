from flask_restful import Resource, reqparse
from resources.models import Ingredient, DStoreSection
from app import db

class IngredientList(Resource):
    def get(self):
        r = Ingredient.query.order_by(Ingredient.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200


class IngredientDetail(Resource):
    def get(self, id):
        r = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        return r.as_json(), 200


class StoreSectionList(Resource):
    def get(self):
        r = DStoreSection.query.order_by(DStoreSection.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    def post(self):
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
        parser = reqparse.RequestParser()
        parser.add_argument('name')
        args = parser.parse_args()
        section = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        section.name = args['name']
        db.session.commit()
        return section.as_json(), 201
