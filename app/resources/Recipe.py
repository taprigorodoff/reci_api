from flask_restful import Resource, reqparse
from flask import send_from_directory
from sqlalchemy import exc
from resources.models import Recipe, RecipeIngredient, Ingredient
from resources.models import DCategory, DStage, DUnit, DPrepackType
from app import db


class RecipeList(Resource):
    def get(self):
        r = Recipe.query.order_by(Recipe.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    def post(self):
        cat_ids = [cat.id for cat in db.session.query(DCategory.id).all()]  # todo кэш

        parser = reqparse.RequestParser()
        parser.add_argument('name')
        parser.add_argument('description')
        parser.add_argument('portion', type=int, help='{error_msg}')
        parser.add_argument('cook_time', type=int, help='{error_msg}')
        parser.add_argument('all_time', type=int, help='{error_msg}')
        parser.add_argument('categories', type=int, choices=cat_ids, action='append', help='Bad choice: {error_msg}')

        args = parser.parse_args()

        recipe = Recipe()
        recipe.name = args['name']
        recipe.description = args['description']
        recipe.portion = args['portion']
        recipe.cook_time = args['cook_time']
        recipe.all_time = args['all_time']
        for cat_id in args['categories']:
            recipe.categories.append(DCategory.query.get(cat_id))

        db.session.add(recipe)
        db.session.commit()

        return recipe.as_json(), 200


class RecipeDetail(Resource):
    def get(self, id):
        recipe = Recipe.query.filter(Recipe.id == id).first_or_404()
        return recipe.as_full_json(), 200

    def delete(self, id):
        r = Recipe.query.filter(Recipe.id == id).first_or_404()
        db.session.add(r)
        db.session.delete(r)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 500

        return '', 204


class RecipeIngredientList(Resource):
    def get(self, recipe_id):
        recipe = Recipe.query.filter(Recipe.id == recipe_id).first_or_404()
        recipe_ingredients = {}
        for ob in recipe.recipe_recipe_ingredients_0:
            ingredient = ob.as_json()

            stage_name = ingredient.pop('stage')

            tmp_ingredients = recipe_ingredients.get(stage_name, [])
            tmp_ingredients.append(ingredient)
            recipe_ingredients.update({stage_name: tmp_ingredients})

        return recipe_ingredients, 200

    def post(self, recipe_id):
        unit_ids = [cat.id for cat in db.session.query(DUnit.id).all()]  # todo кэш
        prepack_type_ids = [cat.id for cat in db.session.query(DPrepackType.id).all()]  # todo кэш
        stage_ids = [cat.id for cat in db.session.query(DStage.id).all()]  # todo кэш

        parser = reqparse.RequestParser()
        parser.add_argument('ingredient_id', type=int, help='{error_msg}')  # check id
        parser.add_argument('amount')
        parser.add_argument('required', type=bool, help='{error_msg}')
        parser.add_argument('unit_id', type=int, choices=unit_ids, help='Bad choice: {error_msg}')
        parser.add_argument('prepack_type_id', type=int, required=False, nullable=True, choices=prepack_type_ids,
                            help='Bad choice: {error_msg}')
        parser.add_argument('stage_id', type=int, required=False, choices=stage_ids, help='Bad choice: {error_msg}')
        parser.add_argument('alternative_ids', type=int, required=False, action='append',
                            help='{error_msg}')  # check id

        args = parser.parse_args()

        # todo посмотреть (в джанго?) куда убрать влидацию
        ingredient = Ingredient.query.filter(Ingredient.id == args['ingredient_id']).first()
        if not ingredient:
            return {
                       'messages': 'Bad choice for ingredient_id'
                   }, 400
        if args['alternative_ids']:
            for alternative_id in args['alternative_ids']:
                ingredient = Ingredient.query.filter(Ingredient.id == alternative_id).first()

                if not ingredient:
                    return {
                               'messages': 'Bad choice for alternative_ids'
                           }, 400

        exist_ingredient = RecipeIngredient.query.filter(RecipeIngredient.ingredient_id == args['ingredient_id'],
                                                         RecipeIngredient.recipe_id == recipe_id).first()
        if exist_ingredient:
            return {
                       'messages': 'already added'
                   }, 400

        ri = RecipeIngredient()
        ri.recipe_id = recipe_id
        ri.ingredient_id = args['ingredient_id']
        ri.amount = args['amount']
        ri.unit_id = args['unit_id']
        ri.required = args['required']
        ri.prepack_type_id = args['prepack_type_id']
        ri.stage_id = args['stage_id']

        if args['alternative_ids']:
            for alternative_id in args['alternative_ids']:
                ri.ingredient_alternatives.append(Ingredient.query.get(alternative_id))

        db.session.add(ri)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 500

        return ri.as_json(), 200


class RecipeIngredientDetail(Resource):
    def get(self, recipe_id, id):
        ri = RecipeIngredient.query.filter(RecipeIngredient.id == id,
                                           RecipeIngredient.recipe_id == recipe_id).first_or_404()
        return ri.as_json(), 200

    def put(self, recipe_id, id):
        unit_ids = [cat.id for cat in db.session.query(DUnit.id).all()]  # todo кэш
        prepack_type_ids = [cat.id for cat in db.session.query(DPrepackType.id).all()]  # todo кэш
        stage_ids = [cat.id for cat in db.session.query(DStage.id).all()]  # todo кэш

        parser = reqparse.RequestParser()
        parser.add_argument('ingredient_id', type=int, help='{error_msg}')  # check id
        parser.add_argument('amount')
        parser.add_argument('required', type=bool, help='{error_msg}')
        parser.add_argument('unit_id', type=int, choices=unit_ids, help='Bad choice: {error_msg}')
        parser.add_argument('prepack_type_id', type=int, required=False, nullable=True, choices=prepack_type_ids,
                            help='Bad choice: {error_msg}')
        parser.add_argument('stage_id', type=int, required=False, choices=stage_ids, help='Bad choice: {error_msg}')
        parser.add_argument('alternative_ids', type=int, required=False, action='append',
                            help='{error_msg}')  # check id

        args = parser.parse_args()

        ingredient = Ingredient.query.filter(Ingredient.id == args['ingredient_id']).first()
        if not ingredient:
            return {
                       'messages': 'Bad choice for ingredient_id'
                   }, 400
        if args['alternative_ids']:
            for alternative_id in args['alternative_ids']:
                ingredient = Ingredient.query.filter(Ingredient.id == alternative_id).first()

                if not ingredient:
                    return {
                               'messages': 'Bad choice for alternative_ids'
                           }, 400

        ri = RecipeIngredient.query.filter(RecipeIngredient.id == id).first()

        ri.ingredient_id = args['ingredient_id']
        ri.amount = args['amount']
        ri.unit_id = args['unit_id']
        ri.required = args['required']
        ri.prepack_type_id = args['prepack_type_id']
        ri.stage_id = args['stage_id']

        if args['alternative_ids']:
            for alternative_id in args['alternative_ids']:
                ri.ingredient_alternatives.append(Ingredient.query.get(alternative_id))

        db.session.add(ri)

        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 500

        return ri.as_json(), 201

    def delete(self, recipe_id, id):
        r = RecipeIngredient.query.filter(RecipeIngredient.id == id).first_or_404()
        db.session.add(r)
        db.session.delete(r)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 500


class RecipeImg(Resource):
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
