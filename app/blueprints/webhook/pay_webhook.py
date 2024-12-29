import hashlib
import hmac
from flask import Blueprint, request

from app.extensions import db
from app.blueprints.webhook import PAY_SECRET, send_message
from app.models import Users

pay_bp = Blueprint("pay_bp", __name__)

@pay_bp.route("/webhook", methods=["POST"])
def webhook():
    webhook_data = request.get_json()
    signature = request.headers.get("x-paystack-signature")
    computed_signature = hmac.new(PAY_SECRET.encode("utf-8"), request.get_data(as_text=True).encode(),
                                  hashlib.sha512).hexdigest()
    if signature != computed_signature:
        print("invalid signature")
        return {"error": "Invalid signature"}, 401
    if webhook_data["event"] == "charge.success":
        chat_id = webhook_data["data"]["metadata"]["chat_id"]
        amount = webhook_data["data"]["amount"]

        user = Users.query.filter_by(chat_id=chat_id).first()
        user.balance += amount/100
        db.session.commit()

        message = f"You have successfully received {amount / 100} to your account."
        send_message(chat_id, message)
        return "OK", 200
    return "OK", 200