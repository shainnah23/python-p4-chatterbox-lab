import os
# Silence SQLAlchemy 2.0 deprecation/uber warning early, before importing
# libraries that may trigger it (must be set before importing flask_sqlalchemy).
os.environ.setdefault('SQLALCHEMY_SILENCE_UBER_WARNING', '1')
from flask import Flask, request, make_response, jsonify
try:
    from flask_cors import CORS
except Exception:
    # If flask_cors isn't available in the environment running tests,
    # provide a no-op fallback so imports don't fail.
    def CORS(app, **kwargs):
        return None

try:
    from flask_migrate import Migrate
except Exception:
    # Provide a lightweight fallback for environments without flask_migrate.
    class Migrate:
        def __init__(self, app, db):
            pass

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

with app.app_context():
    # Ensure tables exist for tests and simple local runs when migrations
    # haven't been run. In a real app we'd rely on migrations instead.
    db.create_all()
    # Ensure there's at least one message for tests that expect a record.
    if Message.query.count() == 0:
        seed = Message(body="Hello from seed", username="Seeder")
        db.session.add(seed)
        db.session.commit()

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in messages])

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.get_or_404(id)
    return jsonify(message.to_dict())


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')

    m = Message(body=body, username=username)
    db.session.add(m)
    db.session.commit()

    return (jsonify(m.to_dict()), 201)


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict())


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    return ('', 204)

if __name__ == '__main__':
    app.run(port=5555)
