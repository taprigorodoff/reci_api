from flask_restful import Resource
from sqlalchemy import exc

from models.db import DStoreSection, DUnit, DStage, DCategory, DPrePackType
from models.db import Foodstuff, Ingredient, Dish

from resources.schema.dictionary.store_section.request import StoreSectionRequestSchema
from resources.schema.dictionary.store_section.response import StoreSectionResponseSchema
from resources.schema.dictionary.unit.request import UnitRequestSchema
from resources.schema.dictionary.unit.response import UnitResponseSchema
from resources.schema.dictionary.stage.request import StageRequestSchema
from resources.schema.dictionary.stage.response import StageResponseSchema
from resources.schema.dictionary.category.request import CategoryRequestSchema
from resources.schema.dictionary.category.response import CategoryResponseSchema
from resources.schema.dictionary.pre_pack_type.request import PrePackTypeRequestSchema
from resources.schema.dictionary.pre_pack_type.response import PrePackTypeResponseSchema
from common.response_http_codes import response_http_codes

from app import db
from app import cache

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs


class StoreSectionList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read store sections.', responses=response_http_codes([200]))
    def get(self):
        sections = DStoreSection.query.order_by(DStoreSection.id.desc()).all()

        return StoreSectionResponseSchema(many=True).dump(sections), 200

    @doc(tags=['dictionary'], description='Create store section.', responses=response_http_codes([201, 400, 503]))
    @use_kwargs(StoreSectionRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = StoreSectionRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400

        section = DStoreSection()
        section.name = kwargs['name']

        try:
            db.session.add(section)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return StoreSectionResponseSchema().dump(section), 201


class StoreSectionDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read store section.', responses=response_http_codes([200, 404]))
    def get(self, id):
        section = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()

        return StoreSectionResponseSchema().dump(section), 200

    @doc(tags=['dictionary'], description='Update store section.', responses=response_http_codes([200, 400, 404, 503]))
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return StoreSectionResponseSchema().dump(section), 200

    @doc(tags=['dictionary'], description='Delete store section.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        sections = DStoreSection.query.filter(DStoreSection.id == id).first_or_404()

        foodstuffs = Foodstuff.query.filter(Foodstuff.store_section_id == id).all()
        if foodstuffs:
            return {
                       'messages': {
                           'store_section_id': [
                               'Already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(sections)
            db.session.delete(sections)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class UnitList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read units.', responses=response_http_codes([200]))
    def get(self):
        units = DUnit.query.order_by(DUnit.id.desc()).all()

        return UnitResponseSchema(many=True).dump(units), 200

    @doc(tags=['dictionary'], description='Create unit.', responses=response_http_codes([201, 400, 503]))
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

        return UnitResponseSchema().dump(unit), 201


class UnitDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read unit.', responses=response_http_codes([200, 404]))
    def get(self, id):
        unit = DUnit.query.filter(DUnit.id == id).first_or_404()

        return UnitResponseSchema().dump(unit), 200

    @doc(tags=['dictionary'], description='Update unit.', responses=response_http_codes([200, 400, 404, 503]))
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return UnitResponseSchema().dump(unit), 200

    @doc(tags=['dictionary'], description='Delete unit.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        unit = DUnit.query.filter(DUnit.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.unit_id == id).all()
        if ingredients:
            return {
                       'messages': {
                           'unit_id': [
                               'Already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(unit)
            db.session.delete(unit)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class StageList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read stages.', responses=response_http_codes([200]))
    def get(self):
        stages = DStage.query.order_by(DStage.id.desc()).all()

        return StageResponseSchema(many=True).dump(stages), 200

    @doc(tags=['dictionary'], description='Create stage.', responses=response_http_codes([201, 400, 503]))
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

        return StageResponseSchema().dump(stage), 201


class StageDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read stage.', responses=response_http_codes([200, 404]))
    def get(self, id):
        stage = DStage.query.filter(DStage.id == id).first_or_404()

        return StageResponseSchema().dump(stage), 200

    @doc(tags=['dictionary'], description='Update stage.', responses=response_http_codes([200, 400, 404, 503]))
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return StageResponseSchema().dump(stage), 200

    @doc(tags=['dictionary'], description='Delete stage.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        stage = DStage.query.filter(DStage.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.stage_id == id).all()
        if ingredients:
            return {
                       'messages': {
                           'stage_id': [
                               'Already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(stage)
            db.session.delete(stage)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class CategoryList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read categories.', responses=response_http_codes([200]))
    def get(self):
        categories = DCategory.query.order_by(DCategory.id.desc()).all()

        return CategoryResponseSchema(many=True).dump(categories), 200

    @doc(tags=['dictionary'], description='Create category.', responses=response_http_codes([201, 400, 503]))
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

        return CategoryResponseSchema().dump(category), 201


class CategoryDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read category.', responses=response_http_codes([200, 404]))
    def get(self, id):
        category = DCategory.query.filter(DCategory.id == id).first_or_404()

        return CategoryResponseSchema().dump(category), 200

    @doc(tags=['dictionary'], description='Update category.', responses=response_http_codes([200, 400, 404, 503]))
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return CategoryResponseSchema().dump(category), 200

    @doc(tags=['dictionary'], description='Delete category.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        category = DCategory.query.filter(DCategory.id == id).first_or_404()

        dishes = Dish.query.filter(Dish.categories.contains(category)).all()
        if dishes:
            return {
                       'messages': {
                           'category_id': [
                               'Already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(category)
            db.session.delete(category)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204


class PrePackTypeList(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read pre pack types.', responses=response_http_codes([200]))
    def get(self):
        pre_pack_types = DPrePackType.query.order_by(DPrePackType.id.desc()).all()

        return PrePackTypeResponseSchema(many=True).dump(pre_pack_types), 200

    @doc(tags=['dictionary'], description='Create pre pack type.', responses=response_http_codes([201, 400, 503]))
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

        return PrePackTypeResponseSchema().dump(pre_pack_type), 201


class PrePackTypeDetail(MethodResource, Resource):
    @cache.cached()
    @doc(tags=['dictionary'], description='Read pre pack type.', responses=response_http_codes([200, 404]))
    def get(self, id):
        pre_pack_type = DPrePackType.query.filter(DPrePackType.id == id).first_or_404()

        return PrePackTypeResponseSchema().dump(pre_pack_type), 200

    @doc(tags=['dictionary'], description='Update pre pack type.', responses=response_http_codes([200, 400, 404, 503]))
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
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return PrePackTypeResponseSchema().dump(pre_pack_type), 200

    @doc(tags=['dictionary'], description='Delete pre pack type.', responses=response_http_codes([204, 404, 422, 503]))
    def delete(self, id):
        pre_pack_type = DPrePackType.query.filter(DPrePackType.id == id).first_or_404()

        ingredients = Ingredient.query.filter(Ingredient.pre_pack_type_id == id).all()
        if ingredients:
            return {
                       'messages': {
                           'pre_pack_type_id': [
                               'Already use'
                           ]
                       }
                   }, 422

        try:
            db.session.add(pre_pack_type)
            db.session.delete(pre_pack_type)
            db.session.commit()
            cache.clear()
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

        return '', 204
