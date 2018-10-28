import rethinkdb as r
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.helpers import db_connecton, db_operation_success
from .. import api

COURSE_FIELDS = (
    'id',
    'drug_name',
    'diagnosis_id',
    'start_time',
    'duration_in_days',
    'doctor_id',
    'dose',
    'intake_mode',
    'intake_time',
    'per_day_count',
    'minutes_before_meal',
    'minutes_before_meal',
    'interval_minutes',
    'intakes'
)


@api.route('/drug_courses', methods=['GET', 'POST'])
@jwt_required
def drug_courses():
    if request.method == 'GET':
        limit = int(request.args.get('limit', 25))
        if not 0 < limit <= 100:
            return jsonify({'error': '\'limit\' must be in (0, 100]..'}), 400
        offset = int(request.args.get('offset', 0))
        if not 0 <= offset:
            return jsonify({'error': '\'limit\' must be in [0, +inf).'}), 400
        with db_connecton() as conn:
            res = r.table('drug_courses').pluck(
                'id',
                'drug_name',
                'diagnosis_id',
                'start_time',
                'duration'
            ).skip(offset).limit(limit).run(conn)
        return jsonify({
            'drug_courses': list(res)
        }), 200
    elif request.method == 'POST':
        if any(_ not in COURSE_FIELDS for _ in request.json):
            return jsonify({'error': 'JSON contains unsupported fields.'}), 400
        course = request.json
        course.update({
            'user_phone_number': get_jwt_identity(),
            'intakes': list()
        })
        with db_connecton() as conn:
            res = r.table('drug_courses').insert(course).run(conn)
        if not db_operation_success(res):
            return jsonify({'error': 'An error occurred on server side.'}), 500
        return jsonify({
            'success': True,
            'drug_course_id': res['generated_keys'][0]
        }), 201


@api.route('/drug_courses/<string:course_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required
def course(course_id: str):
    with db_connecton() as conn:
        course_exists = r.table('drug_courses').get_all(course_id).count().eq(1).run(conn)
        if not course_exists:
            return jsonify({'error': 'Drug course with given ID do not exist.'}), 400
        is_accessible = r.table('drug_courses').get(course_id)['user_phone_number'].eq(
            get_jwt_identity()).run(conn)
        if not is_accessible:
            return jsonify({'error': 'You have no permissions to this course.'}), 403
        if request.method == 'GET':
            c = r.table('drug_courses').get(course_id).run(conn)
            return jsonify({
                'drug_course': c
            }), 200

        elif request.method == 'PATCH':
            if any(_ not in COURSE_FIELDS for _ in request.json):
                return jsonify({'error': 'JSON contains unsupported fields.'}), 400
            res = r.table('drug_courses').get(course_id).update(request.json, return_changes=True).run(conn)
            if not db_operation_success(res):
                return jsonify({'error': 'An error occurred on server side.'}), 500
            return jsonify({
                'drug_course': res['changes'][0]['new_val']
            }), 200
        elif request.method == 'DELETE':
            res = r.table('drug_courses').get(course_id).delete().run(conn)
            if not db_operation_success(res):
                return jsonify({'error': 'An error occurred on server side.'}), 500
            return jsonify({
                'success': True
            }), 200


@api.route('/drug_courses/<string:course_id>/intakes', methods=['GET', 'POST'])
@jwt_required
def intakes(course_id: str):
    with db_connecton() as conn:
        course_exists = r.table('drug_courses').get_all(course_id).count().eq(1).run(conn)
        if not course_exists:
            return jsonify({'error': 'Drug course with given ID do not exist.'}), 400
        is_accessible = r.table('drug_courses').get(course_id)['user_phone_number'].eq(
            get_jwt_identity()).run(conn)
        if not is_accessible:
            return jsonify({'error': 'You have no permissions to this course.'}), 403
        if request.method == 'GET':
            limit = int(request.args.get('limit', 25))
            if not 0 < limit <= 100:
                return jsonify({'error': '\'limit\' must be in (0, 100]..'}), 400
            offset = int(request.args.get('offset', 0))
            if not 0 <= offset:
                return jsonify({'error': '\'limit\' must be in [0, +inf).'}), 400
            res = r.table('drug_courses').get(course_id)['intakes'].skip(offset).limit(limit).run(conn)
            return jsonify({
                'intakes': res
            }), 200
        elif request.method == 'POST':
            if 'at' not in request.json or len(request.json) > 1:
                return jsonify({'error': 'JSON contains unsupported fields.'}), 400
            at = request.json['at']
            res = r.table('drug_courses').get(course_id).update({
                'intakes': r.row['intakes'].append(at)
            }).run(conn)
            if not db_operation_success(res):
                return jsonify({'error': 'An error occurred on server side.'}), 500
            return jsonify({
                'success': True
            }), 200


@api.route('/drug_courses/<string:course_id>/intakes/count', methods=['GET'])
@jwt_required
def intakes_count(course_id: str):
    with db_connecton() as conn:
        count = r.table('drug_courses').get(course_id)['intakes'].count().run(conn)
        return jsonify({
            'intakes_count': count
        }), 200
