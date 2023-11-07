from flask import Blueprint, url_for, render_template, flash, request, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
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
