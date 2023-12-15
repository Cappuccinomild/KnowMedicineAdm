from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from flask import make_response, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Img_set, Tag_set, Medicine, Check_log, ID_seq, Model_list
from server.views.auth_views import login_required

from sqlalchemy import func

import os

# 데이터셋으로 이용하던 이미지를 제거하는 경우
def del_tag(img_id):
    # 사용 예시
    # /static/yolo_model/datasets/train/images/image-0.jpg
    # /static/image/202311/IMG_00005951_20231120_151321.png

    head = './server'
    label_path = '/static/yolo_model/datasets/train/labels/'

    img_query = Img_set.query.get(img_id)

    img_name = img_query.img_dir.split("/")[-1]
    try:
        seq_name, seq, yyyymmdd, picture = img_name.split("_")
        img_path = f"/static/image/{yyyymmdd[:-2]}/"

    except:
        img_path = "/static/image/default/"    

    

    # img 폴더에 저장되어있던 이미지 파일을
    # dataset 폴더로 이동
    os.replace(head + img_query.img_dir, head + img_path + img_name)
    
    # 이동한 이미지의 경로를 업데이트
    img_query.img_dir = img_path + img_name
    db.session.commit()
    
    # 태그를 입력하기 위한 파일을 open
    tag_file = f'{head + label_path + img_name.split(".")[0]}.txt'
    try:
        os.remove(tag_file)
    except:
        print("file none")

# 태그로 이용 할 수 있게 DB의 데이터를 텍스트파일로 저장함
def tag_to_txt(img_id):
        
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
    tag_file = f'{img_name.split(".")[0]}.txt'
    f = open(head + label_path + tag_file, "w")

    # 6 0.388875 0.497333 0.617250 0.486000
    for tag in Tag_set.query.filter(Tag_set.img_id == img_id).all():
        tag_list = list(map(str, [tag.class_id, tag.x, tag.y, tag.width, tag.height]))
        f.write(" ".join(tag_list))
        f.write("\n")
    
    f.close()

# 의약품 키워드를 기반으로 의약품의 class id를 추출
def get_id_from_keyword(keyword):
    search = "%%{}%%".format(keyword)

    # 키워드를 기반으로 class_id를 추출함
    id_list = []
    for item in Medicine.query.filter(Medicine.name.ilike(search)).all():
        id_list.append(item.class_id)

    subquery = Tag_set.query.filter(Tag_set.class_id.in_(id_list)).subquery()
    using_dataset = db.session.query(
        Img_set.img_id,
        Img_set.user_id,
        Img_set.img_dir,
        Img_set.train_cnt,
        Img_set.date,
        Img_set.rate,
        Img_set.train_yn
    ).select_from(Img_set).join(
        subquery, Img_set.img_id == subquery.c.img_id
    ).group_by(subquery.c.img_id)

    return using_dataset

bp = Blueprint("model", __name__, url_prefix="/model")

# 현재 사용중인 학습 데이터셋과 사용중이지 않은 데이터셋을 출력
@bp.route("/data_list/", methods=['GET', 'POST'])
@login_required
def data_list():
    
    params = request.form
    y_keyword = ""
    n_keyword = ""

    print(params)
    # 키워드가 존재한다면 전달받음
    if(request.method =='POST'):
        y_keyword = params['yKeyword']
        n_keyword = params['nKeyword']
    
    # 현재 사용중인 데이터셋 추출
    using_dataset = Img_set.query.filter(Img_set.train_yn == "Y")
    subquery = Img_set.query.filter(Img_set.train_yn == "N").subquery()

    # 키워드가 존재한다면 검색 결과를 출력함
    if y_keyword:
        using_dataset = get_id_from_keyword(y_keyword)

        subquery = using_dataset.filter(Img_set.train_yn == "N").subquery()
        using_dataset = using_dataset.filter(Img_set.train_yn == "Y")
        
    using_dataset = using_dataset.paginate(page=1, per_page=50)

    # 의약품 목록 추출
    medicine_list_using = Medicine.get_using()

    # 미사용 목록 추출
    
    n_dataset = db.session.query(
        subquery.c.img_id,
        subquery.c.date,
        subquery.c.rate,
        subquery.c.train_cnt,
        subquery.c.train_yn
    ).join(
        Tag_set, Tag_set.img_id == subquery.c.img_id
    ).group_by(subquery.c.img_id)

    n_dataset = n_dataset.paginate(page=1, per_page=50)

    return render_template("model/data_list.html", 
                           current_menu="data_list",
                           using_dataset = using_dataset,
                           n_dataset = n_dataset,
                           yKeyword = y_keyword,
                           nKeyword = n_keyword,
                           medicine_list_using = medicine_list_using)

# 데이터셋 검색 및 페이지 넘기기 기능
@bp.route("/data_q_list/<string:train_yn>/<int:page>/<string:keyword>")
@bp.route("/data_q_list/<string:train_yn>/<int:page>/")
@login_required
def data_q_list(page, train_yn, keyword = ""):
    print(page, train_yn)

    # 사용 여부에 따른 쿼리
    dataset = get_id_from_keyword(keyword).filter(Img_set.train_yn == train_yn)
    
    # 데이터 페이징
    dataset = dataset.paginate(page=page, per_page=15)

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

# 사용여부 변경 (data_list에서 데이터 추가 및 제거 버튼)
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

        if to_change == "N":
            del_tag(img.img_id)

        if to_change == "Y":
            tag_to_txt(img.img_id)


    db.session.commit()

    return make_response("success", 200)

# 데이터셋의 태그를 수정하는 페이지
@bp.route("/data_tag/")
@login_required
def data_tag():
    
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")
    using_dataset = Img_set.query.filter(Img_set.train_yn == "Y")

    # 키워드가 존재하면 검색결과를 출력함
    if kw:
        using_dataset = get_id_from_keyword(kw)

    using_dataset = using_dataset.paginate(page=page, per_page=10)

    # 현재 사용중인 class_id 추출, 검색어 자동완성에 사용됨
    medicine_list_using = Medicine.get_using()
    # medicine_list_all = medicine_list.all()

    return render_template("model/data_tag.html", 
                           current_menu="data_tag",
                           using_dataset = using_dataset,
                           page = page,
                           kw = kw,
                           medicine_list_using = medicine_list_using
                           )

# 구체적인 해당 img_id의 태그 정보를 불러옴
@bp.route("/data_detail/<img_id>")
@login_required
def data_detail(img_id):
    
    img_dir = Img_set.query.filter(Img_set.img_id == img_id).first().img_dir
    subquery = Tag_set.query.filter(Tag_set.img_id == img_id).subquery()
    
    # 이미지 id가 같은 tag 정보를 img와 join
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

    # 결과 form
    response_list = {
        'id': img_id,
        'path': img_dir,
        'data':[]
    }

    if tag_list is None:
        return jsonify({'error': '태그 정보를 찾을 수 없습니다.'}), 404

    # 결과 입력
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

# 사용할 모델 설정
@bp.route("/data_learning/")
@login_required
def data_learning():
    page = request.args.get("page", type=int, default=1)

    model_list = Model_list.query.paginate(page=page, per_page=10)
    
    return render_template("model/data_learning.html",
                           current_menu="data_learning",
                           model_list = model_list
                           ) 

# 서버 모델 학습
@bp.route("/learning/", methods = ['POST'])
@login_required
def learning():
    
    from ultralytics import YOLO

    model = YOLO()

    model_id = ID_seq.call_ID("MOD")

    # yaml 파일 저장
    yaml = open("./server/static/yolo_model/data.yaml", "w", encoding="utf-8")
    
    # class_id 순서대로 정렬
    using_list = sorted(Medicine.get_using(), key=lambda x: int(x[0]))

    # 약품 이름만 추출
    using_list = [item[1] for item in using_list]

    yaml.write("\n".join([
        "train: ./datasets/train",
        "val: ./datasets/valid",
        "",
        f"nc: {len(using_list)}",
        "",
        f"names: {using_list}"
    ]))

    yaml.close()

    # 모델 학습결과 저장
    result = model.train(data='./server/static/yolo_model/data.yaml' , epochs=1, patience=50,  project="server/static/yolo_model", name=model_id)
    
    # 새로운 파일 이름 생성
    from datetime import datetime

    pt_dir = str(result.save_dir)
    pt_dir = f'./{pt_dir}/weights/best.pt'

    # 평균 정확도
    mean_rate = result.maps.mean()

    # 클래스별 정확도 결과 리스트
    maps = ",".join(str(value) for value in result.maps)

    # DB 저장
    Model_list.add_model(model_id, pt_dir, mean_rate, maps)

    try:
        resp = {
            "resp" : 200,
            "data" : result
        }
    except:
        resp = {
            "resp" : 400,
            "data" : []
        }

    # 'useYn'이 'Y'인 레코드를 선택하고 'train_cnt'를 1씩 증가시킴
    db.session.query(Img_set).filter_by(useYn='Y').update({'train_cnt': Img_set.train_cnt + 1}, synchronize_session=False)

    # 변경 내용을 데이터베이스에 반영
    db.session.commit()
    
    return jsonify(resp)

# 폴더 내부의 이미지 파일 목록 추출
def get_image_files(folder_path):
    # 지원하는 이미지 파일 확장자들
    supported_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tif', '.tiff']

    image_files = []

    # 폴더 내 모든 파일에 대해 반복
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        _, file_extension = os.path.splitext(file_path)

        # 파일이 지원하는 이미지 확장자 중 하나인지 확인
        if file_extension.lower() in supported_extensions:
            image_files.append(file_path)

    return image_files

# 모델 세부 분석 결과 확인
@bp.route("/model_detail/<model_id>")
@login_required
def model_detail(model_id):
    
    print(model_id)
    save_dir = Model_list.query.get(model_id).model_dir

    save_dir = save_dir.replace("\\", "/")
    save_dir = "/".join(save_dir.split("/")[:-2])

    # 모델 이미지 데이터와 디렉토리를 결합해
    # 이미지 파일 링크를 전송함    
    data = ["/"+"/".join(item.split("/")[2:]) for item in get_image_files(save_dir)]
    try:
        resp = {
            "resp" : 200,
            "data" : data
        }
    except:
        resp = {
            "resp" : 400,
            "data" : []
        }

    return jsonify(resp)

# 미사용 중인 모델을 사용으로 변경
@bp.route("/model_update/", methods = ['POST'])
@login_required
def model_update():
    
    data = request.get_json()
    if(request.method =='POST'):
        model_id = data['model_id']
        using = data['using']
    
    

    # 이미 사용중일 경우 처리
    if using == "Y":
        if db.session.query(func.count()).filter(Model_list.using == "Y").scalar() == 1:
            return make_response("fail", 403)

    # 업데이트    
    for now_using in Model_list.query.filter(Model_list.using == "Y").all():
        now_using.using="N"
    
    db.session.commit()
    
    Model_list.update_model(model_id=model_id, using="Y")
    
    return make_response("success", 200)

# 모델 데이터 삭제
# 구현필요
@bp.route("/model_delete/<model_id>", methods = ['POST'])
@login_required
def model_delete(model_id):
    
    return "complete"

# 수정한 태그 정보를 저장함
@bp.route("/tag_save/", methods = ['POST'])
@login_required
def tag_save():
    
    print(request)
    
    data = request.get_json()

    print(data)
    
    tag_id_list = []

    # 수정된 태그 데이터 dict로 변환
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
    
    # 저장되어있던 태그 데이터 삭제
    Tag_set.del_tag_by_id(data['id'])
    
    db.session.commit()

    # 수정한 태그 데이터 저장
    for item in tag_id_list:
        
        Tag_set.add_tag(**item)

    return make_response("success", 200)

# 로그 분석 페이지
@bp.route('/analysis_log/')
@login_required
def analysis_log():
    
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")


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

        # 키워드를 기반으로 class_id를 추출함
        id_list = []
        for item in Medicine.query.filter(Medicine.name.ilike(search)).all():
            id_list.append(item.class_id)
        
        log_list = log_list.filter(Check_log.class_id.in_(id_list))
        
    log_list = log_list.paginate(page=page, per_page=10)
    # log_list = query.paginate(page=page, per_page=10)
    
    medicine_list_using = Medicine.get_using()

    return render_template("model/analysis_log.html",
                           current_menu="analysis_log",
                           medicine_list_using = medicine_list_using,
                           log_list=log_list,
                           page=page,
                           kw=kw) 

# 학습 데이터로 저장 버튼 작동부분
# tag_set db에 태그 정보를 저장한다
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

    Tag_set.del_tag_by_id(data['id'])
    
    db.session.commit()

    for item in tag_id_list:
        
        Tag_set.add_tag(**item)

    return make_response("success", 200)

# 분석 로그 정보를 추출함
@bp.route("/log_detail/<img_id>")
@login_required
def log_detail(img_id):
    
    img_dir = Img_set.query.filter(Img_set.img_id == img_id).first().img_dir

    # 로그 정보는 Check_log 테이블에 존재한다.
    subquery = Check_log.query.filter(Check_log.img_id == img_id).subquery()
    
    # img_id 기준으로 join
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
    

# 기능테스트 링크
# @bp.route('/test/')
# def test():
    
    
#     # 사용 예시
#     head = './server'
#     label_path = '/static/yolo_model/datasets/train/labels/'
#     img_path = '/static/yolo_model/datasets/train/images'

#     img_list = [file for file in os.listdir(head + img_path) if os.path.isfile(os.path.join(head + img_path, file))]

#     for img in img_list:
#         label = img.replace(".jpg", ".txt")

#         image_data = {}
#         f = open(head + label_path + label, "r")

#         image_data['img_id'] = ID_seq.call_ID('IMG')

#         image_data['user_id'] = "admin"
#         image_data['img_dir'] = img_path + "/" + img
#         image_data['train_yn'] = "Y"
#         image_data['rate'] = 0

#         print(image_data)
#         Img_set.add_img(**image_data)
#         line = f.readline()
#         while line:
#             line.replace('\n', '')
#             tag_item = {}
#             tag_item['tag_id'] = ID_seq.call_ID('TAG')
#             tag_item['img_id'] = image_data['img_id']
#             tag_item['class_id'], tag_item['x'], tag_item['y'], tag_item['width'], tag_item['height'] = map(float, line.split(" "))
#             tag_item['class_id'] = str(int(tag_item['class_id']))

#             print(tag_item)
#             Tag_set.add_tag(**tag_item)
#             line = f.readline()
#     return "complete"
    
    