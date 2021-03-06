from binascii import hexlify
from datetime import datetime
from hashlib import pbkdf2_hmac

from flask import Blueprint, Response, current_app, request
from flask_restful import Api


from app.views.v1 import BaseResource
from app.views.v1 import admin_only


from app.models.account import StudentModel, AdminModel

api = Api(Blueprint('admin-signup-api', __name__))
api.prefix = '/admin'


@api.resource('/new-account')
class NewAccount(BaseResource):
    
    @admin_only
    def post(self):
        """
        새로운 관리자 계정 생성
        """
        id = request.form['id']
        pw = request.form['pw']
        name = request.form['name']

        student = StudentModel.objects(id=id).first()
        admin = AdminModel.objects(id=id).first()
        if any((student, admin)):
            return Response('', 204)

        # --- Create new admin account_admin

        pw = hexlify(pbkdf2_hmac(
            hash_name='sha256',
            password=pw.encode(),
            salt=current_app.secret_key.encode(),
            iterations=100000
        )).decode('utf-8')
        # pbkdf2_hmac hash with salt(secret key) and 100000 iteration

        AdminModel(id=id, pw=pw, name=name, signup_time=datetime.now()).save()

        return Response('', 201)
