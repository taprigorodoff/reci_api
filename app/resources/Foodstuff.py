from flask_restful import Resource, abort
from sqlalchemy import exc
from resources.models import Foodstuff, DStoreSection, Ingredient
from app import db
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields, ValidationError, validate, types
import typing

class FoodstuffRequestSchema(Schema):
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
        if Foodstuff.query.filter(Foodstuff.name == data["name"]).first():
            validation_errors.update(
                {
                    'name': [
                        'Already exist'
                    ]
                }
            )
        return validation_errors

class FoodstuffList(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read all Foodstuffs.')
    def get(self):
        r = Foodstuff.query.order_by(Foodstuff.id.desc()).all()
        results = {}

        for ob in r:
            foodstuff = ob.as_json()
            store_section = foodstuff.pop('store_section', 'other')['name']
            tmp_foodstuffs = results.get(store_section, [])
            tmp_foodstuffs.append(foodstuff)
            results.update({store_section: tmp_foodstuffs})

        return results, 200

    @doc(tags=['foodstuff'], description='Create foodstuff.')
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        foodstuff = Foodstuff()
        foodstuff.name = kwargs['name']
        foodstuff.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(foodstuff)
            db.session.commit()
            return foodstuff.as_json(), 201
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class FoodstuffDetail(MethodResource, Resource):
    @doc(tags=['foodstuff'], description='Read foodstuff.')
    def get(self, id):
        r = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['foodstuff'], description='Update foodstuff.')
    @use_kwargs(FoodstuffRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = FoodstuffRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        foodstuff = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()
        foodstuff.name = kwargs['name']
        foodstuff.store_section_id = kwargs['store_section_id']

        try:
            db.session.add(foodstuff)
            db.session.commit()
            return foodstuff.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['foodstuff'], description='Delete foodstuff.')
    def delete(self, id):
        r = Foodstuff.query.filter(Foodstuff.id == id).first_or_404()

        use_ingredients = Ingredient.query.filter(Ingredient.foodstuff_id == id).all()
        if use_ingredients:
            return {
                       "message": "ingredient already use in dishes"
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
    @doc(tags=['dictionary'], description='Read store sections.')
    def get(self):
        r = DStoreSection.query.order_by(DStoreSection.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(tags=['dictionary'], description='Create store section.')
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
    @doc(tags=['dictionary'], description='Read store section.')
    def get(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['dictionary'], description='Update store section.')
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

    @doc(tags=['dictionary'], description='Delete store section.')
    def delete(self, id):
        r = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()

        foodstuffs = Foodstuff.query.filter(Foodstuff.store_section_id == id).all()
        if foodstuffs:
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
