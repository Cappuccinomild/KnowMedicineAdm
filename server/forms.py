from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class UserLoginForm(FlaskForm):
    user_id = StringField("아이디", validators=[DataRequired('아이디를 입력하세요.'), Length(min=3, max=25)])
    password = PasswordField("비밀번호", validators=[DataRequired('비밀번호를 입력하세요.')])
