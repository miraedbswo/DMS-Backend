from datetime import datetime

from flask import Blueprint, Response, g, request
from flask_restful import Api


from app.views.v1 import BaseResource
from app.views.v1 import student_only


from app.models.survey import AnswerModel, QuestionModel, SurveyModel

api = Api(Blueprint('student-survey-api', __name__))


@api.resource('/survey')
class Survey(BaseResource):

    @student_only
    def get(self):
        """
        설문지 리스트 조회
        """
        student = g.user

        student_number = student.number

        response = [{
            'id': str(survey.id),
            'creation_time': str(survey.creation_time)[:10],
            'description': survey.description,
            'title': survey.title,
            'start_date': str(survey.start_date)[:10],
            'end_date': str(survey.end_date)[:10]
        } for survey in SurveyModel.objects if int(student_number / 1000) in survey.target and survey.end_date > datetime.now()]

        return self.unicode_safe_json_response(response)
        # Filter by student number


@api.resource('/survey/question')
class Question(BaseResource):

    @student_only
    def get(self):
        """
        설문지의 질문 리스트 조회
        """
        student = g.user

        survey_id = request.args['survey_id']
        if len(survey_id) != 24:
            return Response('', 204)

        survey = SurveyModel.objects(id=survey_id).first()
        if not survey:
            return Response('', 204)

        response = [{
            'id': str(question.id),
            'title': question.title,
            'is_objective': question.is_objective,
            'choice_paper': question.choice_paper if question.is_objective else None
        } for question in QuestionModel.objects(survey=survey)]

        for question in response:
            answer = AnswerModel.objects(
                question=QuestionModel.objects(id=question['id']).first(),
                answer_student=student
            ).first()

            if answer:
                question['answer'] = answer.content
            else:
                question['answer'] = None

        return self.unicode_safe_json_response(response)


    @student_only
    def post(self):
        """
        설문지 질문의 답변 업로드
        """
        student = g.user

        question_id = request.form['question_id']
        if len(question_id) != 24:
            return Response('', 204)

        question = QuestionModel.objects(id=question_id).first()
        if not question:
            # Question doesn't exist
            return Response('', 204)

        answer = request.form['answer']

        AnswerModel.objects(question=question, answer_student=student).delete()
        # Delete existing document

        AnswerModel(question=question, answer_student=student, content=answer).save()
        # Insert new answer data

        return Response('', 201)
