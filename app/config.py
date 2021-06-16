from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin


class Configuration(object):
    DEBUG = True
    ENV = 'development'

    SQLALCHEMY_DATABASE_URI = 'postgresql://cherelady:000@localhost/cherelady'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CONFIRM_DELETED_ROWS = False

    APISPEC_SPEC: APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    )
    APISPEC_SWAGGER_URL = '/swagger/'  # URI to access API Doc JSON
    APISPEC_SWAGGER_UI_URL = '/swagger-ui/'  # URI to access UI of API Doc

    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    JSONIFY_MIMETYPE = 'application/hal+json'
