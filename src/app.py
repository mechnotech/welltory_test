from flasgger import Swagger
from flask import Flask
from flask_jwt_extended import JWTManager

from dbs.db import init_db
from settings import config
from views.auth.auth import auth
from views.medical.medical import medical

app = Flask(__name__)
app.config.from_pyfile('settings.py', silent=True)
init_db(app)
app.app_context().push()

swagger = Swagger(app, template_file='project_description/openapi.yaml')
jwt = JWTManager(app)
app.register_blueprint(auth, url_prefix='/api/v1/auth')
app.register_blueprint(medical, url_prefix='/api/v1/stats')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0', port=config.auth_port,
    )
