import json
from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Medicine, Tag_set, User, Check_log
from server.views.auth_views import login_required
from sqlalchemy import desc, func, cast, Integer

from datetime import datetime, timedelta, timezone

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
    medicine_list = Medicine.query.order_by(Medicine.name)

    if kw:
        search = "%%{}%%".format(kw)
        medicine_list = medicine_list.filter(Medicine.name.ilike(search))
        
    medicine_list = medicine_list.paginate(page=page, per_page=10)
    return render_template("page/medicine_list.html", current_menu="medicine_list", medicine_list=medicine_list, page=page, kw=kw)


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


@bp.route('/analysis_log/')
@login_required
def analysis_log():
    
    page = request.args.get("page", type=int, default=1)
    kw = request.args.get("kw", type=str, default="")

    # log_list = Check_log.query.order_by(desc(Check_log.date))
    
    # log_list = (
    #     db.session.query(Check_log, Medicine.name).join(Medicine, Check_log.class_id == Medicine.class_id).order_by(desc(Check_log.date))
    # )
    
    # query = db.session.query(
    #     Check_log.check_log_id,
    #     Check_log.user_id,
    #     Check_log.img_id,
    #     Medicine.name.label('medicine_name'),
    #     Check_log.x,
    #     Check_log.y,
    #     Check_log.width,
    #     Check_log.height,
    #     Check_log.rate,
    #     Check_log.date
    # ).join(Check_log, Check_log.class_id == Medicine.class_id)
    
    subquery = Check_log.query.subquery()
    log_list = db.session.query(
        subquery.c.check_log_id,
        subquery.c.user_id,
        subquery.c.img_id,
        subquery.c.class_id,
        subquery.c.x,
        subquery.c.y,
        subquery.c.width,
        subquery.c.height,
        subquery.c.rate,
        subquery.c.date,
        Medicine.name.label('medicine_name')
    ).join(Medicine, Medicine.class_id == subquery.c.class_id)
    
    if kw:
        search = "%%{}%%".format(kw)
        # log_list = log_list.filter(Check_log.check_log_id.ilike(search))
        # query = query.filter(Check_log.check_log_id.ilike(search))
        log_list = log_list.filter(subquery.c.check_log_id.ilike(search)).distinct()
        
    log_list = log_list.paginate(page=page, per_page=10)
    # log_list = query.paginate(page=page, per_page=10)
    
    
    # UTC 시각을 한국 시각으로 변환
    # for log in log_list.items:
    #     log.date = log.date.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=9)))

    return render_template("page/analysis_log.html", current_menu="analysis_log", log_list=log_list, page=page, kw=kw) 