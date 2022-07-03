from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
import configurations as config
import uuid
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.dialects.postgresql import UUID

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.postgresConn
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)


class Aircraft(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    serial_number = db.Column(UUID(as_uuid=True), default=uuid.uuid4)
    manufacturer = db.Column(db.String(255))
    # comments = db.relationship('Flight', backref='aircraft')
    __table_args__ = (
        db.UniqueConstraint(serial_number, manufacturer),
    )

    def __repr__(self):
        return f'<Aircraft "{self.serial_number} : {self.manufacturer}">'


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    arrival_airport_icao = db.Column(db.Text)
    departure = db.Column(db.DateTime)
    arrival = db.Column(db.DateTime)
    aircraft = db.Column(UUID, db.ForeignKey('aircraft.id'))

    def __repr__(self):
        return f'<Comment "{self.content[:20]}...">'


class FlightSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'arrival_airport_icao',
            'departure',
            'arrival',
            'aircraft',
        )


class AircraftSchema(ma.Schema):
    class Meta:
        fields = (
            'id',
            'serial_number',
            'manufacturer',
        )


flight_schema = FlightSchema()
flights_schema = FlightSchema(many=True)
aircraft_schema = AircraftSchema()
aircrafts_schema = AircraftSchema(many=True)


class AirCraftListResource(Resource):
    def get(self):
        aircrafts = Aircraft.query.all()
        return aircrafts_schema.dump(aircrafts)

    def post(self):
        new_aircraft = Aircraft(
            serial_number=request.json["serial_number"],
            manufacturer=request.json["manufacturer"],
        )
        db.session.add(new_aircraft)
        db.session.commit()
        return aircraft_schema.dump(new_aircraft)


api.add_resource(AirCraftListResource, "/aircraft/")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
