
from flask import request
from flask import jsonify
from flask import session
from flask import Response
from flask import make_response
from flask import redirect, url_for, send_from_directory, render_template

# JWT 확장 라이브러리
from flask_jwt_extended import *

import json
import sqlite3

from PIL import Image

import pandas as pd
import numpy as np
import datetime
import cv2
import os

import sqlite3
from PIL import Image

from ultralytics import YOLO

yolo_model = YOLO("../img_model.pt")

def PIL2OpenCV(pil_image):
    
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def yolo_img_predict(img):

    results = yolo_model(img)

    for r in results:

        # show result in server
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.show()  # show image

        correct_rate = r.boxes.conf
        label = r.boxes.cls

        print(r.boxes)

    rate_list = []
    label_list = []

    low_accuracy = []
    for rate, label in zip(correct_rate, label):

        if rate >= 0.8:
            rate_list.append(rate)
            label_list.append(label)

        else:
            low_accuracy.append([rate, label])

    return rate_list, label_list, low_accuracy, im

def get_medicine_data(label):

    con = sqlite3.connect("./data.db")

    cur = con.cursor()

    json_skeleton = {
        "title" : "medicine_resp",
        "resp" : 200,
        "medicine_list" : []
    }

    # 1개의 객체만 들어올 경우
    # prev (8,)
    # mid ('8',) 이 부분의 콤마를 제거함
    # now ('8')
    label = str(tuple(map(str, label)))
    label = label.replace(",)", ")")
    
    # in 연산을 이용해 검출된 모든 객체를 추출 할 수 있도록 함.
    result = pd.read_sql_query("SELECT * FROM MEDICINE WHERE MED_ID IN " + label, con)

    json_skeleton['medicine_list'] = result.to_dict(orient= "records")

    con.close()

    return json_skeleton

def save_nonelabel(id, img, low_accuracy, res_img):
    
    path_month = datetime.datetime.now().strftime('%Y%m')
    fname_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    path = './image/none_labeled/'+ path_month

    res_path = './image/none_labeled_result/'+ path_month

    fname = "_".join([id, fname_time])

    fname += ".png"

    os.makedirs(path,exist_ok=True)
    os.makedirs(res_path,exist_ok=True)

    print(path)
    print(fname)

    cv2.imwrite(path + "/" + fname, img)
    cv2.imwrite(res_path + "/" + fname, res_img)

def id_validation(id, pwd):

    with sqlite3.connect("./data.db") as con:

        cur = con.cursor()

        cur.execute("SELECT * FROM USER WHERE USR_ID = '" + id + "' AND Password = '" + pwd + "'")

    return len(cur.fetchall())


from flask import Blueprint, render_template

bp = Blueprint('conn', __name__, url_prefix='/')

from server.models import Medicine

@bp.route('/')
def index():
    med_list = Medicine.query.order_by(Medicine.MED_ID.desc())
    return render_template('test/test.html', med_list=med_list)

@bp.route('/')
def hello_world():
    return 'Hello World!'

# ID pwd를 검증한 후 200 코드 return
# JWT를 이용해 토큰 전달
@bp.route('/login', methods = ['POST'])
def ID_json_handler():

    # 유저 json 입력을 parsing 함
    if request.is_json:

        content = request.get_json()

        user_id = content['username']
        user_pw = content['password']
        
        print(content)
        # user id와 pw 검증
        validation_flag = id_validation(user_id, user_pw)
        
        # id와 pwd가 일치하는 결과가 1개 뿐일때.
        if validation_flag == 1:

            # user_id에 관한 토큰을 작성해서 유저에게 넘김
            # 유효기간 설정 코드 expires_delta=datetime.timedelta(minutes = 10)
            access_token = create_access_token(identity=user_id, expires_delta=False)

            return make_response(
                jsonify({"result": 'login_success', 
                        "access_token" : access_token}), 200)
        
        else:
            return make_response(jsonify({"resp": 'not allowed'}), 401)
    
    # 입력값이 json 형식이 아닐경우
    else:
        return make_response(jsonify({"resp": 'not allowed'}), 404)

# 200 코드 return 후 session release 기능을 구현 예정
@bp.route('/logout', methods = ['POST'])
def logout_json_handler():

    print (request.is_json)
    content = request.get_json()
    print (content)

    return make_response(jsonify({"resp": "logout_success"}), 200)

# 객체 인식 및 결과 전송
@bp.route('/photo', methods = ['POST'])
@jwt_required()
def photo_json_handler():
    
    current_user = get_jwt_identity()
    if current_user is None:
        return make_response("none", 401)
    
    #user ID
    user_id = request.form['id']
    photo = request.files['photo']

    # 이미지 cv2 파일로 변환
    photo = Image.open(photo)
    # photo.show()
    photo = PIL2OpenCV(photo)
        
    correct_rate, label, low_accuracy, res_img = yolo_img_predict(photo)
    
    # 검출 결과 이미지 cv2 파일로 변환
    res_img = PIL2OpenCV(res_img)

    yolo_result = get_medicine_data(tuple(map(int, label)))

    # 검출 데이터 확인 여부
    item_len = len(yolo_result['medicine_list'])

    # 검출 데이터가 존재하지 않을 경우
    print("low", len(low_accuracy))
    if item_len == 0 or len(low_accuracy) != 0:
        save_nonelabel(user_id, photo, low_accuracy, res_img)
    
    # 검출된 데이터가 없다면 빈 "medicine_list"를 전송하고
    # 클라이언트 단에서 처리 할 수 있도록 함.
    yolo_result = json.dumps(yolo_result, ensure_ascii=False)

    
    return make_response(yolo_result, 200)

# 회원가입 링크
@bp.route('/signup', methods = ['POST'])
def signup_json_handler():

    # 유저 json 입력을 parsing 함
    if request.is_json:

        content = request.get_json()

        user_data = list(content.values())
        print(user_data)
        
        user_id = user_data[0]

        con = sqlite3.connect("./data.db")

        cur = con.cursor()

        # 중복 ID 확인
        cur.execute("SELECT * FROM USER WHERE USR_ID = '" + user_id + "'")

        validation_flag = len(cur.fetchall())

        # 이미 존재하는 회원 ID
        if validation_flag == 0:
            
            # DB에 데이터 입력
            cur.execute("INSERT INTO USER(ID, Password, Name, Birthday, Gender, Phone) VALUES(?,?,?,?,?,?)", (user_data))
            
            # 수정 적용
            con.commit()

            con.close()

            access_token = create_access_token(identity=user_id, expires_delta=False)
            print(access_token)
            return make_response(
                jsonify({"result": 'login_success', 
                        "access_token" : access_token}), 200)

        else:

            return make_response(jsonify({"resp": 'not allowed'}), 401)
        
    # 입력값이 json 형식이 아닐경우
    else:
        return make_response(jsonify({"resp": 'not allowed'}), 401)

# 회원가입 링크
@bp.route('/idValidation', methods = ['POST'])
def is_valid_id():

    # 유저 json 입력을 parsing 함
    if request.is_json:

        content = request.get_json()
        
        user_id = content['id']
        
        with sqlite3.connect("./data.db") as con:

            cur = con.cursor()

            # 중복 ID 확인
            cur.execute("SELECT * FROM USER WHERE USR_ID = '" + user_id + "'")

            validation_flag = len(cur.fetchall())

        # 존재하지 않는 ID
        if validation_flag == 0:
            
            return make_response(
                jsonify({"result": 'valid_id'}), 200)
        # 이미 존재하는 회원 ID
        else:

            return make_response(jsonify({"resp": 'invalid_id'}), 401)
        
    # 입력값이 json 형식이 아닐경우
    else:
        return make_response(jsonify({"resp": 'not allowed'}), 401)


# function test site
@bp.route('/test', methods = ['POST'])
def test():
    return "test"
