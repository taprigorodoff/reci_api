from flask_restful import Resource, reqparse
from flask import send_from_directory
from resources.models import Recipe, DCategory
from app import db


class RecipeList(Resource):
    def get(self):
        r = Recipe.query.order_by(Recipe.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    def post(self):

        cat_ids = [cat.id for cat in db.session.query(DCategory.id).all()]
        print(cat_ids)

        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('description')
        parser.add_argument('portion')
        parser.add_argument('cook_time')
        parser.add_argument('all_time')
        parser.add_argument('categories', type=int, choices=cat_ids, action='append', help='must be in dcategory')

        parser.add_argument("recipe_ingredients")
        #ingredient
        #amount
        #unit_id
        #alternatives_ids
        #required
        #prepack_type_id
        #stage_id

        args = parser.parse_args()

        return args, 200


class RecipeDetail(Resource):
    def get(self, id):
        recipe = Recipe.query.filter(Recipe.id == id).first_or_404()
        return recipe.as_full_json(), 200


class RecipeImg(Resource):
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
