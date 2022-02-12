from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

# since our server is now acting as an API, we want to return a JSON containing the necessary data, we want to return a JSON containing the necessary data
# convert the random_cafe object into a JSON - serialization
# jsonify() - built in serialisation method
# how do we do it??? - first we convert it to a dictionary and then use jsonify() to convert the dictionary to a JSON
def to_dict(self):
    cafe_dictionary = {}
    for column in self.__table__.columns:
        # getattr() method returns the value of the named attribute of an object
        cafe_dictionary[column.name] = getattr(self, column.name)
    return cafe_dictionary

# create a /random route in main.py that allows GET requests to be made into it
# @app.route("/random", methods=["Get"])
# def home():
    # return render_template("index.html")
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choices(cafes)
    # .to_dict() - convert the DataFrame to a dictionary
    return jsonify(cafe=random_cafe.to_dict())

# HTTP GET - read record
# create another GET route that's called /all
# when a GET request is made to this /all route, your server should return all the cafes in your database as a JSON
@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_cafe_location:
    cafe_location = requests.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=cafe_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"There is not cafe at that location."}), 404

# HTTP POST - create record
@app.route("/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "You have successfully added a new cafe."})

# HTTP PUT/PATCH - update record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def change_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "You have successfully updated the price of coffee."}), 200
    else:
        return jsonify(error={"error" : "A cafe with that id does not exist."}), 404

# HTTP DELETE - delete record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "You have successfully delted the cafe."}), 200
        else:
            return jsonify(error={"error" : "A cafe with that id does not exist."}), 404
    else:
        return jsonify(error={"forbidden" : "You do not have the correct API Key"}), 403

if __name__ == '__main__':
    app.run(debug=True)
