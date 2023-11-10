import functools
from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from server import db
from server.forms import UserLoginForm
from server.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login/", methods=("GET", "POST"))
def login():
    form = UserLoginForm()

    if request.method == "POST" and form.validate_on_submit():
        error = None
        user = User.query.filter_by(user_id=form.user_id.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다."

        if error is None:
            session.clear()
            session["user_id"] = user.user_id
            _next = request.args.get("next", "")
            if _next:
                return redirect(_next)
            else:
                return redirect(url_for("page.dashboard"))

        flash(error)

    return render_template("auth/login.html", form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@bp.route("/signup/")
def signup():
    form = UserLoginForm()
    
    if request.method == "GET":
        print("GET 요청왓음ㅇㅇ")
        user = User.query.filter_by(user_id="admin").first()
        if not user:
            user = User(
                user_id="admin",
                # auth_id="admin",
                password=generate_password_hash("admin"),
            )
            db.session.add(user)
            db.session.commit()
        else:
            flash('이미 생성되었음')
    
    return redirect(url_for('auth.login'))


@bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for('adm.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        
        return view(*args, **kwargs)
   
    return wrapped_view