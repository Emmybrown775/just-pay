import os
from sys import prefix
from uuid import uuid4

import requests
from sqlalchemy.orm.attributes import flag_modified

from app.models import Users
from app.extensions import db
import pandas

TOKEN =  os.getenv("TELEGRAM_TOKEN")
TOKEN_URL = f"https://api.telegram.org/bot{TOKEN}"
PAY_SECRET = os.getenv("PAY_SECRET")

PAYSTACK_HEADER = {
    "Authorization": f"Bearer {PAY_SECRET}"
}

def set_webhook():
    response =  requests.post(
        f"{TOKEN_URL}/setWebhook",
        json={"url": f"https://acb4-102-90-101-44.ngrok-free.app/tel-bp/{TOKEN}"}
    )

    print(response.json())


def start(chat_id):
    user =  Users.query.filter_by(chat_id=chat_id).first()
    if user is None:
        new_user = Users(
            chat_id = chat_id
        )
        db.session.add(new_user)
        db.session.commit()

        send_message(chat_id, "Welcome to Just Pay. Please use the /setup command to setup you payment details.")

    else:
        if user.account_number is None:
            not_setup(chat_id)
        else:
            send_message(chat_id, "Welcome back to just pay")



def not_setup(chat_id):
    send_message(chat_id, "Please use the /setup command to setup your payment details")


def setup(chat_id, message):
    user = Users.query.filter_by(chat_id=chat_id).first()
    if user:

        if user.state is None:
            send_message(chat_id, "Please type in your account number.")
            user.state = "waiting for account number"
            db.session.commit()
            return
        elif user.state == "waiting for account number":
            if not str(message).isdigit() and len(str(message)) != 10:
                return send_message(chat_id, "Please type in valid details.")
            else:
                account_number = int(message)
                user.temp_details["account_number"] = account_number
                flag_modified(user, "temp_details")
                user.state = "waiting for bank letter"
                db.session.commit()
                return send_message(chat_id, "Please type the first three or more  letters of your bank's name,")

        elif user.state == "waiting for bank letter":
            if len(message) < 3:
                return send_message(chat_id, "Please type the first three or more  letters of your bank's name,")
            else:
                response = requests.get(url="https://api.paystack.co/bank", params={
                    "country": "nigeria"
                }, headers=PAYSTACK_HEADER)

                if response.status_code == 200:
                    df = pandas.DataFrame(response.json()["data"])
                    filtered_df = df[df["name"].str.startswith(message, na=False)].to_dict(orient="records")
                    print(filtered_df)
                    if len(filtered_df) != 0:
                        new_message = (f"Please type the code associated with your bank\n"
                                       )
                        for bank in filtered_df:
                            new_string = f"Code: {bank['code']}     Bank: {bank['name']}\n"
                            new_message += new_string

                        user.state = "waiting for bank code"
                        db.session.commit()
                        return send_message(chat_id, new_message)
                    else:
                        send_message(chat_id, "No bank was found, please try again or select another bank.")
                else:
                    print(response.text)

        elif user.state == "waiting for bank code":
            if not str(message).isdigit() and len(str(message)) != 3:
                return send_message(chat_id, "Please type in a valid code.")
            else:
                bank_code = str(message)
                account_number = str(user.temp_details["account_number"])

                response = requests.get(
                    "https://api.paystack.co/bank/resolve", headers=PAYSTACK_HEADER,
                    params={
                        "account_number": account_number,
                        "bank_code": bank_code
                    }
                )

                if response.status_code == 200:
                    new_message = f"Please confirm with y or n your account name is: {response.json()['data']["account_name"]}"
                    user.temp_details["bank_code"] = message
                    user.temp_details["account_name"] = response.json()['data']["account_name"]

                    flag_modified(user, "temp_details")
                    user.state = "waiting for confirmation"
                    db.session.commit()
                    return send_message(chat_id, new_message)

        elif user.state == "waiting for confirmation":
            if str(message).lower() == "y":
                user.account_number = user.temp_details["account_number"]
                user.bank_code = user.temp_details["bank_code"]
                user.account_name = user.temp_details["account_name"]
                user.state = None

                db.session.commit()
                return send_message(chat_id, "Updated successfully")


def account(chat_id):
    user =  Users.query.filter_by(chat_id=chat_id).first()
    if user:
        if user.account_number is None:
            return send_message(chat_id, "Please use the /setup command to setup your payment details")
        else:
            return send_message(chat_id, "Here are you details:\n"
                                         f"Account Name: {user.account_name}\n"
                                         f"Bank Code: {user.bank_code}\n"
                                         f"Account Number: {user.account_number}")


def make_request(chat_id, message, user):
    if user:
        if message == "/request":
            user.state = "awaiting amount"
            db.session.commit()

            return send_message(chat_id, "Please place in your request amount")
        elif str(message).isdigit():
            amount = int(message)
            body = {
                "email": "elumezeemma@gmail.com",
                "amount": str(amount * 100),
                "reference": str(uuid4()),
                "metadata": {
                    "chat_id": chat_id
                }
            }

            response = requests.post("https://api.paystack.co/transaction/initialize", json=body, headers=PAYSTACK_HEADER)
            if response.status_code == 200:
                data = response.json()
                url = data["data"]["authorization_url"]

                message = f"Your Payment url has been created successfully for {amount} \n {url}"

                send_message(chat_id, message)
            else:
                print(response.text)
                send_message(chat_id, "An error occurred please try again")

            user.state = None
            db.session.commit()

def balance(chat_id, message, user):
    user_balance = user.balance

    send_message(chat_id, f"You have {user_balance} left in your balance.")


def send_message(chat_id, message):
    response = requests.post(
        f"{TOKEN_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message
        }
    )
    return response.status_code

