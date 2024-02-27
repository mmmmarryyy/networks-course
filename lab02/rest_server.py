from flask import Flask, request, jsonify, abort, send_file
import uuid
import os

app = Flask(__name__)
products = []

class Product:
    def __init__(self, name, description, icon=""):
        self.id = uuid.uuid4().int
        self.name = name
        self.description = description
        self.icon = icon
    def get_json(self):
        return jsonify({'id': self.id, 'name': self.name, 'description': self.description, 'icon': self.icon})

@app.route('/')
def debug():
  return 'Debug'

@app.route('/product', methods=['POST'])
def add_product():
    try:
        if request.is_json:
            data = request.get_json()
        else: 
            data = request.form
        new_product = Product(data['name'], data['description'])
        products.append(new_product)
        return new_product.get_json()
    except:
        abort(400)

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    for product in products:
        if product.id == product_id:
            return product.get_json()
    abort(404)

@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    for product in products:
        if product.id == product_id:
            if request.is_json:
                data = request.get_json()
            else: 
                data = request.form
            if 'name' in data:
                product.name = data['name']
            if 'description' in data:
                product.description = data['description']
            return product.get_json()
    abort(404)

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    for index, product in enumerate(products):
        if product.id == product_id:
            deleted_product = products.pop(index)
            return deleted_product.get_json()
    abort(404)

@app.route('/products', methods=['GET'])
def get_all_products():
    return jsonify([{'id': product.id, 'name': product.name, 'description': product.description} for product in products])

@app.route('/product/<int:product_id>/image', methods=['POST'])
def post_icon(product_id):
    try:
        icon = request.files['icon']
        filename = f"product_{product_id}_icon.png"
        for product in products:
            if product.id == product_id:
                icon.save(os.path.join(os.getcwd(), 'icons', filename))
                product.icon = filename
                return product.get_json()
        abort(404)
    except:
        abort(404)

@app.route('/product/<int:product_id>/image', methods=['GET'])
def get_image(product_id):
    try:
        for product in products:
            if product.id == product_id:
                if product.icon == "":
                    abort(404)
                filename = product.icon
                return send_file(os.path.join(os.getcwd(), 'icons', filename))
        abort(404)
    except:
        abort(404)

if __name__ == '__main__':
    icons = os.path.join(os.getcwd(), 'icons')
    if not os.path.exists(icons):
        os.mkdir(icons)
    app.run(debug=True)