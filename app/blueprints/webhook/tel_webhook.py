import requests

from app.blueprints.webhook import TOKEN, TOKEN_URL, start, setup, account, make_request, balance
from flask import Blueprint, request

from app.models import Users

tel_bp = Blueprint("tel-webhook", __name__)

@tel_bp.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        user = Users.query.filter_by(chat_id=chat_id).first()

        if text == "/start":
            start(chat_id)
            return "ok", 200
        if user:
            if text == "/account":
                account(chat_id)
                return "ok", 200
            elif text == "/request" or user.state=="awaiting amount":
                if user is None:
                    return "ok", 200

                elif user:
                    make_request(chat_id, message=text, user=user)
                return "ok"
            elif text == "/balance":
                balance(chat_id, message=text, user=user)
                return "ok", 200
            else:
                setup(chat_id, text)

            return "ok", 200

    return "ok", 200


def is_user_set_up(user):
    if user.account_number is None:
        return False
    else:
        return True



