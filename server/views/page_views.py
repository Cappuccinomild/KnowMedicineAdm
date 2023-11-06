from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

bp = Blueprint("page", __name__, url_prefix="/page")


@bp.route("/dashboard/")
def dashboard():
    # 데이터베이스에서 필요한 정보 불러오기
    
    return render_template('page/dashboard.html')