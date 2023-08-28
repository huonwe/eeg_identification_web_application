# encoding:utf-8
import re

from flask import current_app, request, jsonify
from authlib.jose import jwt, JoseError
import functools


def create_token():
    header = {'alg': 'HS256'}
    
    key = current_app.config['SECRET_KEY']
    data = {}
    token = jwt.encode(header=header, payload=data, key=key)
    return token


def verify_token(token):
    key = current_app.config['SECRET_KEY']
    try:
        data = jwt.decode(token, key)
        print(data)
    except Exception:
        return False

    return True


def login_required(view_func):
    @functools.wraps(view_func)
    def verify(*args, **kwargs):
        try:
            # 在请求头上拿到token
            token = request.cookies.get('token')
        except Exception:
            # 没接收的到token,给前端抛出错误
            return jsonify(code=200, msg='token required')
            # return render_template('')
            
        yes = verify_token(token)
        if not yes:
            return jsonify(code=200, url='/', msg='no access')

        return view_func(*args, **kwargs)

    return verify


def inputs_valid_check(inputs):
    if inputs is None:
        return False
    id = inputs["id"]
    password = inputs['password']
    if not all([id, password]):
        return False
    _id_s = re.match("[A-Z][a-z]", id)
    if _id_s or len(id) != 8:
        return False
    _id_n = re.match("[0-9]{8}", id)
    if len(_id_n.group()) != 8:
        return False
    if len(password)<6 or len(password)>20:
        return False
    _p = re.match("[a-zA-Z0-9_'@]{6,20}", password)
    if _p.group() != password:
        return False
    return True
