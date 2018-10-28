from datetime import datetime

import rethinkdb as r
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.helpers import db_connecton, db_operation_success
from .. import api

DIAGNOSIS_FIELDS = (
    'id',
    'user_phone_number',
    'summary',
    'description',
    'created_at',
    'doctor_id',
    'symptoms',
    'drug_courses_ids'
)


@api.route('/diagnoses', methods=['GET', 'POST'])
@jwt_required
def diagnoses():
    if request.method == 'GET':
        limit = int(request.args.get('limit', 25))
        if not 0 < limit <= 100:
            return jsonify({'error': '\'limit\' must be in (0, 100]..'}), 400
        offset = int(request.args.get('offset', 0))
        if not 0 <= offset:
            return jsonify({'error': '\'limit\' must be in [0, +inf).'}), 400
        with db_connecton() as conn:
            res = r.table('diagnoses').filter({
                'user_phone_number': get_jwt_identity()
            }).skip(offset).limit(limit).pluck(
                'id',
                'name',
                'created_at',
                'symptoms'
            ).run(conn)
        return jsonify({
            'diagnoses': list(res)
        }), 200

    elif request.method == 'POST':
        if any(_ not in DIAGNOSIS_FIELDS for _ in request.json):
            return jsonify({'error': 'JSON contains unsupported fields.'}), 400
        diagnosis = request.json
        diagnosis.update({
            'user_phone_number': get_jwt_identity(),
            'created_at': int(datetime.now().timestamp())
        })
        with db_connecton() as conn:
            res = r.table('diagnoses').insert(diagnosis).run(conn)
        if not db_operation_success(res):
            return jsonify({'error': 'An error occurred on server side.'}), 500
        return jsonify({
            'success': True,
            'diagnosis_id': res['generated_keys'][0]
        }), 201


@api.route('/diagnoses/<string:diagnosis_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required
def diagnosis(diagnosis_id: str):
    with db_connecton() as conn:
        diagnosis_exists = r.table('diagnoses').get_all(diagnosis_id).count().eq(1).run(conn)
        if not diagnosis_exists:
            return jsonify({'error': 'Diagnosis with given ID do not exist.'}), 400
        is_accessible = r.table('diagnoses').get(diagnosis_id).get_field('user_phone_number').eq(
            get_jwt_identity()).run(conn)
        if not is_accessible:
            return jsonify({'error': 'You have no permissions to this diagnosis.'}), 403

        if request.method == 'GET':
            d = r.table('diagnoses').get(diagnosis_id).run(conn)
            return jsonify({
                'diagnosis': d
            }), 200
        elif request.method == 'PATCH':
            if any(_ not in DIAGNOSIS_FIELDS for _ in request.json):
                return jsonify({'error': 'JSON contains unsupported fields.'}), 400
            res = r.table('diagnoses').get(diagnosis_id).update(request.json, return_changes=True).run(conn)
            if not db_operation_success(res):
                return jsonify({'error': 'An error occurred on server side.'}), 500
            return jsonify({
                'diagnosis': res['changes'][0]['new_val']
            }), 200
        elif request.method == 'DELETE':
            res = r.table('diagnoses').get(diagnosis_id).delete().run(conn)
            if not db_operation_success(res):
                return jsonify({'error': 'An error occurred on server side.'}), 500
            return jsonify({
                'success': True
            }), 200
