from flask import Flask
from flask import request
from flask import jsonify
from flask import session
from flask import Response
from flask import make_response
from flask import redirect, url_for, send_from_directory, render_template

from server.models import Model_list

# JWT 확장 라이브러리
from flask_jwt_extended import *

import os

import json
import sqlite3
from ultralytics import YOLO
import pandas as pd
import numpy as np
import datetime
import cv2
from PIL import Image

def PIL2OpenCV(pil_image):
    
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# xy xy 좌표로 이루어진 직사각형을
# 좌측 상단 xy 좌표와 width, height 좌표로 변환
def xyxy_to_xywh(xyxy, img):

    img_y, img_x, rgb = img.shape

    x1, y1, x2, y2 = xyxy
    width = x2 - x1
    height = y2 - y1
    x = x1 + width / 2
    y = y1 + height / 2
    return x/img_x, y/img_y, width/img_x, height/img_y

# 이미지 분석, 로그저장
def yolo_img_predict(id, img):
    
    model_dir = Model_list.query.filter(Model_list.using=="Y").first().model_dir
    print(model_dir)
    yolo_model = YOLO(model_dir)

    results = yolo_model(img)

    from server.models import ID_seq, Img_set, Check_log 
    
    image_data = {}
    
    for r in results:

        # show result in server
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.show()  # show image
        
        image_data['img_id'] = ID_seq.call_ID('IMG')

        path_month = datetime.datetime.now().strftime('%Y%m')
        fname_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        # 이미지 저장위치 생성
        head = './server'
        path = '/static/image/' + path_month
        
        fname = "_".join([image_data['img_id'], fname_time])
        fname += ".png"

        correct_rate = r.boxes.conf
        label = r.boxes.cls

        bbox_xyxy = r.boxes.xyxy.tolist()

        # print(len(correct_rate))

        # 이미지 저장
        os.makedirs(head + path,exist_ok=True)
        cv2.imwrite(head + path + "/" + fname, img)

        image_data['user_id'] = id
        image_data['img_dir'] = path + "/" + fname


        
        # 이미지의 평균 정확도 계산
        image_data['rate'] = np.mean(np.array(correct_rate))

        # 이미지 입력
        print(image_data)
        Img_set.add_img(**image_data)

    rate_list = []
    label_list = []

    low_accuracy = []

    for rate, label, xyxy in zip(correct_rate, label, bbox_xyxy):
        
        
        # init tag data
        log_data = {}
        print(str(int(label.item())))
        log_data['check_log_id'] = ID_seq.call_ID('LOG')
        log_data['user_id'] = id
        log_data['img_id'] = image_data['img_id']
        log_data['class_id'] = str(int(label.item()))
        log_data['rate'] = rate.item()

        # yolo 라벨 데이터는 xywh 로 저장되므로 변환이 필요함
        # 왼쪽 위가 0.0
        log_data['x'], log_data['y'], log_data['width'], log_data['height'] = xyxy_to_xywh(xyxy, img)

        print(log_data)
        # save tag data to db
        Check_log.add_check_log(**log_data)

        if rate >= 0.8:
            rate_list.append(rate)
            label_list.append(label)

        else:
            low_accuracy.append([rate, label])

    return rate_list, label_list, low_accuracy, img

# 라벨 명을 이용한 의약품 리스트 추출
def get_medicine_data(label):

    json_skeleton = {
        "title" : "medicine_resp",
        "resp" : 200,
        "medicine_list" : []
    }

    from server.models import Medicine
    # SQLAlchemy ORM을 사용한 쿼리
    result = Medicine.query.filter(Medicine.class_id.in_(label)).all()

    # 결과를 딕셔너리로 변환하여 리스트에 추가
    medicine_list = [item.__dict__ for item in result]

    # Remove unnecessary keys from each dictionary
    for med in medicine_list:
        med.pop('_sa_instance_state', None)

    json_skeleton['medicine_list'] = medicine_list

    return json_skeleton

from flask import Blueprint, render_template

bp = Blueprint('api', __name__, url_prefix='/')

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
        from server.models import User
        # user id와 pw 검증
        validation_flag = User.id_validation(user_id, user_pw)
        
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
        
    correct_rate, label, low_accuracy, res_img = yolo_img_predict(user_id, photo)
    
    # 검출 결과 이미지 cv2 파일로 변환
    res_img = PIL2OpenCV(res_img)

    yolo_result = get_medicine_data(tuple(map(int, label)))
    
    '''
    # 이전 미검출 데이터 저장코드
    # 검출 데이터 확인 여부
    item_len = len(yolo_result['medicine_list'])

    # 검출 데이터가 존재하지 않을 경우
    print("low", len(low_accuracy))
    if item_len == 0 or len(low_accuracy) != 0:
        save_nonelabel(user_id, photo, low_accuracy, res_img)
    '''
    
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
        print(content)
        user_data = list(content.values())
        print(user_data)
        
        user_id = user_data[0]

        from server.models import User
    
        validation_flag = User.id_validation(user_id)

        # 이미 존재하는 회원 ID
        if validation_flag == 0:
            
            from server import db

            db.session.add(User(**content))
            db.session.commit()

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
        
        from server.models import User
    
        validation_flag = User.id_validation(user_id)

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

