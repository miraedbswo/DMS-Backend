from flask import Blueprint, Response, abort, g, request
from flask_restful import Api
from flasgger import swag_from

from app.docs.v2.admin.point.point import *
from app.models.account import AdminModel, StudentModel
from app.models.point import PointRuleModel, PointHistoryModel
from app.views.v2 import BaseResource, auth_required, json_required

api = Api(Blueprint(__name__, __name__, url_prefix='/admin'))


@api.resource('/point')
class Point(BaseResource):
    @auth_required(AdminModel)
    @swag_from(POINT_GET)
    def get(self):
        """
        특정 학생의 상벌점 내역 조회
        """
        id = request.args['id']

        student = StudentModel.objects(id=id).first()

        if not student:
            return Response('', 204)

        return self.unicode_safe_json_dumps([{
            'id': str(history.id),
            'date': history.time.strftime('%Y-%m-%d'),
            'reason': history.reason,
            'pointType': history.point_type,
            'point': history.point
        } for history in student.point_histories])

    @auth_required(AdminModel)
    @json_required('id', 'ruleId', 'point')
    @swag_from(POINT_POST)
    def post(self):
        """
        특정 학생에게 상벌점 부여
        """
        id = request.json['id']
        rule_id = request.json['ruleId']
        point = request.json['point']

        student = StudentModel.objects(id=id).first()

        if not student:
            return Response('', 204)

        if len(rule_id) != 24 or not PointRuleModel.objects(id=rule_id):
            return Response('', 205)

        rule = PointRuleModel.objects(id=rule_id).first()

        if not rule.min_point <= point <= rule.max_point:
            # 최소 점수와 최대 점수 외의 점수를 부여하는 경우
            abort(403)

        point_history = PointHistoryModel(
            reason=rule.name,
            point_type=rule.point_type,
            point=point
        )

        student.point_histories.append(point_history)

        if (student.bad_point - 10) // 5 > student.penalty_level and not student.penalty_training_status:
            student.penalty_level = student.penalty_level + 1
            student.penalty_training_status = True

        if rule.point_type:
            student.good_point += point
        else:
            student.bad_point += point

        student.save()

        return {
            'id': str(point_history.id)
        }, 201

    @swag_from(POINT_DELETE)
    def patch(self):
        pass
