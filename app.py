# encoding=utf-8
import os
from flask import Flask, render_template, Response, request, redirect, jsonify, make_response
import json

import numpy as np
from numpy import byte
from navigator import Navigator
import time
import hashlib
import h5py
import torch

from scipy.io import loadmat
from mne.io import concatenate_raws, read_raw_edf
import mne

from web_utils import *

app = Flask(__name__)
app.secret_key = 'huonwe'

nav = Navigator()

now = byte(time.time())
secret = hashlib.md5(now).hexdigest()
# print(secret)

with open('data','r') as f:
    password = f.read()
if not password:
    with open('data','w') as f:
        f.writelines("123456")
with open('data','r') as f:
    password = f.read()


@app.route("/",methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login_verify():
    passwd = request.form['password']
    resp = Response()
    if passwd == password:
        
        token = create_token()
        resp.data = "登陆成功"
        resp.set_cookie('token', token)
        # print(resp)
        return resp
    resp.data = "登陆失败"
    return resp

@app.route("/index",methods=["GET"])
@login_required
def index():
    return render_template("index.html")

@app.route("/views/list",methods=["GET"])
def list():
    arg = request.args
    # print(arg)
    if arg['username'] and arg['status']:
        return render_template("views/list.html",eegList=nav.eegList(Name=arg['username'],Status=arg['status']),searchValue=arg['username'])
    if arg['username']:
        return render_template("views/list.html",eegList=nav.eegList(Name=arg['username']),searchValue=arg['username'])
    if arg['status']:
        return render_template("views/list.html",eegList=nav.eegList(Status=arg['status']),searchValue=arg['username'])
    return render_template("views/list.html",eegList=nav.eegList(),searchValue=arg['username'])

@app.route("/views/map",methods=["GET"])
def map():
    arg = request.args
    dist_list = nav.distMap(arg['username'])
    # print(dist_list)
    return render_template("views/map.html",distList=dist_list)
@app.route("/reg",methods=['POST'])
def reg():
    # print(request.form)
    # print(request.files)
    if len(request.files) != 1:
        return jsonify(code=201,msg="File Read Failed")
    file = request.files.getlist('file')[0]
    filename = file.filename
    data = eval(request.form['data'])
    name = data['Username']
    extro = data['Extro']

    if not filename.endswith(('.mat','.edf')):
        print(filename)
        return jsonify(code=201,msg="File Must Endwith .mat")
    path = os.path.join(nav.EEGDATA,filename)
    file.save(path)
    if filename.endswith('.mat'):
        dict_data = loadmat(path)
        try:
            eeg = np.array(dict_data["temp_data"])
        except KeyError:
            eeg = np.array(dict_data["epoch_data"][:-1,:])
    elif filename.endswith('.edf'):
        raw = read_raw_edf(path,preload=True)
        eeg,_ = raw[:,160:160+160]
    code, msg = nav.reg(torch.Tensor(eeg),name,extro)
    print("REG RESULT: ",msg)
    resp = jsonify(code=code,msg=msg)
    resp.headers['Content-Type'] = "application/json"
    return resp

@app.route("/rec",methods=['POST'])
def rec():
    # print(request.files['file'])
    if len(request.files) != 1:
        return jsonify(code=201,msg="文件有且只能有一个")
    file = request.files.getlist('file')[0]
    filename = file.filename
    if not filename.endswith(('.mat','.edf')):
        return jsonify(code=201,msg="文件必须为.mat格式")
    
    path = os.path.join(nav.EEGDATA,filename)
    file.save(path)
    
    if filename.endswith('.mat'):
        dict_data = loadmat(path)
        try:
            eeg = np.array(dict_data["temp_data"])
        except KeyError:
            eeg = np.array(dict_data["epoch_data"][:-1,:])
    elif filename.endswith('.edf'):
        raw = read_raw_edf(path,preload=True)
        eeg,_ = raw[:,:160]
    result = nav.rec(torch.Tensor(eeg))
    if not result:
        return jsonify(code=201,msg="用户不存在")
    else:
        print("REC RESULT: ",result['name'])
        
        return jsonify(code=200,data=result['name'],msg="success")


@app.route("/update",methods=["POST"])
def update():
    if len(request.files) != 1:
        return jsonify(code=201,msg="文件有且只能有一个")
    file = request.files.getlist('file')[0]
    filename = file.filename
    if not filename.endswith(('.mat','.MAT')):
        return jsonify(code=201,msg="文件必须为.mat格式")
    path = os.path.join(nav.EEGDATA,filename)
    file.save(path)
    dict_data = h5py.File(path)
    code, msg = nav.update(torch.Tensor(dict_data["temp_data"]))
    return jsonify(code=code, msg=msg)

@app.route("/delete",methods=["GET"])
def delete():
    arg = request.args
    code,msg = nav.delete(arg['username'])
    resp = jsonify(code=code,msg=msg)
    resp.headers['Content-Type'] = "application/json"
    return resp

@app.route("/switchStatus",methods=["GET"])
def ban():
    arg = request.args
    result = nav.userStatusToggle(arg['username'])
    return jsonify(code=200,data=result,msg='success')

@app.route("/secret",methods=["GET"])
def secret():
    return 

@app.route("/sort", methods=["POST"])
def sort():
    if len(request.files) != 1:
        return jsonify(code=201,msg="File Read Failed")
    file = request.files.getlist('file')[0]
    filename = file.filename

    if not filename.endswith(('.mat','.edf')):
        print(filename)
        return jsonify(code=201,msg="File Must Endwith .mat")
    path = os.path.join(nav.EEGDATA,filename)
    file.save(path)
    if filename.endswith('.mat'):
        dict_data = loadmat(path)
        try:
            eeg = np.array(dict_data["temp_data"])
        except KeyError:
            eeg = np.array(dict_data["epoch_data"][:-1,:])
            
    elif filename.endswith('.edf'):
        raw = read_raw_edf(path,preload=True)
        eeg,_ = raw[:,:160]
    # print(eeg.shape)
    result = nav.rec(torch.Tensor(eeg))
    print("REG RESULT: ",result)
    if not result:
        resp = jsonify(code=200,msg="查无此人")
    else:
        resp = jsonify(code=200,msg=result['name']+"  "+result['extro'])
    resp.headers['Content-Type'] = "application/json"
    return resp

app.run(host='0.0.0.0', port=5500, debug=True)
