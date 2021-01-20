from flask_restful import Resource, reqparse
from flask import send_from_directory
from sqlalchemy import exc
from resources.models import Recipe, DCategory
from app import db


class RecipeList(Resource):
    def get(self):
        r = Recipe.query.order_by(Recipe.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    def post(self):
        cat_ids = [cat.id for cat in db.session.query(DCategory.id).all()]

        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('description')
        parser.add_argument('portion', type=int, help='{error_msg}')
        parser.add_argument('cook_time', type=int, help='{error_msg}')
        parser.add_argument('all_time', type=int, help='{error_msg}')
        parser.add_argument('categories', type=int, choices=cat_ids, action='append', help='Bad choice: {error_msg}')

        args = parser.parse_args()

        # todo разобрться, почему r в другой сессии(импорт?)
        recipe = Recipe()
        recipe.name = args['name']
        recipe.description = args['description']
        recipe.portion = args['portion']
        recipe.cook_time = args['cook_time']
        recipe.all_time = args['all_time']
        for cat_id in args['categories']:
            recipe.categories.append(DCategory.query.get(cat_id))

        current_db_sessions = db.session.object_session(recipe)
        current_db_sessions.add(recipe)
        current_db_sessions.commit()

        return recipe.as_json(), 200


class RecipeDetail(Resource):
    def get(self, id):
        recipe = Recipe.query.filter(Recipe.id == id).first_or_404()
        return recipe.as_full_json(), 200

    def delete(self, id):
        r = Recipe.query.filter(Recipe.id == id).first_or_404()
        # todo разобрться, почему r в другой сессии(импорт?)
        current_db_sessions = db.session.object_session(r)
        current_db_sessions.add(r)
        current_db_sessions.delete(r)
        try:
            current_db_sessions.commit()
        except exc.SQLAlchemyError as e:
            current_db_sessions.rollback()
            return {
                       'messages': e.args
                   }, 500

        return '', 204


class RecipeIngredientList(Resource):
    def get(self, recipe_id):
        print(recipe_id)
        return '', 204


class RecipeIngredientDetail(Resource):
    def get(self, recipe_id, id):
        # ingredient_id
        # amount
        # unit_id
        # alternative_ids
        # required
        # prepack_type_id
        # stage_id
        return '', 204


class RecipeImg(Resource):
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
