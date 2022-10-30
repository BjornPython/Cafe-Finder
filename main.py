from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Variables
API_KEY = "THISISASECRETAPIKEY"

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


# ------- FUNCTIONS --------#
def add_cafe(name, map_url, img_url, location, seats, has_toilet, has_wifi, has_sockets, can_take_calls, coffee_price):
    cafe = Cafe(
        name=name,
        map_url=map_url,
        img_url=img_url,
        location=location,
        seats=seats,
        has_toilet=has_toilet,
        has_wifi=has_wifi,
        has_sockets=has_sockets,
        can_take_calls=can_take_calls,
        coffee_price=coffee_price

    )
    try:
        db.session.add(cafe)
        db.session.commit()
    except:
        return "UPLOAD FAILED"
    else:
        return {
            "response": {
                "success": "Successfully added the new cafe."
            }
        }


def del_cafe(id):
    try:
        cafe = db.session.query(Cafe).get(id)
    except:
        return "Cafe id not found"
    else:

        try:
            db.session.delete(cafe)
            db.session.commit()
        except:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        else:
            return jsonify(response={"success": "Successfully Deleted the Cafe."}), 200


def get_all_data():
    data = db.session.query(Cafe).all()
    return data


def data_json(datas: list):
    list = []
    for data in datas:
        list.append({
            "id": data.id,
            "name": data.name,
            "map_url": data.map_url,
            "img_url": data.img_url,
            "location": data.location,
            "seats": data.seats,
            "has_toilet": data.has_toilet,
            "has_wifi": data.has_wifi,
            "has_sockets": data.has_sockets,
            "can_take_calls": data.can_take_calls,
            "coffee_price": data.coffee_price
        }
        )
    return list


def search_cafe_loc(location):
    data = get_all_data()
    cafes = data_json(data)
    cafe_list = []
    for cafe in cafes:
        if location.title() == cafe["location"].title():
            cafe_list.append(cafe)

    if len(cafe_list) > 1:
        return "No Cafe Found in the Area."
    return cafe_list


def edit_price(id, price):
    cafe = db.session.query(Cafe).get(id)
    if cafe:
        cafe.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200

    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all")
def all_data():
    data = get_all_data()
    json = data_json(data)
    return json


@app.route("/search")
def search():
    print(request.args.get('location'))
    return search_cafe_loc(request.args.get('location'))


@app.route("/add", methods=['POST'])
def post_new_cafe():
    if request.args.get("apiKey") == API_KEY:
        name = request.form.get("name")
        map_url = request.form.get("map_url")
        img_url = request.form.get("img_url")
        location = request.form.get("location")
        seats = request.form.get("seats")
        has_toilet = bool(request.form.get("has_toilet"))
        has_wifi = bool(request.form.get("has_wifi"))
        has_sockets = bool(request.form.get("has_sockets"))
        can_take_calls = bool(request.form.get("can_take_calls"))
        coffee_price = request.form.get("coffee_price")

        return (add_cafe(name, map_url, img_url, location, seats, has_toilet, has_wifi, has_sockets, can_take_calls,
                         coffee_price))
    return jsonify(error={"Unauthorized": "Not a valid api."}), 401


@app.route("/update-price/<id>", methods=['PATCH'])
def update_price(id):
    print(id)
    price = request.args.get("price")
    return edit_price(id, price)


@app.route("/report-closed/<id>", methods=['DELETE'])
def report_closed(id):
    user_key = request.args.get("apiKey")
    if user_key == API_KEY:
        return del_cafe(id)
    return jsonify(error={"Unauthorized": "Not a valid api."}), 401


if __name__ == '__main__':
    app.run(debug=True)
