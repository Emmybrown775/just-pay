from flask import Flask

from app.blueprints.webhook import set_webhook
from app.blueprints.webhook.pay_webhook import pay_bp
from app.blueprints.webhook.tel_webhook import tel_bp
from app.extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.DevConfig")

    db.init_app(app)

    app.register_blueprint(tel_bp, url_prefix="/tel-bp")
    app.register_blueprint(pay_bp, url_prefix="/pay-bp")
    set_webhook()

    with app.app_context():
        db.create_all()


    return app