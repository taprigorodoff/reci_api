from flask_restful import Resource
from sqlalchemy import exc
from models.db import DStoreSection, DUnit, DStage, DCategory, DPrePackType
from models.db import Foodstuff, Ingredient, Dish
from resources.schema.dictionary.store_section.request import StoreSectionRequestSchema
from resources.schema.dictionary.store_section.response import StoreSectionResponseSchema
from resources.schema.dictionary.unit.request import UnitRequestSchema
from resources.schema.dictionary.stage.request import StageRequestSchema
from resources.schema.dictionary.category.request import CategoryRequestSchema
from resources.schema.dictionary.pre_pack_type.request import PrePackTypeRequestSchema
from app import db
from app import cache

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class StoreSectionList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read store sections.')
    def get(self):
        sections = DStoreSection.query.order_by(DStoreSection.id.desc()).all()
        return StoreSectionResponseSchema(many=True).dump(sections), 200

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
        cache.clear()
        return StoreSectionResponseSchema().dump(section), 201


class StoreSectionDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read store section.')
    def get(self, id):
        section = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()
        return StoreSectionResponseSchema().dump(section), 200

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
            cache.clear()
            return StoreSectionResponseSchema().dump(section), 200
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
            cache.clear()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class UnitList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read units.')
    def get(self):
        r = DUnit.query.order_by(DUnit.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(tags=['dictionary'], description='Create unit.')
    @use_kwargs(UnitRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = UnitRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        unit = DUnit()
        unit.name = kwargs['name']

        try:
            db.session.add(unit)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return unit.as_json(), 201


class UnitDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read unit.')
    def get(self, id):
        r = DUnit.query.filter(DUnit.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['dictionary'], description='Update unit.')
    @use_kwargs(UnitRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = UnitRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        unit = DUnit.query.filter(DUnit.id == id).first_or_404()
        unit.name = kwargs['name']

        try:
            db.session.add(unit)
            db.session.commit()
            cache.clear()
            return unit.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['dictionary'], description='Delete unit.')
    def delete(self, id):
        r = DUnit.query.filter(DUnit.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.unit_id == id).all()
        if ingredients:
            return {
                       "message": "unit already use"
                   }, 422

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            cache.clear()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class StageList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read stages.')
    def get(self):
        r = DStage.query.order_by(DStage.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(tags=['dictionary'], description='Create stage.')
    @use_kwargs(StageRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = StageRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        stage = DStage()
        stage.name = kwargs['name']

        try:
            db.session.add(stage)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return stage.as_json(), 201


class StageDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read stage.')
    def get(self, id):
        r = DStage.query.filter(DStage.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['dictionary'], description='Update stage.')
    @use_kwargs(StageRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = StageRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        stage = DStage.query.filter(DStage.id == id).first_or_404()
        stage.name = kwargs['name']

        try:
            db.session.add(stage)
            db.session.commit()
            cache.clear()
            return stage.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['dictionary'], description='Delete stage.')
    def delete(self, id):
        r = DStage.query.filter(DStage.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.stage_id == id).all()
        if ingredients:
            return {
                       "message": "stage already use"
                   }, 422

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            cache.clear()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class CategoryList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read categories.')
    def get(self):
        r = DCategory.query.order_by(DCategory.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(tags=['dictionary'], description='Create category.')
    @use_kwargs(CategoryRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = CategoryRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        category = DCategory()
        category.name = kwargs['name']

        try:
            db.session.add(category)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return category.as_json(), 201


class CategoryDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read category.')
    def get(self, id):
        r = DCategory.query.filter(DCategory.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['dictionary'], description='Update category.')
    @use_kwargs(CategoryRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = CategoryRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        category = DCategory.query.filter(DCategory.id == id).first_or_404()
        category.name = kwargs['name']

        try:
            db.session.add(category)
            db.session.commit()
            cache.clear()
            return category.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['dictionary'], description='Delete category.')
    def delete(self, id):
        category = DCategory.query.filter(DCategory.id == id).first_or_404()

        dishes = Dish.query.filter(Dish.categories.contains(category)).all()  # todo
        if dishes:
            return {
                       "message": "category already use"
                   }, 422

        try:
            db.session.add(category)
            db.session.delete(category)
            db.session.commit()
            cache.clear()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


class PrePackTypeList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read pre pack types.')
    def get(self):
        r = DPrePackType.query.order_by(DPrePackType.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(tags=['dictionary'], description='Create pre pack type.')
    @use_kwargs(PrePackTypeRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = PrePackTypeRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        pre_pack_type = DPrePackType()
        pre_pack_type.name = kwargs['name']

        try:
            db.session.add(pre_pack_type)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return pre_pack_type.as_json(), 201


class PrePackTypeDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read pre pack type.')
    def get(self, id):
        r = DPrePackType.query.filter(DPrePackType.id == id).first_or_404()
        return r.as_json(), 200

    @doc(tags=['dictionary'], description='Update pre pack type.')
    @use_kwargs(PrePackTypeRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = PrePackTypeRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        pre_pack_type = DPrePackType.query.filter(DPrePackType.id == id).first_or_404()
        pre_pack_type.name = kwargs['name']

        try:
            db.session.add(pre_pack_type)
            db.session.commit()
            cache.clear()
            return pre_pack_type.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(tags=['dictionary'], description='Delete pre pack type.')
    def delete(self, id):
        pre_pack_type = DPrePackType.query.filter(DPrePackType.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.pre_pack_type_id == id).all()
        if ingredients:
            return {
                       "message": "pre pack type already use"
                   }, 422

        try:
            db.session.add(pre_pack_type)
            db.session.delete(pre_pack_type)
            db.session.commit()
            cache.clear()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503
