import os

from flask import Flask
from flask_jwt_extended import JWTManager

from .helpers import db_connecton

app = Flask(__name__)
app.debug = True
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
jwt = JWTManager(app)

# def authenticate(phone_number, sms_code):
#     with db_connecton() as conn:
#         is_good = r.table('users').get(phone_number).get_field('last_sms_code').eq(sms_code).run(conn)
#         if not is_good:
#             return abort(403, 'Incorrect SMS code.')
#         user = r.table('users').get(phone_number).run(conn)
#     return user
#
#
# def make_payload(identity):
#     return {'phone_number': identity['phone_number']}
#
#
# def identity(payload):
#     phone_number = payload['phone_number']
#     with db_connecton() as conn:
#         u = r.table('users').get(phone_number).run(conn)
#         return u


# jwt = JWTManager(app, authentication_handler=authenticate, identity_handler=identity)

from . import routes
