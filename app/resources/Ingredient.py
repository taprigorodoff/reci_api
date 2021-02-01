from flask_restful import Resource, reqparse, abort
from sqlalchemy import exc
from resources.models import Ingredient, DStoreSection, RecipeIngredient
from app import db
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields, ValidationError, validate, types
import typing

class IngredientRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=50))
    store_section_id = fields.Integer(required=True, description="API type of awesome API")

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)

    def validate(
        self,
        data: typing.Mapping,
        *,
        many: typing.Optional[bool] = None,
        partial: typing.Optional[typing.Union[bool, types.StrSequenceOrSet]] = None
    ) -> typing.Dict[str, typing.List[str]]:
        store_section_ids = [cat.id for cat in db.session.query(DStoreSection.id).all()]  # todo кэш
        validation_errors = {}
        if data['store_section_id'] not in store_section_ids:
            validation_errors.update(
                {
                    'store_section_id': [
                        'Bad choice for store_section_id'
                    ]
                }
            )
        if Ingredient.query.filter(Ingredient.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors

class IngredientList(MethodResource, Resource):
    @doc(description='Read all ingredients.')
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

    @doc(description='Create ingredient.')
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = IngredientRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        ingredient = Ingredient()
        ingredient.name = kwargs['name']
        ingredient.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(ingredient)
            db.session.commit()
            return ingredient.as_json(), 201
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class IngredientDetail(MethodResource, Resource):
    @doc(description='Read ingredient.')
    def get(self, id):
        r = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        return r.as_json(), 200

    @doc(description='Update ingredient.')
    @use_kwargs(IngredientRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = IngredientRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        ingredient = Ingredient.query.filter(Ingredient.id == id).first_or_404()
        ingredient.name = kwargs['name']
        ingredient.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(ingredient)
            db.session.commit()
            return ingredient.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(description='Delete ingredient.')
    def delete(self, id):
        r = Ingredient.query.filter(Ingredient.id == id).first_or_404()

        use_ingredients = RecipeIngredient.query.filter(RecipeIngredient.ingredient_id == id).all()
        if use_ingredients:
            return {
                       "message": "ingredient already use in recipes"
                   }, 422

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

class StoreSectionRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=50))

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
        if DStoreSection.query.filter(DStoreSection.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors

class StoreSectionList(MethodResource, Resource):
    @doc(description='Read store sections.')
    def get(self):
        r = DStoreSection.query.order_by(DStoreSection.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create store section.')
    @use_kwargs(StoreSectionRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = StoreSectionRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        section = DStoreSection()
        section.name = kwargs['name']
        db.session.add(section)
        db.session.commit()
        return section.as_json(), 201


class StoreSectionDetail(MethodResource, Resource):
    @doc(description='Read store section.')
    def get(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        return r.as_json(), 200

    @doc(description='Update store section.')
    @use_kwargs(StoreSectionRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = StoreSectionRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        section = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        section.name = kwargs['name']

        try:
            db.session.add(section)
            db.session.commit()
            return section.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(description='Delete store section.')
    def delete(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.store_section_id == id).all()
        if ingredients:
            return {
                       "message": "store section already use"
                   }, 422

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503
