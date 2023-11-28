from io import BytesIO, StringIO
import json
from urllib.parse import quote
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify, Response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Medicine, Tag_set, User, Check_log
from server.views.auth_views import login_required
from sqlalchemy import desc, func, cast, Integer

from datetime import datetime, timedelta, timezone
import pandas as pd

bp = Blueprint("page", __name__, url_prefix="/page")


@bp.route("/dashboard/")
@login_required
def dashboard():
    taggedCnt = Medicine.query.filter(Medicine.class_id != None).count()
    nonTaggedCnt = Medicine.query.filter(Medicine.class_id == None).count()
    dailyUsage = get_daily_usage()
    monthlyUsage = get_monthly_usage()
    medImgs = get_med_imgs()

    return render_template("page/dashboard.html", current_menu="dashboard", 
                           taggedCnt=taggedCnt, nonTaggedCnt=nonTaggedCnt,
                           dailyUsage=dailyUsage, monthlyUsage=monthlyUsage,
                           medImgs=medImgs)


def get_daily_usage():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=4)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
    daily_usage = db.session.query(func.date(Check_log.date).label('date'), func.count().label('count')) \
        .filter(Check_log.date >= start_date, Check_log.date <= end_date ) \
        .group_by(func.date(Check_log.date)) \
        .all()
    
    results = [(row.date.strftime('%Y-%m-%d'), row.count) for row in daily_usage]
    results = json.dumps(results)
    
    return results


def get_monthly_usage():
    end_month = datetime.utcnow().month
    start_month = end_month - 4 if end_month > 4 else 1
    
    monthly_usage = db.session.query(func.extract('month', Check_log.date).label('month'), func.count().label('count')) \
        .filter(func.extract('month', Check_log.date) >= start_month, func.extract('month', Check_log.date) <= end_month) \
        .group_by(func.extract('month', Check_log.date)) \
        .all()
        
    results = [tuple(row) for row in monthly_usage]
    results = json.dumps(results)
    
    return results


def get_med_imgs():
    # med_imgs = db.session.query(Tag_set.class_id, func.count().label('count')) \
    #     .group_by(Tag_set.class_id) \
    #     .order_by(cast(Tag_set.class_id, Integer).asc()) \
    #     .all()
    
    # med_imgs = db.session.query(Medicine.name, func.count().label('count')) \
    #     .join(Tag_set, Medicine.class_id == Tag_set.class_id) \
    #     .group_by(Medicine.name) \
    #     .order_by(cast(Tag_set.class_id, Integer).asc()) \
    #     .limit(10) \
    #     .all()
    
    subquery = db.session.query(Medicine.name, func.count().label('count')) \
        .join(Tag_set, Medicine.class_id == Tag_set.class_id) \
        .group_by(Medicine.name) \
        .order_by(desc('count')) \
        .limit(10) \
        .subquery()

    med_imgs = db.session.query(subquery.c.name, subquery.c.count) \
        .order_by(desc(subquery.c.count)) \
        .all()
    
    results = [tuple(row) for row in med_imgs]
    results = json.dumps(results)
    
    return results


@bp.route("/medicine_list/")
@login_required
def medicine_list():
    
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")
    
    t_medicine_list = Medicine.query.filter(Medicine.class_id != None).order_by(Medicine.name)  # class_id가 있는 약품
    nt_medicine_list = Medicine.query.filter(Medicine.class_id == None).order_by(Medicine.name) # class_id가 없는 약품 

    if kw:
        search = "%%{}%%".format(kw)
        nt_medicine_list = nt_medicine_list.filter(Medicine.name.ilike(search))
        
    nt_medicine_list = nt_medicine_list.paginate(page=page, per_page=10)
    
    return render_template("page/medicine_list.html", current_menu="medicine_list", 
                           t_medicine_list=t_medicine_list, nt_medicine_list=nt_medicine_list,
                           page=page, kw=kw)


@bp.route("/medicine_detail/<string:medId>")
def medicine_detail(medId):
    medicine = Medicine.query.get(medId)
    
    if medicine is not None:
        return jsonify({
            'name': medicine.name,
            'effect': medicine.effect,
            'usage': medicine.usage,
            'caution': medicine.caution
        })
    
    return jsonify({'error': '약품 정보를 찾을 수 없습니다.'}), 404


@bp.route("/medicine_download_csv/<string:tbType>")
def medicine_download_csv(tbType):
    # output_stream = StringIO() 
    output_stream = BytesIO() # dataframe을 저장할 IO stream
    
    if tbType == 'tagged':
        medicine_list = Medicine.query.filter(Medicine.class_id != None).order_by(Medicine.name).all()
    
    elif tbType == 'nonTagged':
        medicine_list = Medicine.query.filter(Medicine.class_id == None).order_by(Medicine.name).all()

    # DataFrame 생성
    df = pd.DataFrame({
        '의약품 이름': [medicine.name for medicine in medicine_list],
        '유형': ['키트' if medicine.effect_type == 'K' else '약품' for medicine in medicine_list],
        '효능': [medicine.effect for medicine in medicine_list],
        '용법': [medicine.usage for medicine in medicine_list],
        '주의사항': [medicine.caution for medicine in medicine_list],
    })
    
    df.to_excel(output_stream, index=False)
    output_stream.seek(0)
    
    return send_file(
        output_stream,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"의약품정보_{tbType}.xlsx"
    )
    
    # df.to_csv(output_stream, encoding='utf-8-sig', index=False) # 그 결과를 앞서 만든 IO stream에 저장

    # response = Response(
    #     output_stream.getvalue(),
    #     mimetype='text/x-csv',
    #     content_type='application/octet-stream'
    # )
    
    # filename = quote("의약품정보.csv")
    # response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{filename}"
    
    # return response
    
    # return redirect(url_for("page.medicine_list"))
    

@bp.route("/medicine_add_tag/<string:medId>")
@login_required
def medicine_add_tag(medId):    
    curMedicine = Medicine.query.filter(Medicine.med_id == medId).first()
    
    if curMedicine:
        if not curMedicine.class_id:
            tagCount = Medicine.query.filter(Medicine.class_id != None).count()
            newClassId = str(tagCount + 1)
            curMedicine.class_id = newClassId
            db.session.commit()
        else:
            print(">>> 이미 class_id 가 부여되어 있습니다.")
    else:
        print(">>> 해당 레코드를 찾을 수 없습니다.")

    return redirect(url_for("page.medicine_list"))


@bp.route("/user_list/")
@login_required
def user_list():
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")
    user_list = User.query.order_by(User.user_id)

    if kw:
        search = "%%{}%%".format(kw)
        user_list = user_list.filter(User.user_id.ilike(search))
        
    user_list = user_list.paginate(page=page, per_page=10)
    return render_template("page/user_list.html", current_menu="user_list", user_list=user_list, page=page, kw=kw)


@bp.route("/user_create/", methods=('GET', 'POST'))
@login_required
def user_create():
    form = UserCreateForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(user_id=form.user_id.data).first()
        if not user:
            user = User(user_id=form.user_id.data,
                        password=generate_password_hash(form.password1.data),
                        name=form.name.data,
                        birthday=form.birthday.data,
                        gender=form.gender.data,
                        phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('page.user_list'))
        else:
            flash('이미 존재하는 사용자입니다.')
    
    return render_template('page/user_create.html', current_menu="user_list", form=form)


@bp.route('/user_modify/<string:user_id>', methods=('GET', 'POST'))
@login_required
def user_modify(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        form = UserDetailForm()
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            return redirect(url_for('page.user_list'))
    else:
        form = UserDetailForm(obj=user)
        
    return render_template('page/user_modify.html', current_menu="user_list", form=form)


@bp.route('/user_detail/<string:userId>')
def user_detail(userId):
    user = User.query.get(userId)
    # check_log = Check_log.query.filter_by(user_id=userId).order_by(desc(Check_log.date)).first()
    # check_logs = Check_log.query.filter_by(user_id=userId).order_by(desc(Check_log.date)).all()
    
    subquery = Check_log.query.filter_by(user_id=userId).subquery()
    # subquery = Check_log.query.filter_by(user_id=userId).order_by(desc(Check_log.date)).limit(10).subquery()
    
    check_logs = db.session.query(
        subquery.c.rate,
        subquery.c.date,
        Medicine.name.label('medicine_name')
    ).join(Medicine, Medicine.class_id == subquery.c.class_id).order_by(desc(subquery.c.date))
    
    # if user is not None and check_log is not None:
    #     return jsonify({
    #         'name': user.name,
    #         'birthday': user.birthday,
    #         'gender': user.gender,
    #         'phone': user.phone,
    #         'rate': check_log.rate,
    #         'date': check_log.date
    #     })
    # elif user is not None:
    #     return jsonify({
    #         'name': user.name,
    #         'birthday': user.birthday,
    #         'gender': user.gender,
    #         'phone': user.phone,
    #         'rate': '',
    #         'date': '',
    #     })
    
    if user is not None:
        if check_logs:
            logs_data = [
                {
                    'rate': log.rate,
                    'date': log.date,
                    # 'class_id': log.class_id
                    'medicine_name': log.medicine_name
                }
                for log in check_logs
            ]
            
            # 약품 종류와 약품별 데이터 개수 계산
            medicine_data = {}
            for log in check_logs:
                medicine_name = log.medicine_name
                if medicine_name not in medicine_data:
                    medicine_data[medicine_name] = 1
                else:
                    medicine_data[medicine_name] += 1
            
            # 약품 종류와 약품별 데이터 개수를 리스트로 변환
            labels = list(medicine_data.keys())
            counts = list(medicine_data.values())
            
            user_data = {
                'name': user.name,
                'birthday': user.birthday,
                'gender': user.gender,
                'phone': user.phone,
                'logs': logs_data,
                'labels': labels,
                'counts': counts
            }
        else:
            user_data = {
                'name': user.name,
                'birthday': user.birthday,
                'gender': user.gender,
                'phone': user.phone,
                'logs': []
            }
        
        return jsonify(user_data)
        
    return jsonify({'error': '유저 정보를 찾을 수 없습니다.'}), 404


@bp.route('/user_delete/<string:user_id>')
@login_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('page.user_list'))