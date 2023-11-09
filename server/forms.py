from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
from wtforms.validators import DataRequired, Length, EqualTo


class UserLoginForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired('아이디를 입력하세요.'), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 입력하세요.')])
    

class UserCreateForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired('아이디를 입력하세요.'), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired('비밀번호를 입력하세요.'), EqualTo('password2', '비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired('비밀번호를 한 번 더 입력하세요.')])
    name = StringField('이름', validators=[DataRequired('이름을 입력하세요'), Length(min=1, max=41)])
    birthday = DateField('생년월일', validators=[DataRequired('생년월일을 입력하세요.')])
    gender = StringField('성별', validators=[DataRequired('성별을 입력하세요.'), Length(min=1, max=4)])
    phone = StringField('전화번호', validators=[DataRequired('전화번호를 입력하세요.'), Length(min=1, max=35)])
    

class UserDetailForm(FlaskForm):
    user_id = StringField('아이디', validators=[DataRequired('아이디를 입력하세요.'), Length(min=3, max=25)])
    name = StringField('이름', validators=[DataRequired('이름을 입력하세요'), Length(min=1, max=41)])
    birthday = DateField('생년월일', validators=[DataRequired('생년월일을 입력하세요.')])
    gender = StringField('성별', validators=[DataRequired('성별을 입력하세요.'), Length(min=1, max=4)])
    phone = StringField('전화번호', validators=[DataRequired('전화번호를 입력하세요.'), Length(min=1, max=35)])