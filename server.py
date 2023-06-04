from flask import Flask, jsonify, request
from flask.views import MethodView
from models import Session, AdsTable, User
from typing import Type
from schema import CreateAds, PatchAds, CreateUser, PatchUser
from pydantic import ValidationError
from hashlib import md5
from sqlalchemy.exc import IntegrityError

app = Flask('app')

class HttpError(Exception):
    """
    Класс необходим для вывода ошибок пользователю
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    """
    Функция вовзращает ошибку пользователю
    """
    response = jsonify({'status': 'error', 'message': error.message})
    response.status_code = error.status_code
    return response

def get_ads(ads_id: int, session: Session):
    """
    Получение объявления
    :param ads_id: id объявления
    """
    ads = session.get(AdsTable, ads_id)
    if ads is None:
        raise HttpError(404, message='ads is not found')
    return ads

def get_user(user_id: int, session: Session):
    """
    Получение пользователя по id
    :param user_id: id пользователя
    """
    user = session.get(User, user_id)
    if user is None:
        raise HttpError(404, message='user is not found')
    return user

def get_user_name(user_name, session: Session):
    """
    Получение пользователя по email
    :param user_name: email
    """
    user = session.query(User).filter(User.email == user_name).all()
    if not user:
        raise HttpError(404, message='user is not found')
    return user

def validate(json_data, model_class: Type[CreateAds] | Type[PatchAds]):
    """
    Валидация создания/редактирования объявления
    :param json_data: запрос пришедший от пользователя
    """
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, err.errors())

def validate_user(json_data, model_class: Type[CreateUser] | Type[PatchUser]):
    """
    Валидация создания/редактирования пользователя
    :param json_data: запрос пришедший от пользователя
    """
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, err.errors())

def get_permission(json_data):
    """
    Функция проверяет соответствие поступаемых данных пользователя (email и password) с данными в базе
    :param json_data:
    :return: json_data
    """
    with Session() as session:
        user = get_user_name(json_data.pop('username'), session)
        password = json_data.pop('password')
        password = password.encode()
        hashed_password = md5(password).hexdigest()
        if not (user[0].password == hashed_password):
            raise HttpError(401, message='Wrong password')
        json_data['username'] = user[0].id
        return json_data

class AdsView(MethodView):
    """
    Класс для CRUD с моделью AdsTable
    """

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
        json_data = get_permission(json_data)
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
        json_data = get_permission(json_data)
        with Session() as session:
            ads = get_ads(ads_id, session)
            if not(json_data['username'] == ads.username):
                raise HttpError(401, message='Wrong user')
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
        json_data = validate(request.json, PatchAds)
        json_data = get_permission(json_data)
        with Session() as session:
            ads = get_ads(ads_id, session)
            if not(json_data['username'] == ads.username):
                raise HttpError(401, message='Wrong user')
            session.delete(ads)
            session.commit()
            return jsonify({'status': 'delete ok'})

class UserView(MethodView):
    """
    Класс для CRUD с моделью User
    """

    def get(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            return jsonify({
                'id': user.id,
                'email': user.email,
                'creationdate': user.creationdate
            })

    def post(self):
        json_data = validate_user(request.json, CreateUser)
        password = json_data['password']
        password = password.encode()
        hashed_password = md5(password).hexdigest()
        json_data['password'] = hashed_password
        with Session() as session:
            new_user = User(**json_data)
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError as err:
                raise HttpError(409, 'user already exists')
            return jsonify({
                'id': new_user.id,
                'email': new_user.email,
                'creationdate': new_user.creationdate
            })

    def patch(self, user_id):
        json_data = validate_user(request.json, PatchUser)
        password = json_data['password']
        password = password.encode()
        hashed_password = md5(password).hexdigest()
        json_data['password'] = hashed_password
        with Session() as session:
            user = get_user(user_id, session)
            for field, value in json_data.items():
                setattr(user, field, value)
            try:
                session.commit()
            except IntegrityError as err:
                raise HttpError(409, 'user already exists')
            return jsonify({
                'id': user.id,
                'email': user.email,
                'creationdate': user.creationdate
            })




app.add_url_rule('/ads/', view_func=AdsView.as_view('ads_new'), methods=['POST'])
app.add_url_rule('/ads/<int:ads_id>/', view_func=AdsView.as_view('ads'), methods=['GET', 'PATCH', 'DELETE'])
app.add_url_rule('/user/', view_func=UserView.as_view('user_new'), methods=['POST'])
app.add_url_rule('/user/<int:user_id>/', view_func=UserView.as_view('user'), methods=['GET', 'PATCH'])

if __name__ == '__main__':
    app.run()