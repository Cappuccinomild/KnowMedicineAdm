from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Img_set, Tag_set, Medicine, Check_log, ID_seq
from server.views.auth_views import login_required

def tag_to_txt(img_id):
        
    import os
    # 사용 예시
    # /static/yolo_model/datasets/train/images/image-0.jpg
    # /static/image/202311/IMG_00005951_20231120_151321.png
    head = './server'
    label_path = '/static/yolo_model/datasets/train/labels/'
    img_path = '/static/yolo_model/datasets/train/images/'

    img_query = Img_set.query.get(img_id)

    img_name = img_query.img_dir.split("/")[-1]

    # img 폴더에 저장되어있던 이미지 파일을
    # dataset 폴더로 이동
    os.replace(head + img_query.img_dir, head + img_path + img_name)
    
    # 이동한 이미지의 경로를 업데이트
    img_query.img_dir = img_path + img_name
    db.session.commit()
    
    # 태그를 입력하기 위한 파일을 open
    tag_file = img_name.split(".")[0]
    f = open(head + label_path + tag_file, "w")

    # 6 0.388875 0.497333 0.617250 0.486000
    for tag in Tag_set.query.filter(Tag_set.img_id == img_id).all():
        tag_list = list(map(str, [tag.class_id, tag.x, tag.y, tag.width, tag.height]))
        f.write(" ".join(tag_list))
        f.write("\n")
    
    f.close()


bp = Blueprint("model", __name__, url_prefix="/model")

@bp.route("/data_list/")
@login_required
def data_list():
    
    page = request.args.get("page", type=int, default=1)
    n_page = request.args.get("n_page", type=int, default=1)
    using_kw = request.args.get("using_kw", type=str, default="")
    using_dataset = Img_set.query.filter(Img_set.train_yn == "Y")

    # if using_kw:
    #     search = "%%{}%%".format(using_kw)
    #     using_dataset = using_dataset.filter(Medicine.name.ilike(search))
        
    using_dataset = using_dataset.paginate(page=page, per_page=50)

    medicine_list = db.session.query(
        Medicine.class_id,
        Medicine.name
    ).filter(Medicine.class_id != "").all()

    subquery = Img_set.query.filter(Img_set.train_yn == "N").subquery()
    
    n_dataset = db.session.query(
        subquery.c.img_id,
        subquery.c.date,
        subquery.c.rate,
        subquery.c.train_cnt,
        subquery.c.train_yn
    ).join(
        Tag_set, Tag_set.img_id == subquery.c.img_id
    ).group_by(subquery.c.img_id)

    n_dataset = n_dataset.paginate(page=n_page, per_page=10)

    return render_template("model/data_list.html", 
                           current_menu="data_list",
                           using_dataset = using_dataset,
                           n_dataset = n_dataset,
                           page = page,
                           using_kw = using_kw,
                           medicine_list = medicine_list)

@bp.route("/data_q_list/<int:page>/<string:train_yn>/<string:class_id>")
@login_required
def data_q_list(page, train_yn, class_id):
    print(page, train_yn)

    print(train_yn == "Y")
    # train_yn이 Y인 경우를 불러올 경우
    if train_yn == "Y":
        
        dataset = Img_set.query.filter(Img_set.train_yn == train_yn)

        # if using_kw:
        #     search = "%%{}%%".format(using_kw)
        #     using_dataset = using_dataset.filter(Medicine.name.ilike(search))
            
        dataset = dataset.paginate(page=page, per_page=50)

    # train_yn이 N인 경우를 불러올 경우
    # 태그 데이터가 존재하지 않거나 
    elif train_yn == "N":

        subquery = Img_set.query.filter(Img_set.train_yn == "N").subquery()
        
        dataset = db.session.query(
            subquery.c.img_id,
            subquery.c.date,
            subquery.c.rate,
            subquery.c.train_cnt,
            subquery.c.train_yn
        ).join(
            Tag_set, Tag_set.img_id == subquery.c.img_id
        ).group_by(subquery.c.img_id)

        dataset = dataset.paginate(page=page, per_page=10)

    else:
        return make_response(jsonify({"resp": 'not allowed'}), 304)
    
    resp = {
        "resp" : 200,
        "data" : []
    }

    #출력 데이터 양식
    for item in dataset.items:
        resp["data"].append({
            "img_id" : item.img_id,
            "train_yn" : item.train_yn,
            "train_cnt" : item.train_cnt
        })

    return jsonify(resp)

@bp.route("/yn_change/", methods = ['POST'])
@login_required
def yn_change():
    
    print(request)
    
    data = request.get_json()
    
    if data['now'] == "Y":
        to_change = "N"

    elif data['now'] == "N":
        to_change = "Y"

    else:
        return make_response("fail", 403)
    
    for img in Img_set.query.filter(Img_set.img_id.in_(data['data'])).all():
        img.train_yn = to_change

    db.session.commit()

    return make_response("success", 200)

@bp.route("/data_tag/")
@login_required
def data_tag():
    
    page = request.args.get("page", type=int, default=1)
    using_kw = request.args.get("using_kw", type=str, default="")
    using_dataset = Img_set.query.filter(Img_set.train_yn == "Y")

    # if using_kw:
    #     search = "%%{}%%".format(using_kw)
    #     using_dataset = using_dataset.filter(Medicine.name.ilike(search))
        
    using_dataset = using_dataset.paginate(page=page, per_page=10)

    medicine_list = db.session.query(
        Medicine.class_id,
        Medicine.name
    ).filter(Medicine.class_id != "").all()

    return render_template("model/data_tag.html", 
                           current_menu="data_tag",
                           using_dataset = using_dataset,
                           page = page,
                           using_kw = using_kw,
                           medicine_list = medicine_list)

@bp.route("/data_detail/<img_id>")
@login_required
def data_detail(img_id):
    
    img_dir = Img_set.query.filter(Img_set.img_id == img_id).first().img_dir
    subquery = Tag_set.query.filter(Tag_set.img_id == img_id).subquery()
    
    tag_list = db.session.query(
        subquery.c.tag_id,
        subquery.c.x,
        subquery.c.y,
        subquery.c.width,
        subquery.c.height,
        subquery.c.class_id,
        Medicine.name
    ).join(
        Medicine, Medicine.class_id == subquery.c.class_id
    )

    print(tag_list.statement)
    
    tag_list = tag_list.all()

    response_list = {
        'id': img_id,
        'path': img_dir,
        'data':[]
    }

    if tag_list is None:
        return jsonify({'error': '태그 정보를 찾을 수 없습니다.'}), 404

    for tag in tag_list:
        
        response_list['data'].append({
            'tag_id': tag.tag_id,
            'name' : tag.name,
            'left': tag.x,
            'top': tag.y,
            'width': tag.width,
            'height': tag.height,
            'class_id': tag.class_id
        })
    
    print(response_list)
    return response_list
    

@bp.route("/learning/")
@login_required
def learning():
    from ultralytics import YOLO

    model = YOLO('./yolo_model/best.pt')

    model.train(data='./yolo_model/data.yaml' , epochs=200, patience=50)
    
    return "complete"

@bp.route("/model_update/", methods = ['POST'])
@login_required
def model_update():
    
    return "complete"

@bp.route("/tag_save/", methods = ['POST'])
@login_required
def tag_save():
    
    print(request)
    
    data = request.get_json()
    
    tag_id_list = []

    for item in data['data']:
        
        print(item)
        
        tag_id_list.append({
            "tag_id": item['tag_id'] if item['tag_id'] else ID_seq.call_ID("TAG"),
            "img_id": data['id'],
            "class_id": item['class_id'],
            "x": item['left'],
            "y": item['top'],
            "width": item['width'],
            "height": item['height'],
        })
        
    Tag_set.query.filter(Tag_set.img_id == data['id']).delete()
    
    db.session.commit()

    for item in tag_id_list:
        
        Tag_set.add_tag(**item)

    

    return make_response("success", 200)

# 로그 분석 페이지
@bp.route('/analysis_log/')
@login_required
def analysis_log():
    
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")

    from sqlalchemy import func

    log_list = db.session.query(
        Check_log.img_id,
        Check_log.user_id,
        Check_log.class_id,
        Check_log.rate,
        Check_log.date,
        func.avg(Check_log.rate).label('average_rate')
    ).group_by(Check_log.img_id)
    
    if kw:
        search = "%%{}%%".format(kw)
        # log_list = log_list.filter(Check_log.check_log_id.ilike(search))
        # query = query.filter(Check_log.check_log_id.ilike(search))
        log_list = log_list.filter(Check_log.check_log_id.ilike(search)).distinct()
        
    log_list = log_list.paginate(page=page, per_page=10)
    # log_list = query.paginate(page=page, per_page=10)
    
    medicine_list = db.session.query(
        Medicine.class_id,
        Medicine.name
    ).filter(Medicine.class_id != "").all()
    
    # UTC 시각을 한국 시각으로 변환
    # for log in log_list.items:
    #     log.date = log.date.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=9)))

    return render_template("model/analysis_log.html",
                           current_menu="analysis_log",
                           medicine_list = medicine_list,
                           log_list=log_list,
                           page=page,
                           kw=kw) 

@bp.route("/log_to_tag/", methods = ['POST'])
@login_required
def log_to_tag():
    
    print(request)
    
    data = request.get_json()
    
    tag_id_list = []

    for item in data['data']:
        
        print(item)
        
        tag_id_list.append({
            "tag_id": ID_seq.call_ID("TAG"),
            "img_id": data['id'],
            "class_id": item['class_id'],
            "x": item['left'],
            "y": item['top'],
            "width": item['width'],
            "height": item['height'],
        })

    Tag_set.query.filter(Tag_set.img_id == data['id']).delete()
    
    db.session.commit()

    for item in tag_id_list:
        
        Tag_set.add_tag(**item)

    tag_to_txt(data['id'])

    return make_response("success", 200)

@bp.route("/log_detail/<img_id>")
@login_required
def log_detail(img_id):
    
    img_dir = Img_set.query.filter(Img_set.img_id == img_id).first().img_dir
    subquery = Check_log.query.filter(Check_log.img_id == img_id).subquery()
    
    tag_list = db.session.query(
        subquery.c.check_log_id,
        subquery.c.x,
        subquery.c.y,
        subquery.c.width,
        subquery.c.height,
        subquery.c.class_id,
        Medicine.name
    ).join(
        Medicine, Medicine.class_id == subquery.c.class_id
    )

    print(tag_list.statement)
    
    tag_list = tag_list.all()

    response_list = {
        'id': img_id,
        'path': img_dir,
        'data':[]
    }

    if tag_list is None:
        return jsonify({'error': '태그 정보를 찾을 수 없습니다.'}), 404

    for tag in tag_list:
        
        response_list['data'].append({
            'check_log_id': tag.check_log_id,
            'name' : tag.name,
            'left': tag.x,
            'top': tag.y,
            'width': tag.width,
            'height': tag.height,
            'class_id': tag.class_id
        })
    
    print(response_list)
    return response_list
    

# 임시로 만든 페이지
@bp.route('/test/')
def test():
    
    import os
    # 사용 예시
    head = './server'
    label_path = '/static/yolo_model/datasets/train/labels/'
    img_path = '/static/yolo_model/datasets/train/images'

    img_list = [file for file in os.listdir(head + img_path) if os.path.isfile(os.path.join(head + img_path, file))]

    for img in img_list:
        label = img.replace(".jpg", ".txt")

        image_data = {}
        f = open(head + label_path + label, "r")

        image_data['img_id'] = ID_seq.call_ID('IMG')

        image_data['user_id'] = "admin"
        image_data['img_dir'] = img_path + "/" + img
        image_data['train_yn'] = "Y"
        image_data['rate'] = 0

        print(image_data)
        Img_set.add_img(**image_data)
        line = f.readline()
        while line:
            line.replace('\n', '')
            tag_item = {}
            tag_item['tag_id'] = ID_seq.call_ID('TAG')
            tag_item['img_id'] = image_data['img_id']
            tag_item['class_id'], tag_item['x'], tag_item['y'], tag_item['width'], tag_item['height'] = map(float, line.split(" "))
            tag_item['class_id'] = str(int(tag_item['class_id']))

            print(tag_item)
            Tag_set.add_tag(**tag_item)
            line = f.readline()
    return "complete"
    
    