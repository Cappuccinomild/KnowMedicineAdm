from flask import Flask

from flask_jwt_extended import *

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)
    app.config["JSON_AS_ASCII"] = False

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # JWT토큰 추가
    app.config.update(DEBUG=True, JWT_SECRET_KEY="SILLA1234@")

    # JWT 확장 모듈을 flask 어플리케이션에 등록
    jwt = JWTManager(app)

    from .views import main_views, auth_views, page_views, api_views
    
    # 블루프린트
    app.register_blueprint(api_views.bp)
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(page_views.bp)
    
    # 필터
    from .filter import format_datetime, format_datetime2
    app.jinja_env.filters['birthday'] = format_datetime
    app.jinja_env.filters['customDate'] = format_datetime2
    

    # app.run(host='192.168.55.39', port= 8000)
    return app