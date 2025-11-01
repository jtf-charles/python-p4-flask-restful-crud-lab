#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
ALLOWED_FIELDS = {"name", "image", "price", "is_in_stock"}
from models import db, Plant
from flask_restful import Resource, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)
    
    def patch(self, id):
        plant = Plant.query.get(id)
        if not plant:
            abort(404, message=f"Plant {id} not found")

        data = request.get_json(silent=False) 
        if not isinstance(data, dict):
            return {"error": "JSON object required"}, 400

        for key, value in data.items():
            if key not in ALLOWED_FIELDS:
                continue 
            if key == "price" and value is not None:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    return {"error": "price must be a number"}, 400

            if key == "is_in_stock":
                if isinstance(value, str):
                    value = value.strip().lower() in {"true", "1", "yes", "y"}
                else:
                    value = bool(value)

            setattr(plant, key, value)

        db.session.commit()  
        return plant.to_dict(), 200

    def delete(self, id):

        record = Plant.query.filter_by(id=id).first()

        db.session.delete(record)
        db.session.commit()

        response_dict = {"message": "record successfully deleted"}

        response = make_response(
            response_dict,
            200
        )

        return response

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
