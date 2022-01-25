from http import HTTPStatus

from flask import Blueprint
from flask_jwt_extended import jwt_required

from utils.models import MedDataSet, CorrSet
from utils.tools import post_load, save_to_db, save_correlation, get_load, get_correlation

medical = Blueprint('medical', __name__)


@medical.route('calculate', methods=['POST'])
@jwt_required()
def calculate():
    med_info = post_load(MedDataSet)
    x_params = med_info.data['x']
    y_params = med_info.data['y']
    user_id = med_info.user_id
    x_data_type = med_info.data['x_data_type']
    y_data_type = med_info.data['y_data_type']
    if x_data_type == y_data_type:
        return {'msg': 'Одинаковые названия метрик недопустимы'}, HTTPStatus.BAD_REQUEST

    save_to_db(x_params, y_params, user_id, x_data_type, y_data_type)
    save_correlation(x_data_type, y_data_type, user_id)
    return {'msg': 'Запись создана'}, HTTPStatus.CREATED


@medical.route('correlation', methods=['GET'])
@jwt_required()
def correlation():
    params = get_load(CorrSet)
    return get_correlation(params)
