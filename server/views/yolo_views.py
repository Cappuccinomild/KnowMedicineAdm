from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Img_set, Tag_set, Medicine
from server.views.auth_views import login_required

bp = Blueprint("model", __name__, url_prefix="/model")

@bp.route("/data_list/")
@login_required
def data_list():
    
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

    return render_template("model/data_list.html", 
                           current_menu="data_list",
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


@bp.route('/test/')
def test():
    
    import os
    from server.models import Tag_set, Img_set, ID_seq
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
    