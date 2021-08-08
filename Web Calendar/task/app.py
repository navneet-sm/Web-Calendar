from datetime import datetime
from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse, inputs, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
parser = reqparse.RequestParser()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'


class Calendar(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()
parser.add_argument('date',
                    type=inputs.date,
                    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
                    required=True)
parser.add_argument('event',
                    type=str,
                    help="The event name is required!",
                    required=True)
parser.add_argument('start_time',
                    type=inputs.date,
                    required=False)
parser.add_argument('end_time',
                    type=inputs.date,
                    required=False)
resource_fields = {'id': fields.Integer,
                   'event': fields.String,
                   'date': fields.String}


def query(data):
    events_list = []
    for i in range(len(data)):
        x = {"id": data[i].id, "event": data[i].event, "date": str(data[i].date)}
        events_list.append(x)
    return events_list


class EventsToday(Resource):
    def get(self):
        return query(Calendar.query.filter(Calendar.date == datetime.today().date()).all())


class Events(Resource):
    def get(self):
        start = request.args.get('start_time')
        end = request.args.get('end_time')
        if start and end:
            events_between = Calendar.query.filter(Calendar.date.between(start, end)).all()
            return query(events_between)
        else:
            return query(Calendar.query.all())

    def post(self):
        args = parser.parse_args()
        data = Calendar(event=args['event'], date=args['date'].date())
        db.session.add(data)
        db.session.commit()
        response = {"message": "The event has been added!",
                    "event": args['event'],
                    "date": str(args['date'].date())}
        return response


class EventById(Resource):

    @marshal_with(resource_fields)
    def get(self, id):
        event = Calendar.query.filter(Calendar.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, id):
        event = Calendar.query.filter(Calendar.id == id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message": "The event has been deleted!"}


api.add_resource(Events, '/event')
api.add_resource(EventsToday, '/event/today')
api.add_resource(EventById, '/event/<int:id>')
# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
