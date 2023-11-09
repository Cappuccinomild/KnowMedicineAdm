from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserCreateForm, UserDetailForm
from server.models import Medicine, User
from server.views.auth_views import login_required

bp = Blueprint("page", __name__, url_prefix="/page")


@bp.route("/dashboard/")
@login_required
def dashboard():
    # TODO: 데이터베이스에서 필요한 정보 불러오기

    return render_template("page/dashboard.html", current_menu="dashboard")


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
    
    print(form.name.data)
    
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
        print(user.birthday)
        form = UserDetailForm(obj=user)
        
    return render_template('page/user_modify.html', current_menu="user_list", form=form)


@bp.route('/user_delete/<string:user_id>')
@login_required
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('page.user_list'))