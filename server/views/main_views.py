from flask import Blueprint, redirect, url_for
bp = Blueprint("adm", __name__, url_prefix="/")

from server.models import Medicine

@bp.route("/")
def index():
    # med_list = Medicine.query.order_by(Medicine.med_id.desc())
    # return render_template("test/test.html", med_list=med_list)
    return redirect(url_for("auth.login"))


