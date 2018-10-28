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


@api.route('/auth', methods=['POST'])
def users():
    if not request.is_json:
        return abort(400, 'Missing JSON in request')
    if not all(_ in request.json for _ in ('phone_number', 'first_name', 'last_name')):
        return abort(400, 'Request must contain \'phone_number\', \'first_name\', \'last_name\' fields.')
    phone_number = request.json['phone_number']
    if not isinstance(phone_number, int):
        return abort(400, '\'phone_number\' is incorrect.')
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    sms_code = generate_sms_code()

    with db_connecton() as conn:
        r.table('users').insert(
            {
                'phone_number': phone_number,
                'first_name': first_name,
                'last_name': last_name,
                'last_sms_code': sms_code,
            }
        ).run(conn)
    send_sms_code(phone_number, sms_code)
    return jsonify({
        'success': True
    })


@api.route('/auth/request_sms_code', methods=['POST'])
def request_sms_code():
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request.'}), 400
    if 'phone_number' not in request.json:
        return jsonify({'error': 'Request must contain \'phone_number\' field.'}), 400
    phone_number = request.json['phone_number']
    if not isinstance(phone_number, int):
        return jsonify({'error': '\'phone_number\' is incorrect.'}), 400
    sms_code = generate_sms_code()
    with db_connecton() as conn:
        r.table('users').get(phone_number).update({
            'last_sms_code': sms_code
        }).run(conn)
    send_sms_code(phone_number, sms_code)
    return jsonify({
        'success': True
    })


@api.route('/auth/verify', methods=['POST'])
def verify():
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request.'}), 400
    if not all(_ in request.json for _ in ('phone_number', 'sms_code')):
        return jsonify({'error': 'Request must contain \'phone_number\', \'sms_code\' fields.'}), 400
    phone_number = request.json.get('phone_number')
    if not isinstance(phone_number, int):
        return jsonify({'error': '\'phone_number\' is incorrect.'}), 400
    sms_code = request.json.get('sms_code')
    with db_connecton() as conn:
        is_good = r.table('users').get(phone_number)['last_sms_code'].eq(sms_code).run(conn)
    if not is_good:
        return jsonify({'error': 'Bad \'phone_number\' of \'sms_code\'.'}), 401
    access_token = create_access_token(identity=phone_number, expires_delta=timedelta(days=365))
    return jsonify(access_token=access_token)
