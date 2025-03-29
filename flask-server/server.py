from flask import Flask, jsonify, request, redirect
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Food(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    meal = db.Column(db.String(20), nullable=False)
    food = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Food {self.date} {self.meal} {self.food}>"


@app.route("/")
def index():
    return "Welcome to the Stay Fit API!"


@app.route("/food", methods=["POST", "GET"])
@cross_origin()
def food():
    if request.method == "POST":
        food_content = request.get_json()
        meal = food_content["title"]
        data = food_content["data"]
        print(food_content)
        new_food = Food(
            id=data["id"],
            date=datetime.strptime(data["date"], "%Y-%m-%d"),
            meal=meal,
            food=data["food"],
        )
        try:
            db.session.add(new_food)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")
            return f"An error occurred: {e}"
    else:
        foods = Food.query.order_by(Food.meal).all()
        print(foods)
        if foods == []:
            return []
        else:
            return [
                {
                    "id": food.id,
                    "meal": food.meal,
                    "date": datetime.strftime(food.date, "%Y-%m-%d"),
                    "food": food.food,
                }
                for food in foods
            ]

@app.route("/food/<string:id>", methods=['DELETE'])
@cross_origin()
def delete(id):
    food_to_delete = Food.query.get_or_404(id)
    print(food_to_delete)
    try:
        db.session.delete(food_to_delete)
        db.session.commit()
        print(f"Deleted item successfully: {id}")
        return jsonify({"message": f"Food with ID {id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
