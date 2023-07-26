from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route("/messages", methods=["GET", "POST"])
def messages():
    all = Message.query.all()
    messages = []
    if request.method == "GET":
        for message in all:
            messages.append(message.to_dict())
        messages = sorted(messages, key=lambda x: x["created_at"])
        return messages
    elif request.method == "POST":
        data = request.json
        message = Message()
        for attr in data:
            setattr(message, attr, data[attr])
        try:
            db.session.add(message)
            db.session.commit()
            return message.to_dict(), 201
        except IntegrityError as ie:
            return {"error": ie.args}, 422


@app.route("/messages/<int:id>", methods=["PATCH", "DELETE"])
def messages_by_id(id):
    # data = request.json
    message = Message.query.filter(Message.id == id).first()
    # print(message)
    if request.method == "PATCH":
        data = request.json
        for attr in data:
            setattr(message, attr, data[attr])
        setattr(message, "updated_at", datetime.now())
        try:
            db.session.commit()
            return message.to_dict(), 200
        except IntegrityError as ie:
            return {"error": ie.args}, 422
    elif request.method == "DELETE":
        if not message:
            return {"message": "Message not found"}, 404
        db.session.delete(message)
        db.session.commit()
        return {}, 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)
