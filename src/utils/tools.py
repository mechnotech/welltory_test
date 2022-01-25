import hmac
import json
from functools import wraps
from http import HTTPStatus
from typing import Tuple, Union, Optional, Any

from flask import make_response, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jti,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from orjson import orjson
from pydantic import ValidationError
from werkzeug.exceptions import abort

from db_models.models import User, JwtRefresh, Login, Metric, MetricData, MetricUser, MetricResult
from dbs.db import db, cache
from settings import JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES, SALT
from utils.models import UserSet, LogSet
import pandas as pd


def show_error(text: Optional[Any], http_code: int):
    return abort(make_response(jsonify({'msg': text}), http_code))


def sign(password: str) -> str:
    sig = hmac.new(key=SALT.encode('utf-8'), msg=password.encode('utf-8'), digestmod='sha256')
    return sig.hexdigest()


def get_user_tokens(user) -> Tuple[str, str]:
    access_token = create_access_token(identity=user.login)
    refresh_token = create_refresh_token(identity=user.login)
    return access_token, refresh_token


def get_user_by_id(user_id):
    return User.query.filter_by(id=user_id).first()


def is_user_exists(user: Union[UserSet, str], check_email=None) -> Optional[User]:
    User.query.all()
    if check_email:
        return (
            User.query.filter_by(login=user.login).one_or_none() or User.query.filter_by(email=user.email).one_or_none()
        )
    return User.query.filter_by(login=user).one_or_none()


def is_password_correct(hashed_password: str, password_to_check: str):
    return hashed_password == sign(password_to_check)


def is_token_revoked(jwt_id: str):
    return cache.get(jwt_id)


def get_key_to_cache(login: str, url: str) -> str:
    return f'{login}-{url}'


def to_cache_expired(jwt_id: str, token_type='refresh'):
    """
    Храним в Кэше только подписи от JWT как ключи, так-как они уникальны,
    Значением же будет 1, так короче и вернет True при последующем запросе их кэша
    :param jwt_id: Подпись JWT токена
    :param token_type: Тип токена assess или refresh
    :return:
    """
    if token_type == 'refresh':
        ttl = int(JWT_REFRESH_TOKEN_EXPIRES.total_seconds())
    else:
        ttl = int(JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
    cache.setex(jwt_id, ttl, 1)


def update_jwt_db(user, refresh_token: str):
    JwtRefresh.query.all()
    jwt_record = JwtRefresh.query.filter_by(user_id=user.id).first()
    jwt_record.refresh_token = refresh_token
    db.session.add(jwt_record)
    db.session.commit()


def do_checkout(user, info: str, status='login', jwt_id=Optional[str], refresh_token=Optional[str]):
    JwtRefresh.query.all()
    jwt_record = JwtRefresh.query.filter_by(user_id=user.id).first()
    if status == 'logout':
        refresh_jwt_id = get_jti(jwt_record.refresh_token)
        to_cache_expired(jwt_id=jwt_id, token_type='access')
        to_cache_expired(jwt_id=refresh_jwt_id)
    if status == 'login':
        jwt_record.refresh_token = refresh_token
        db.session.add(jwt_record)
    login = Login(user_id=user.id, info=info, status=status)
    db.session.add(login)
    db.session.commit()


def register_user_data(refresh_token, user: UserSet):
    new_user = User(login=user.login, password=sign(user.password), email=user.email)
    db.session.add(new_user)
    db.session.commit()
    User.query.all()
    db_user = User.query.filter_by(login=user.login).first()

    jwt_token = JwtRefresh(user_id=db_user.id, refresh_token=refresh_token)

    db.session.add(jwt_token)
    db.session.commit()


def get_logins(user):
    Login.query.all()
    logins = Login.query.filter_by(user_id=user.id).all()
    result = [orjson.loads(LogSet(created_at=x.created_at, info=x.info, status=x.status).json()) for x in logins]
    return result


def user_sets():
    user_login = get_jwt_identity()
    body = get_jwt()
    jwt_id = body.get('jti')
    if is_token_revoked(jwt_id):
        return show_error('token был отозван', HTTPStatus.UNAUTHORIZED)
    user = is_user_exists(user_login)
    if not user:
        return show_error('Такой пользователь не существует!', HTTPStatus.NOT_FOUND)
    return user, jwt_id


def post_load(obj):
    if not request.json:
        return abort(make_response(jsonify({'msg': 'Пустой запрос'}), HTTPStatus.BAD_REQUEST))
    try:
        entity = obj(**request.json)
    except ValidationError as e:
        return show_error(e.errors(), HTTPStatus.BAD_REQUEST)
    return entity


def get_load(obj):
    if not request.args:
        return abort(make_response(jsonify({'msg': 'Ожидаются аргументы'}), HTTPStatus.BAD_REQUEST))
    try:
        entity = obj(**request.args)
    except ValidationError as e:
        return show_error(e.errors(), HTTPStatus.BAD_REQUEST)
    return entity


def get_correlation(params):
    metric_first = Metric.query.filter_by(user_id=params.user_id, metric_name=params.x_data_type).one_or_none()
    metric_second = Metric.query.filter_by(user_id=params.user_id, metric_name=params.y_data_type).one_or_none()
    if not metric_first or not metric_second:
        return show_error('Такая метрика(и) не найдены', HTTPStatus.NOT_FOUND)
    result = MetricResult.query.filter_by(
        user_id=params.user_id, metric_first=metric_first.id, metric_second=metric_second.id
    ).one_or_none()
    if not result:
        return show_error('Результаты не найдены', HTTPStatus.NOT_FOUND)
    response = {
        'user_id': params.user_id,
        'x_data_type': params.x_data_type,
        'y_data_type': params.y_data_type,
        'correlation': {'value': result.value, 'p_value': result.p_value,},
    }
    return response


def get_or_create(model: db.Model, **kwargs):
    instance = model.query.filter_by(**kwargs).one_or_none()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return get_or_create(model, **kwargs)


def save_metric(user_id: int, metric_name: str, metric_data: list):
    metric = get_or_create(Metric, user_id=user_id, metric_name=metric_name)
    exist_dates = [str(x.metric_date) for x in MetricData.query.filter_by(metric_id=metric.id).all()]
    for i in metric_data:
        data = MetricData(metric_id=metric.id, metric_date=i['date'], metric_value=i['value'])
        if str(i['date']) not in exist_dates:
            db.session.add(data)
    db.session.commit()
    return metric


def save_to_db(x_params: list, y_params: list, user_id: int, x_data_type: str, y_data_type: str):
    get_or_create(MetricUser, id=user_id)
    save_metric(user_id=user_id, metric_name=x_data_type, metric_data=x_params)
    save_metric(user_id=user_id, metric_name=y_data_type, metric_data=y_params)


def extract_values(metric):
    values = MetricData.query.filter_by(metric_id=metric.id).all()
    return values


def calculate_updated_corr(metric_first, metric_second):
    combined_data = dict()
    to_calculate = dict()
    x_data = extract_values(metric_first)
    y_data = extract_values(metric_second)
    for x in x_data:
        combined_data[x.metric_date] = {metric_first.metric_name: x.metric_value}
    for y in y_data:
        value = combined_data.get(y.metric_date)
        if not value:
            value = {}
        value[metric_second.metric_name] = y.metric_value
        combined_data[y.metric_date] = value
        if len(value) > 1:
            to_calculate[y.metric_date] = value
    to_calculate = sorted(to_calculate.items())
    df = pd.DataFrame([x[1] for x in to_calculate])
    corr = df[metric_first.metric_name].corr(df[metric_second.metric_name])
    return float(corr)


def save_correlation(x_data_type: str, y_data_type: str, user_id: int):
    metric_first = Metric.query.filter_by(user_id=user_id, metric_name=x_data_type).one_or_none()
    metric_second = Metric.query.filter_by(user_id=user_id, metric_name=y_data_type).one_or_none()
    if not metric_second or not metric_first:
        return
    result = MetricResult.query.filter_by(
        user_id=user_id, metric_first=metric_first.id, metric_second=metric_second.id
    ).one_or_none()
    if result:
        corr = calculate_updated_corr(metric_first, metric_second)
        result.value = corr
        db.session.add(result)
        db.session.commit()

    else:
        corr = calculate_updated_corr(metric_first, metric_second)
        result = MetricResult(user_id=user_id, metric_first=metric_first.id, metric_second=metric_second.id, value=corr)
        db.session.add(result)
        db.session.commit()

    return result


def cache_it(ttl=JWT_ACCESS_TOKEN_EXPIRES):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user, jwt_id = user_sets()
            url = request.base_url
            key = get_key_to_cache(user.login, url)
            value = cache.get(key)
            if not value:
                value = f(*args, **kwargs)
            else:
                cache.setex(key, ttl, value)
                return json.loads(value)
            cache.setex(key, ttl, json.dumps(value))
            return value

        return wrapper

    return decorator
