import os
import json
import numpy as np
from flask import Flask
from flask_restful import abort, Api, Resource
from functools import wraps

app = Flask(__name__)
api = Api(app)
datasetpart = {}
datasetparthourly = {}


def cors(func, allow_origin=None, allow_headers=None, max_age=None):
    if not allow_origin:
        allow_origin = "*"
    if not allow_headers:
        allow_headers = "content-type, accept"
    if not max_age:
        max_age = 60

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        cors_headers = {
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": func.__name__.upper(),
            "Access-Control-Allow-Headers": allow_headers,
            "Access-Control-Max-Age": max_age,
        }
        if isinstance(response, tuple):
            if len(response) == 3:
                headers = response[-1]
            else:
                headers = {}
            headers.update(cors_headers)
            return (response[0], response[1], headers)
        else:
            return response, 200, cors_headers
    return wrapper


def abortIfNotExist(fileName):
    filepath = '../data/json/' + fileName
    if not os.path.exists(filepath):
        abort(404, message="{} doesn't exist".format(fileName))


class Resource(Resource):
    method_decorators = [cors]


def binarySearch(array, t):
    '''
    return the index of where t should be inserted in
    '''
    if len(array) == 0:
        return 0
    low = 0
    height = len(array) - 1
    while low <= height:
        mid = (low + height) / 2
        if array[mid] < t:
            low = mid + 1
            mid += 1
        elif array[mid] > t:
            height = mid - 1
        else:
            return mid
    return mid


def calculateCorrcoef(dataset, data):
    '''
    return the ordered corrcoef
    '''
    src_data = data['rain']
    corr_results = []
    index_results = []

    top_corr_data = []
    heat_corr_data = []
    return_dict = {}
    for key in dataset:
        dist_data = dataset[key]['rain']
        temp_corr = np.corrcoef(src_data, dist_data)[0, 1]
        # fill heat data
        heat_corr_data.append([key, temp_corr])
        # fill top twenty's index
        index = binarySearch(corr_results, temp_corr)
        index_results.insert(index, key)
        # fill top twenty's corr
        corr_results.insert(index, temp_corr)

    top_twenty_index = index_results[-20:]
    for i in top_twenty_index:
        top_corr_data.append([i, dataset[i]])

    return_dict['top_corr_data'] = top_corr_data
    return_dict['heat_corr_data'] = heat_corr_data

    return return_dict  # corr_results


class DataResource(Resource):

    def get(self, parameters):
        lat_lon = parameters.split('_')
        lat = round(float(lat_lon[0]) * 5) / 5
        lon = round(float(lat_lon[1]) * 5) / 5
        lat_lon = str(lat) + '_' + str(lon)
        '''
        calculate corr
        [ lat_lon: [ttd:[], clh:[], cll:[], clm:[], cla:[], tpw:[],
                    rain:[], psurf[], tmp:[]] ]
        http://d4pdf.diasjp.net/d4PDF.cgi?target=RCM-subset&lang=ja
        '''
        try:
            data = datasetpart[lat_lon]
            return calculateCorrcoef(datasetpart, data)
        except:
            abort(404, message="data in {} doesn't exist".format(lat_lon))


class HourlyResource(Resource):

    def get(self, parameters):
        latlons = parameters.split('|')
        target_latlon = latlons[0]
        compared_lonlat = latlons[1]
        data = [datasetparthourly[target_latlon]['tmp'],
                datasetparthourly[compared_lonlat]['tmp']]
        return data


api.add_resource(DataResource, '/data/<parameters>')
api.add_resource(HourlyResource, '/hourly/<parameters>')

if __name__ == '__main__':
    jsonDataPath = '../data/json/datasetpart.json'
    jsonHourlyDataPath = '../data/json/datasetpartHourly.json'
    with open(jsonDataPath, 'r') as f1, open(jsonHourlyDataPath, 'r') as f2:
        datasetpart = json.load(f1)
        datasetparthourly = json.load(f2)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
