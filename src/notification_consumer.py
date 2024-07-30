import pika
import requests

def send_notification(user, flight):
    message = f"Flight {flight['flight_number']} status changed to {flight['status']}."
    # Send email/SMS using your preferred method here
    print(f"Sending notification to {user['email']}: {message}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='flight_status')

def callback(ch, method, properties, body):
    flight = json.loads(body)
    subscriptions = Subscription.query.filter_by(flight_id=flight['id']).all()
    for subscription in subscriptions:
        user = User.query.get(subscription.user_id)
        send_notification(user, flight)

channel.basic_consume(queue='flight_status', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
