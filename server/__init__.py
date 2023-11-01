from flask import Flask

from flask_jwt_extended import *

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)

    app.config.from_object(config)
    app.config['JSON_AS_ASCII'] = False

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # JWT토큰 추가
    app.config.update(
        DEBUG = True,
        JWT_SECRET_KEY = "SILLA1234@"
    )
    
    # JWT 확장 모듈을 flask 어플리케이션에 등록
    jwt = JWTManager(app)

    from .views import main_views
    app.register_blueprint(main_views.bp)

    # app.run(host='192.168.55.39', port= 8000)
    return app
        
        
        