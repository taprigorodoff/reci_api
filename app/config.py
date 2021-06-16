from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
import os
import configparser


class Configuration(object):
    settings = configparser.ConfigParser()
    settings.read("settings.ini")

    DEBUG = True
    ENV = 'development'

    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pw}@{url}/{db}'. \
        format(user=os.environ.get('POSTGRES_USER', settings['PostgreSQL']['user']),
               pw=os.environ.get('POSTGRES_PASSWORD', settings['PostgreSQL']['password']),
               url=os.environ.get('POSTGRES_URL', '{host}:{port}'.format(host=settings['PostgreSQL']['host'],
                                                                         port=settings['PostgreSQL']['port'])),
               db=os.environ.get('POSTGRES_DB', settings['PostgreSQL']['database'])
               )
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
    CACHE_REDIS_URL = 'redis://{url}/0'.format(
        url=os.environ.get('REDIS_URL', '{host}:{port}'.format(host=settings['Redis']['host'],
                                                                port=settings['Redis']['port'])))

    JSONIFY_MIMETYPE = 'application/hal+json'
