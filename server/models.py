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

    def id_validation(id, pwd=None):

        # pwd가 주어지지 않았을 때
        if pwd is None:
            user = User.query.filter(User.user_id == id).all()
        else:
            user = User.query.filter(User.user_id == id, User.password == pwd).all()

        return len(user)

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

    @staticmethod
    def call_ID(id):
        try:
            # 하나의 결과만 예상한다면 all() 대신 first()를 사용합니다.
            query = ID_seq.query.filter(ID_seq.ID == id).first()

            if query:
                return_seq = str(query.seq).zfill(8)
                query.seq += 1

                db.session.commit()

                return f"{id}_{return_seq}"

            else:
                return None
        except Exception as e:
            # 데이터베이스 작업 중 예외를 처리합니다. 예를 들어 오류를 기록합니다.
            print(f"오류: {e}")
            db.session.rollback()  # 오류 발생 시 변경 사항을 롤백합니다.
            return None

class Img_set(db.Model):
    img_id = db.Column(db.String(12), primary_key=True, comment = "이미지 ID")
    user_id = db.Column(db.String(12), nullable=True, comment = "이미지 출처 ID")
    img_dir = db.Column(db.Text, nullable=False, comment = "이미지 저장 장소")
    train_cnt = db.Column(db.Integer, nullable=False, default=0, comment = "학습에 사용된 횟수")
    rate = db.Column(db.Float, nullable=False, comment = "분석 결과 평균 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "저장된 날짜")

    def add_img(img_id, user_id, img_dir, rate):
        """
        Add image data to the database.

        :param img_id: Image ID.
        :param user_id: User ID.
        :param img_dir: Image directory.
        :param train_cnt: Number of times the image was used for training.
        """
        if not all([img_id, user_id, img_dir]):
            print([img_id, user_id, img_dir])
            raise ValueError("Image data should contain img_id, user_id, img_dir, and rate as valid inputs.")

        new_img = Img_set(
            img_id=img_id,
            user_id=user_id,
            img_dir=img_dir,
            train_cnt=0,
            rate=rate,
            date=datetime.utcnow()
        )

        db.session.add(new_img)
        db.session.commit()

class Tag_set(db.Model):
    tag_id = db.Column(db.String(12), primary_key=True, comment = "태그 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    med_id = db.Column(db.String(12), nullable=False, comment = "태깅 의약품 ID")
    rate = db.Column(db.Float, nullable=False, comment = "분석 정확도")
    start_x = db.Column(db.Float, nullable=True, comment = "좌표 x1")
    start_y = db.Column(db.Float, nullable=True, comment = "좌표 y1")
    end_x = db.Column(db.Float, nullable=True, comment = "좌표 x2")
    end_y = db.Column(db.Float, nullable=True, comment = "좌표 y2")

    def add_tag(tag_id, img_id, med_id, rate, start_x=None, start_y=None, end_x=None, end_y=None):
        """
        Add tag data to the database.

        :param img_id: Image ID.
        :param med_id: Tagged medicine ID.
        :param start_x: Starting x-coordinate (optional).
        :param start_y: Starting y-coordinate (optional).
        :param end_x: Ending x-coordinate (optional).
        :param end_y: Ending y-coordinate (optional).
        """
        if not all([img_id, med_id]):
            raise ValueError("Image ID and medicine ID are required for tagging.")

        new_tag = Tag_set(
            tag_id = tag_id,
            img_id = img_id,
            med_id = med_id,
            rate = rate,
            start_x = start_x,
            start_y = start_y,
            end_x = end_x,
            end_y = end_y
        )

        db.session.add(new_tag)
        db.session.commit()