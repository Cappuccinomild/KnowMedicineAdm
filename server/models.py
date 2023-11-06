from server import db
from datetime import datetime

# 의약품 DB
class Medicine(db.Model):
    med_id = db.Column(db.String(12), primary_key=True, comment = "의약품 DB ID") 
    class_id = db.Column(db.String(12), nullable=True, comment = "모델 class ID") 
    name = db.Column(db.String(30), nullable=False, comment = "의약품 이름")
    thumbLink = db.Column(db.String(255), nullable=True, comment = "썸네일 위치")
    effect_type = db.Column(db.String(2), nullable=False, comment = "코로나키트 K 일반약품 N")
    effect = db.Column(db.Text, nullable=True, comment = "효능")
    usage_type = db.Column(db.String(2), nullable=False, comment = "코로나키트 K 일반약품 N")
    usage = db.Column(db.Text, nullable=True, comment = "용법")
    caution_type = db.Column(db.String(2), nullable=False, comment = "코로나키트 K 일반약품 N")
    caution = db.Column(db.Text, nullable=True, comment = "주의사항")

# 
class User(db.Model):
    user_id = db.Column(db.String(12), primary_key=True, comment = "유저 ID")
    password = db.Column(db.String(200), nullable=True, comment = "유저 패스워드")
    name = db.Column(db.String(20), nullable=True, comment = "유저 이름")
    birthday = db.Column(db.DateTime, nullable=True, comment = "유저 생년월일")
    gender = db.Column(db.String(2), nullable=True, comment = "유저 성별")
    phone = db.Column(db.String(17), nullable=True, comment = "유저 전화번호")

class User_log(db.Model):
    user_log_id = db.Column(db.String(12), primary_key=True, comment = "사진 전송 로그 ID")
    user_id = db.Column(db.String(12), nullable=False, comment = "유저 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    rate = db.Column(db.Integer, nullable=False, comment = "분석 결과 평균 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "전송날짜")

class Check_log(db.Model):
    check_log_id = db.Column(db.String(12), primary_key=True, comment = "사진 분석 로그 ID")
    user_log_id = db.Column(db.String(12), nullable=False, comment = "사진 전송 로그 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    med_id = db.Column(db.String(12), nullable=True, comment = "분석결과 의약품 ID")
    start_x = db.Column(db.Float, nullable=True, comment = "좌표 x1")
    start_y = db.Column(db.Float, nullable=True, comment = "좌표 y1")
    end_x = db.Column(db.Float, nullable=True, comment = "좌표 x2")
    end_y = db.Column(db.Float, nullable=True, comment = "좌표 y2")
    rate = db.Column(db.Integer, nullable=True, comment = "분석 결과 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "분석날짜")

# key, seq 모음
class ID_seq(db.Model):
    ID = db.Column(db.String(3), primary_key=True, comment = "키 앞자리 세자리")
    seq = db.Column(db.Integer, nullable=False, comment = "키 번호")

class Img_set(db.Model):
    img_id = db.Column(db.String(12), primary_key=True, comment = "이미지 ID")
    user_id = db.Column(db.String(12), nullable=True, comment = "이미지 출처 ID")
    img_dir = db.Column(db.String(40), nullable=False, comment = "이미지 저장 장소")
    train_cnt = db.Column(db.Integer, nullable=False, default=0, comment = "학습에 사용된 횟수")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "저장된 날짜")

class Tag_set(db.Model):
    tag_id = db.Column(db.String(12), primary_key=True, comment = "태그 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    med_id = db.Column(db.String(12), nullable=False, comment = "태깅 의약품 ID")
    start_x = db.Column(db.Float, nullable=True, comment = "좌표 x1")
    start_y = db.Column(db.Float, nullable=True, comment = "좌표 y1")
    end_x = db.Column(db.Float, nullable=True, comment = "좌표 x2")
    end_y = db.Column(db.Float, nullable=True, comment = "좌표 y2")
