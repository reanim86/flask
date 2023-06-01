from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, AdsTable, User
from typing import Type
from schema import CreateAds, PatchAds
from pydantic import ValidationError

app = Flask('app')

class HttpError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'status': 'error', 'message': error.message})
    response.status_code = error.status_code
    return response

def get_ads(ads_id: int, session: Session):
    ads = session.get(AdsTable, ads_id)
    if ads is None:
        raise HttpError(404, message='ads is not found')
    return ads

def get_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, message='user is not found')
    return user

def validate(json_data, model_class: Type[CreateAds] | Type[PatchAds]):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, err.errors())

class AdsView(MethodView):

    def get(self, ads_id):
        with Session() as session:
            ads = get_ads(ads_id, session)
            return jsonify({
                'id': ads.id,
                'head': ads.head,
                'description': ads.description,
                'creationdate': ads.creationdate,
                'user': ads.username
            })

    def post(self):
        json_data = validate(request.json, CreateAds)
        with Session() as session:
            user = get_user(request.json['username'], session)
            return jsonify({'status': 'ok'})
        with Session() as session:
            new_ads = AdsTable(**json_data)
            session.add(new_ads)
            session.commit()
            return jsonify({
                'id': new_ads.id,
                'head': new_ads.head,
                'description': new_ads.description,
                'creationdate': new_ads.creationdate,
                'user': new_ads.username
            })

    def patch(self, ads_id):
        json_data = validate(request.json, PatchAds)
        with Session() as session:
            ads = get_ads(ads_id, session)
            for field, value in json_data.items():
                setattr(ads, field, value)
            session.commit()
            return jsonify({
                'id': ads.id,
                'head': ads.head,
                'description': ads.description,
                'creationdate': ads.creationdate,
                'user': ads.username
            })

    def delete(self, ads_id):
        with Session() as session:
            ads = get_ads(ads_id, session)
            session.delete(ads)
            session.commit()
            return jsonify({'status': 'delete ok'})

class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            return jsonify({
                'id': user.id,
                'email': user.email,
                'creationdate': user.creationdate
            })

    def post(self):
        json_data = request.json
        with Session() as session:
            new_user = User(**json_data)
            session.add(new_user)
            session.commit()
            return jsonify({
                'id': new_user.id,
                'email': new_user.email,
                'creationdate': new_user.creationdate
            })

    def patch(self, user_id):
        json_data = request.json
        with Session() as session:
            user = get_user(user_id, session)
            for field, value in json_data.items():
                setattr(user, field, value)
            session.commit()
            return jsonify({
                'id': user.id,
                'email': user.email,
                'creationdate': user.creationdate
            })

    def delete(self, user_id):
        with Session() as session:
            user = get_user(user_id, session)
            session.delete(user)
            session.commit()
            return jsonify({'status': 'delete ok'})




app.add_url_rule('/ads/', view_func=AdsView.as_view('ads_new'), methods=['POST'])
app.add_url_rule('/ads/<int:ads_id>/', view_func=AdsView.as_view('ads'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user/', view_func=UserView.as_view('user_new'), methods=['POST'])
app.add_url_rule('/user/<int:user_id>/', view_func=UserView.as_view('user'), methods=['GET', 'PATCH', 'DELETE'])

if __name__ == '__main__':
    app.run()