from app import create_app
from app.blueprints.webhook import set_webhook

app = create_app()

if __name__ ==  "__main__":
    app.run()
