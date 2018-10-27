from datetime import timedelta

import rethinkdb as r
from flask import request, abort, jsonify
from flask_jwt_extended import create_access_token

from api.helpers import db_connecton
from .. import api


def generate_sms_code():
    # code = random.random(100000, 999999)
    code = 123456
    return code


def send_sms_code(phone_number, sms_code):
    pass
    # raise NotImplementedError


@api.route('/users', methods=['POST'])
def users():
    if not all(_ in request.json for _ in ('phone_number', 'first_name', 'last_name')):
        return abort(400, 'Request must contain \'phone_number\', \'first_name\', \'last_name\' fields')
    phone_number = request.json['phone_number']
    sms_code = generate_sms_code()

    with db_connecton() as conn:
        r.table('users').insert(
            {
                'phone_number': phone_number,
                'last_sms_code': sms_code
            }
        ).run(conn)
        send_sms_code(phone_number, sms_code)
    return jsonify({
        'success': True
    })


@api.route('/users/verify', methods=['POST'])
def verify():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    phone_number = request.json.get('phone_number')
    sms_code = request.json.get('sms_code')
    if not phone_number:
        return jsonify({"msg": "Missing \'phone_number\' parameter"}), 400
    if not sms_code:
        return jsonify({"msg": "Missing \'sms_code\' parameter"}), 400
    with db_connecton() as conn:
        is_good = r.table('users').get(phone_number).get_field('last_sms_code').eq(sms_code).run(conn)
    if not is_good:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=phone_number, expires_delta=timedelta(days=365))
    return jsonify(access_token=access_token)
