from flask_restful import Resource, abort
from sqlalchemy import exc
from resources.models import Menu
from app import db

from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import Schema, fields, ValidationError, validate


class MenuRequestSchema(Schema):
    name = fields.String(required=True, description="API type of awesome API", validate=validate.Length(max=100))

    def handle_error(self, error: ValidationError, __, *, many: bool, **kwargs):
        abort(400, message=error.messages)


class MenuList(MethodResource, Resource):
    @doc(description='Read all menus.')
    def get(self):
        r = Menu.query.order_by(Menu.id.desc()).all()
        results = [ob.as_json() for ob in r]
        return results, 200

    @doc(description='Create menu.')
    @use_kwargs(MenuRequestSchema(), location=('json'))
    def post(self, **kwargs):
        validation_errors = MenuRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        menu = Menu()
        menu.name = kwargs['name']

        try:
            db.session.add(menu)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            return {
                       'messages': e.args
                   }, 503

        return menu.as_json(), 200


class MenuDetail(MethodResource, Resource):
    @doc(description='Read menu.')
    def get(self, id):
        r = Menu.query.filter(Menu.id == id).first_or_404()
        return r.as_json(), 200

    @doc(description='Update menu.')
    @use_kwargs(MenuRequestSchema(), location=('json'))
    def put(self, id, **kwargs):
        validation_errors = MenuRequestSchema().validate(kwargs)
        if validation_errors:
            return {
                       'messages': validation_errors
                   }, 400
        menu = Menu.query.filter(Menu.id == id).first_or_404()
        menu.name = kwargs['name']

        try:
            db.session.add(menu)
            db.session.commit()
            return menu.as_json(), 200
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503

    @doc(description='Delete menu.')
    def delete(self, id):
        r = Menu.query.filter(Menu.id == id).first_or_404()

        try:
            db.session.add(r)
            db.session.delete(r)
            db.session.commit()
            return '', 204
        except exc.SQLAlchemyError as e:
            return {
                       'messages': e.args
                   }, 503


