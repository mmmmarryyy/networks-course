from flask import Flask, request, jsonify, send_file
import uuid
import os
import time
from threading import Timer, Event
import smtplib
from email.mime.text import MIMEText
import sys

app = Flask(__name__)
products = []
users = {}
user_ips = {}
timers = {}

sender_password = None

class Product:
    def __init__(self, name, description, icon="", user_id=None):
        self.id = uuid.uuid4().int
        self.name = name
        self.description = description
        self.icon = icon
        self.user_id = user_id

    def get_json(self):
        return jsonify({'id': self.id, 'name': self.name, 'description': self.description, 'icon': self.icon})

class User:
    def __init__(self, email, password, ip_address):
        self.id = uuid.uuid4().int
        self.email = email
        self.password = password
        self.token = str(uuid.uuid4())
        self.ip_address = ip_address

@app.route('/user/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    ip_address = request.remote_addr

    if email is None or password is None:
        return jsonify({'error': "Don't get email or password"}), 400

    if email in users:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(email, password, ip_address)
    users[email] = new_user
    user_ips[ip_address] = email
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/user/sign-in', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users.get(email)

    if user is None or user.password != password:
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'token': user.token}), 200

def get_user_from_token(token):
    for user in users.values():
        if user.token == token:
            return user
    return None

def get_user_from_ip(ip_address):
    return user_ips.get(ip_address)

def send_welcome_email(email):
    sender_email = "barkovskaya.maria@mail.ru"
    receiver_email = email

    message = MIMEText("Рады видеть вас в нашем сервисе вновь!")
    message['Subject'] = "Приветственное сообщение"
    message['From'] = sender_email
    message['To'] = receiver_email

    with smtplib.SMTP('smtp.mail.ru', 587) as server:
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

    print(f"Sending welcome email to {email}")
    timers[email].cancel()

def schedule_welcome_email(email):
    timer = Timer(30, send_welcome_email, args=[email])
    timers[email] = timer
    timer.start()

def reset_timer(email):
    if email in timers:
        timers[email].cancel()
    schedule_welcome_email(email)

@app.route('/')
def debug():
  return 'Debug'

@app.route('/product', methods=['POST'])
def add_product():
    try:
        token = request.args.get('token')
        user = get_user_from_token(token)

        data = request.get_json()
        new_product = Product(data['name'], data['description'], user_id=user.id if user else None)
        products.append(new_product)
        return new_product.get_json()
    except:
        return jsonify({'error': "Bad request"}), 400

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    token = request.args.get('token')
    user = get_user_from_token(token)

    ip_address = request.remote_addr
    user_from_ip = get_user_from_ip(ip_address)
    if not user and user_from_ip:
        reset_timer(user_from_ip)

    for product in products:
        if product.id == product_id:
            if (user and product.user_id == user.id) or product.user_id is None:
                return product.get_json()
    return jsonify({'error': 'Product not found'}), 404

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    token = request.args.get('token')
    user = get_user_from_token(token)
    for product in products:
        if product.id == product_id:
            if (user and product.user_id == user.id) or product.user_id is None:
                data = request.get_json()
                if 'name' in data:
                    product.name = data['name']
                if 'description' in data:
                    product.description = data['description']
                return product.get_json()
    return jsonify({'error': 'Product not found'}), 404

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    token = request.args.get('token')
    user = get_user_from_token(token)
    for index, product in enumerate(products):
        if product.id == product_id:
            if (user and product.user_id == user.id) or product.user_id is None:
                deleted_product = products.pop(index)
                return deleted_product.get_json()
    return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['GET'])
def get_all_products():
    token = request.args.get('token')
    user = get_user_from_token(token)

    ip_address = request.remote_addr
    user_from_ip = get_user_from_ip(ip_address)
    if not user and user_from_ip:
        reset_timer(user_from_ip)

    if user:
        return jsonify([{'id': product.id, 'name': product.name, 'description': product.description} for product in products if product.user_id == user.id or product.user_id is None])
    else:
        return jsonify([{'id': product.id, 'name': product.name, 'description': product.description} for product in products if product.user_id is None])

@app.route('/product/<int:product_id>/image', methods=['POST'])
def post_icon(product_id):
    try:
        token = request.args.get('token')
        user = get_user_from_token(token)
        icon = request.files['icon']
        filename = f"product_{product_id}_icon.png"
        for product in products:
            if product.id == product_id:
                if (user and product.user_id == user.id) or product.user_id is None:
                    icon.save(os.path.join(os.getcwd(), 'icons', filename))
                    product.icon = filename
                    return product.get_json()
        return jsonify({'error': 'Product not found'}), 404
    except:
        return jsonify({'error': "Bad request"}), 400

@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_image(product_id):
    try:
        token = request.args.get('token')
        user = get_user_from_token(token)
        for product in products:
            if product.id == product_id:
                if (user and product.user_id == user.id) or product.user_id is None:
                    if product.icon == "":
                        return jsonify({'error': 'Icon not found'}), 404
                    filename = product.icon
                    return send_file(os.path.join(os.getcwd(), 'icons', filename))
        return jsonify({'error': 'Product not found'}), 404
    except:
        return jsonify({'error': "Bad request"}), 400

if __name__ == '__main__':
    if (len(sys.argv[1:]) != 1):
        print(f"you provide {len(sys.argv[1:])} arguments, 1 expected (sender_password)")
        sys.exit(1)

    sender_password = sys.argv[1] # Пароль от mail аккаунта

    icons = os.path.join(os.getcwd(), 'icons')
    if not os.path.exists(icons):
        os.mkdir(icons)
    app.run(debug=True)