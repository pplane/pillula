import rethinkdb as r
from flask import request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from api.helpers import db_connecton
from .. import api


@api.route('/drug_courses', methods=['GET', 'POST'])
@jwt_required
def courses():
    if request.method == 'GET':
        limit = int(request.args.get('limit', 25))
        offset = int(request.args.get('offset', 0))
        with db_connecton() as conn:
            res = r.table('drug_courses').filter({
                'user_phone_number': get_jwt_identity()}
            ).skip(offset).limit(limit).run(conn)
        return jsonify({
            'drug_courses': list(res)
        }), 200
    elif request.method == 'POST':
        course: dict = request.json
        course.update({'user_phone_number': get_jwt_identity()})
        with db_connecton() as conn:
            res = r.table('drug_courses').insert(course).run(conn)
        return jsonify({
            'success': True,
            'drug_course_id': res['generated_keys'][0]
        }), 201


@api.route('/drug_courses/<string:course_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required
def course(course_id: str):
    if request.method == 'GET':
        with db_connecton() as conn:
            is_accessable = r.table('drug_courses').get(course_id).get_field('user_phone_number').eq(get_jwt_identity()).run(
                conn)
            if not is_accessable:
                return abort(403, 'You have no permissions to this course')
            c = r.table('drug_courses').get(course_id).run(conn)
        return jsonify({
            'drug_course': c
        })

    elif request.method == 'PATCH':
        upd = request.json
        with db_connecton() as conn:
            is_accessable = r.table('drug_courses').get(course_id).get_field('user_phone_number').eq(get_jwt_identity()).run(
                conn)
            if not is_accessable:
                return abort(403, 'You have no permissions to this course')
            res = r.table('drug_courses').get(course_id).update(upd, return_changes=True).run(conn)
        return jsonify({
            'drug_course': res['changes'][0]['new_val']
        }), 200
    elif request.method == 'DELETE':
        with db_connecton() as conn:
            is_accessable = r.table('drug_courses').get(course_id).get_field('user_phone_number').eq(
                get_jwt_identity()).run(conn)
            if not is_accessable:
                return abort(403, 'You have no permissions to this course')
            c = r.table('drug_courses').get(course_id).delete().run(conn)
        return jsonify({
            'success': True
        }), 200
