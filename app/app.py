#!/usr/bin/env python3
import hashlib
from flask import Flask, json, request, Response, abort

app = Flask(__name__)

messages = {}


def create_json_error_response(msg, status):
    resp_json = json.dumps({"err_msg": msg})
    resp = Response(resp_json, status=status, mimetype='application/json')
    return resp


@app.route('/messages', methods=['POST'])
def add_message():
    if request.headers['Content-Type'] == 'application/json':
        data = request.json
    else:
        error_msg, status = "Unsupported Content Type", 415
        return create_json_error_response(error_msg, status)

    try:
        msg = data["message"]
    except KeyError:
        error_msg, status = "Missing message key from json", 404
        return create_json_error_response(error_msg, status)

    msg_digest = hashlib.sha256(msg.encode()).hexdigest()
    resp_json = json.dumps({"digest": msg_digest})
    new_msg = {msg_digest: msg}
    messages.update(new_msg)
    resp = Response(resp_json, status=201, mimetype='application/json')

    return resp


@app.route('/messages/<message_hash>', methods=['GET'])
def lookup_message(message_hash):
    if message_hash in messages:
        resp_json = json.dumps({"message": messages[message_hash]})
        resp = Response(resp_json, status=200, mimetype='application/json')
        return resp
    else:
        error_msg, status = "Message not found", 404
        return create_json_error_response(error_msg, status)


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(ssl_context=('cert.pem', 'key.pem'), host="0.0.0.0")
