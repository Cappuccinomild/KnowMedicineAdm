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

    def get_using():
        using_list = db.session.query(
            Medicine.class_id,
            Medicine.name
        )
        return using_list.filter(Medicine.class_id != "").all()

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
    user_id = db.Column(db.String(12), nullable=False, comment = "사진 전송자 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    class_id = db.Column(db.String(12), nullable=False, comment = "태깅 의약품 class ID")
    x = db.Column(db.Float, nullable=True, comment = "좌표 x1")
    y = db.Column(db.Float, nullable=True, comment = "좌표 y1")
    width = db.Column(db.Float, nullable=True, comment = "너비")
    height = db.Column(db.Float, nullable=True, comment = "높이")
    rate = db.Column(db.Float, nullable=True, comment = "분석 결과 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "분석날짜")

    def add_check_log(check_log_id, user_id, img_id, class_id, rate, x=None, y=None, width=None, height=None):
        """
        Add tag data to the database.

        :param img_id: Image ID.
        :param med_id: Tagged medicine ID.
        :param x: Starting x-coordinate (optional).
        :param y: Starting y-coordinate (optional).
        :param width: Ending width (optional).
        :param height: Ending height (optional).
        """
        if not all([img_id, class_id]):
            raise ValueError("Image ID and medicine ID are required for tagging.")

        new_tag = Check_log(
            check_log_id = check_log_id,
            user_id = user_id,
            img_id = img_id,
            class_id = class_id,
            x = x,
            y = y,
            width = width,
            height = height,
            rate = rate,
            date = datetime.utcnow()
        )

        db.session.add(new_tag)
        db.session.commit()
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
    train_yn = db.Column(db.String(2), nullable=False, default = "N", comment = "학습 사용 여부")
    rate = db.Column(db.Float, nullable=True, comment = "분석 결과 평균 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "저장된 날짜")

    def add_img(img_id, user_id, img_dir, rate, train_yn="N"):
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
            train_yn=train_yn,
            rate=rate,
            date=datetime.utcnow()
        )

        db.session.add(new_img)
        db.session.commit()

class Tag_set(db.Model):
    tag_id = db.Column(db.String(12), primary_key=True, comment = "태그 ID")
    img_id = db.Column(db.String(12), nullable=False, comment = "이미지 ID")
    class_id = db.Column(db.String(12), nullable=False, comment = "태깅 의약품 class ID")
    x = db.Column(db.Float, nullable=True, comment = "좌표 x1")
    y = db.Column(db.Float, nullable=True, comment = "좌표 y1")
    width = db.Column(db.Float, nullable=True, comment = "너비")
    height = db.Column(db.Float, nullable=True, comment = "높이")

    def add_tag(tag_id, img_id, class_id, x=None, y=None, width=None, height=None):
        """
        Add tag data to the database.

        :param img_id: Image ID.
        :param med_id: Tagged medicine ID.
        :param x: Starting x-coordinate (optional).
        :param y: Starting y-coordinate (optional).
        :param width: Ending width (optional).
        :param height: Ending height (optional).
        """
        if not all([img_id, class_id]):
            raise ValueError("Image ID and medicine ID are required for tagging.")

        new_tag = Tag_set(
            tag_id = tag_id,
            img_id = img_id,
            class_id = class_id,
            x = x,
            y = y,
            width = width,
            height = height
        )

        db.session.add(new_tag)
        db.session.commit()

    def update_tag(tag_id, img_id=None, class_id=None, x=None, y=None, width=None, height=None):
        """
        Update tag data in the database.

        :param tag_id: Tag ID to be updated.
        :param img_id: New image ID (optional).
        :param class_id: New class ID (optional).
        :param x: New starting x-coordinate (optional).
        :param y: New starting y-coordinate (optional).
        :param width: New ending width (optional).
        :param height: New ending height (optional).
        """
        # Query the existing tag data by tag_id
        existing_tag = Tag_set.query.filter_by(tag_id=tag_id).first()

        # Check if the tag_id exists
        if not existing_tag:
            raise ValueError(f"Tag with tag_id {tag_id} does not exist.")

        # Update the tag data with new values if provided
        if img_id is not None:
            existing_tag.img_id = img_id
        if class_id is not None:
            existing_tag.class_id = class_id
        if x is not None:
            existing_tag.x = x
        if y is not None:
            existing_tag.y = y
        if width is not None:
            existing_tag.width = width
        if height is not None:
            existing_tag.height = height

        # Commit the changes to the database
        db.session.commit()

    def del_tag_by_id(img_id):
        Tag_set.query.filter(Tag_set.img_id == img_id).delete()


class Model_list(db.Model):
    model_id = db.Column(db.String(12), primary_key=True, comment = "모델 ID")
    model_dir = db.Column(db.Text, nullable=False, comment = "모델 저장 장소")
    rate = db.Column(db.Float, nullable=True, comment = "분석 결과 평균 정확도")
    maps = db.Column(db.Text, nullable=True, comment = "클래스별 정확도")
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, comment = "저장된 날짜")
    using = db.Column(db.String(2), nullable=False, default = "N", comment = "모델 사용여부")

    def add_model(model_id, model_dir, rate=None, maps=None):
        
        if not all([model_id, model_dir]):
            raise ValueError("model id and directory are required for tagging.")

        new_model = Model_list(
            model_id = model_id,
            model_dir = model_dir,
            rate = rate,
            maps = maps,
            date = datetime.utcnow(),
            using = "N"
        )

        db.session.add(new_model)
        db.session.commit()

    def update_model(model_id, model_dir=None, rate=None, date=None, maps=None, using=None):

        
        """
        Update model data in the database.
        """
        # Query the existing model data by model_id
        existing_model = Model_list.query.get(model_id)

        # Check if the model_id exists
        if not existing_model:
            raise ValueError(f"Tag with tag_id {model_id} does not exist.")

        # Update the tag data with new values if provided
        if model_dir is not None:
            existing_model.model_dir = model_dir
        if rate is not None:
            existing_model.rate = rate
        if date is not None:
            existing_model.date = date
        if using is not None:
            existing_model.using = using

        if maps is not None:
            existing_model.maps = maps

        # Commit the changes to the database
        db.session.commit()

    def del_model(model_id, model_dir=None, rate=None, date=None, using=None):
        """
        delete model data in the database.
        """
        # Query the existing model data by model_id
        model = Model_list.query.get(model_id)

        pt_dir = model.model_dir

        db.session.delete(model)
        db.session.commit()

        return pt_dir
        