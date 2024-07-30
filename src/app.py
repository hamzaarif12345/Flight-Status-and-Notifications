import json
import random
import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
import pika
import logging
import eventlet
import eventlet.wsgi

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/flightdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='flight_updates')

logging.basicConfig(level=logging.INFO)

# Models
class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    gate = db.Column(db.String(5), nullable=False)

    def as_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=True)
    notifications = db.Column(db.Boolean, default=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notifications = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref=db.backref('settings', uselist=False))

db.create_all()

# Fetch flight data from OpenSky Network API
def fetch_flight_data():
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url)
    if response.status_code == 200 and 'states' in response.json():
        flights = response.json().get('states', [])
        a = str(random.randint(1, 5))
        return [{
            'id': i,
            'flight_iata': f[1],
            'flight_status': 'in_air' if f[8] else 'landed',
            'gate': str(random.randint(1, 5)) if f[1] == 'N/A' else a
        } for i, f in enumerate(flights)]
    else:
        return []

@app.route('/api/flights', methods=['GET'])
def get_flights():
    flights = fetch_flight_data()
    return jsonify(flights) if flights else jsonify({'message': 'No flight data available'}), 200

@app.route('/api/flights/<int:flight_id>', methods=['PUT'])
def update_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    data = request.json
    flight.status = data.get('status', flight.status)
    flight.gate = data.get('gate', flight.gate)
    db.session.commit()
    send_flight_update(flight)
    return jsonify(flight.as_dict())

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    phone_number = data.get('phone_number')
    user = User(email=email, phone_number=phone_number)
    db.session.add(user)
    db.session.commit()
    user_settings = UserSettings(user_id=user.id)
    db.session.add(user_settings)
    db.session.commit()
    return jsonify({'id': user.id, 'email': user.email, 'phone_number': user.phone_number})

@app.route('/api/users/<int:user_id>/settings', methods=['GET', 'PUT'])
def user_settings(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'GET':
        return jsonify(user.settings.as_dict())
    elif request.method == 'PUT':
        data = request.json
        user.settings.notifications = data.get('notifications', user.settings.notifications)
        db.session.commit()
        return jsonify(user.settings.as_dict())

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    data = request.get_json()
    user_id = data['user_id']
    flight_id = data['flight_id']
    
    subscription = Subscription(user_id=user_id, flight_id=flight_id)
    db.session.add(subscription)
    db.session.commit()
    return jsonify({"message": "Subscribed successfully"}), 201

@app.route('/api/users/<int:user_id>/subscriptions', methods=['GET'])
def get_subscriptions(user_id):
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    result = [{"flight_id": s.flight_id} for s in subscriptions]
    return jsonify(result), 200

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

def send_flight_update(flight):
    flight_data = flight.as_dict()
    logging.info(f"Sending flight update: {flight_data}")
    socketio.emit('flight_update', flight_data, broadcast=True)
    channel.basic_publish(exchange='', routing_key='flight_updates', body=json.dumps(flight_data))

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
