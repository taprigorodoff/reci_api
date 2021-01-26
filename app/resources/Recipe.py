from flask_restful import Resource, reqparse, abort
from flask import send_from_directory
from sqlalchemy import exc
from resources.models import Recipe, RecipeIngredient, Ingredient
from resources.models import DCategory, DStage, DUnit, DPrepackType
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields, ValidationError, validate


class RecipeRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=3))
    description = fields.String(required=True, description="API type of awesome API")
    portion = fields.Integer(required=True, description="API type of awesome API")
    cook_time = fields.Integer(required=True, description="API type of awesome API")
    all_time = fields.Integer(required=True, description="API type of awesome API")
    categories = fields.List(cls_or_instance=fields.Integer(),
                             required=True,
                             description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)


class RecipeList(MethodResource, Resource):
    @doc(description='Read all recipes.')
    def get(self):
        '''
        Get method represents a GET API method
        '''
        r = Recipe.query.order_by(Recipe.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create recipe.')
    @use_kwargs(RecipeRequestSchema(), location=('json'))
    def post(self, **kwargs):
        recipe = Recipe()
        recipe.name = kwargs['name']
        recipe.description = kwargs['description']
        recipe.portion = kwargs['portion']
        recipe.cook_time = kwargs['cook_time']
        recipe.all_time = kwargs['all_time']
        for category_id in kwargs['categories']:
            category = DCategory.query.get(category_id)
            if category:
                recipe.categories.append(category)
            else:
                return {
                           'messages': 'bad choice for category'
                       }, 400

        try:
            db.session.add(recipe)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 500

        return recipe.as_json(), 200


class RecipeDetail(MethodResource, Resource):
    @doc(description='Read recipe.')
    def get(self, id):
        recipe = Recipe.query.filter(Recipe.id == id).first_or_404()
        return recipe.as_full_json(), 200

    @doc(description='Delete recipe.')
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

class RecipeIngredientRequestSchema(Schema):
    ingredient_id = fields.Integer(required=True, description="API type of awesome API")
    amount = fields.Float(required=True, description="API type of awesome API")
    required = fields.Bool(required=True, description="API type of awesome API")
    unit_id = fields.Integer(required=True, description="API type of awesome API")
    prepack_type_id = fields.Integer(required=True, description="API type of awesome API") #required=False, nullable=True,
    stage_id = fields.Integer(required=True, description="API type of awesome API") #required=False, nullable=True,
    alternative_ids = fields.List(cls_or_instance=fields.Integer(),
                             required=True,
                             description="API type of awesome API") #required=False, nullable=True,

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)
        
class RecipeIngredientList(MethodResource, Resource):
    @doc(description='Create recipe ingredient.')
    @use_kwargs(RecipeIngredientRequestSchema(), location=('json'))
    #todo документировать коды ошибок
    def post(self, recipe_id, **kwargs):

        unit_ids = [cat.id for cat in db.session.query(DUnit.id).all()]  # todo кэш
        prepack_type_ids = [cat.id for cat in db.session.query(DPrepackType.id).all()]  # todo кэш
        stage_ids = [cat.id for cat in db.session.query(DStage.id).all()]  # todo кэш

        # todo посмотреть (в джанго?) куда убрать влидацию
        validation_errors = {}
        if kwargs['unit_id'] not in unit_ids:
            validation_errors.update(
                {
                    'unit_id': [
                        'Bad choice for unit_id'
                    ]
                }
            )
        if kwargs['prepack_type_id'] not in prepack_type_ids:
            validation_errors.update(
                {
                    'prepack_type_id': [
                        'Bad choice for prepack_type_id'
                    ]
                }
            )
        if kwargs['stage_id'] not in stage_ids:
            validation_errors.update(
                {
                    'stage_id': [
                        'Bad choice for stage_id'
                    ]
                }
            )

        ingredient = Ingredient.query.filter(Ingredient.id == kwargs['ingredient_id']).first()
        if not ingredient:
            validation_errors.update(
                {
                    'ingredient_id': [
                        'Bad choice for ingredient_id'
                    ]
                }
            )
        if kwargs['alternative_ids']:
            for alternative_id in kwargs['alternative_ids']:
                ingredient = Ingredient.query.filter(Ingredient.id == alternative_id).first()

                if not ingredient:
                    validation_errors.update(
                        {
                            'alternative_id': [
                                'Bad choice for alternative_id'
                            ]
                        }
                    )

        #todo проверить существование рецепта!
        exist_ingredient = RecipeIngredient.query.filter(RecipeIngredient.ingredient_id == kwargs['ingredient_id'],
                                                         RecipeIngredient.recipe_id == recipe_id).first()
        if exist_ingredient:
            validation_errors.update(
                {
                    'ingredient_id': [
                        f'Already added to recipe {recipe_id}'
                    ]
                }
            )

        if validation_errors:
            return {
                'messages': validation_errors
            }, 400

        ri = RecipeIngredient()
        ri.recipe_id = recipe_id
        ri.ingredient_id = kwargs['ingredient_id']
        ri.amount = kwargs['amount']
        ri.unit_id = kwargs['unit_id']
        ri.required = kwargs['required']
        ri.prepack_type_id = kwargs['prepack_type_id']
        ri.stage_id = kwargs['stage_id']

        if kwargs['alternative_ids']:
            for alternative_id in kwargs['alternative_ids']:
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

    @doc(description='Read recipe ingredients.')
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


class RecipeIngredientDetail(MethodResource, Resource):
    @doc(description='Read recipe ingredient.')
    def get(self, recipe_id, id):
        ri = RecipeIngredient.query.filter(RecipeIngredient.id == id,
                                           RecipeIngredient.recipe_id == recipe_id).first_or_404()
        return ri.as_json(), 200

    @doc(description='Update recipe ingredient.')
    @use_kwargs(RecipeIngredientRequestSchema(), location=('json'))
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

    @doc(description='Delete recipe ingredient.')
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


class RecipeImg(MethodResource, Resource):
    @doc(description='Read recipe img.')
    def get(self, id):
        response = send_from_directory(directory='images/', filename='{}.jpg'.format(id))
        return response
