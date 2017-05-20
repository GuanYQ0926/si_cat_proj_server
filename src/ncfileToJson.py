from netCDF4 import Dataset
import numpy as np
import json


class NCFileProcessor:
    '''
    1.remove masked data
    2.convert hourly data into daily data
    3.save to json [lat, lon, [factor:value]]
    '''

    def __init__(self, filepathList, jsonFilepath):
        self.filepathList = filepathList
        self.jsonFilepath = jsonFilepath
        self.datasetDictionary = {}
        self.factorList = []

    def removeMaskedDataConvertToDailyData(self, filepath):
        dataset = Dataset(filepath, 'r')
        properties = [str(v) for v in dataset.variables]
        lons = dataset.variables[properties[0]][:]
        lats = dataset.variables[properties[1]][:]
        times = dataset.variables[properties[2]][:]
        values = dataset.variables[properties[3]][:]

        dataList = []
        for lt in xrange(len(lats)):
            for ln in xrange(len(lons)):
                num = 1
                temp_day = 0
                recorded_count = 0
                contents = [lats[lt], lons[ln]]
                for t in xrange(len(times)):
                    if float(values[t, lt, ln]) is not np.nan:
                        temp_day += float(values[t, lt, ln])
                        recorded_count += 1
                    if num % 24 == 0 and recorded_count > 0:
                        contents.append(temp_day / float(recorded_count))
                        temp_day = 0
                        recorded_count = 0
                    num += 1
                if len(contents) > 2:
                    dataList.append(contents)
        self.factorList.append(properties[3])
        return properties[3], dataList  # valueName, [[],...,[]]

    def saveToJson(self):
        with open(self.jsonFilepath, 'w') as f:
            json.dump(self.datasetDictionary, f)

    # convert to daily data
    def processNCFile(self):
        tempDictionary = {}
        for filepath in self.filepathList:
            factorName, values = self.removeMaskedDataConvertToDailyData(
                filepath)
            tempDictionary[factorName] = values
            print(len(values))
        # reform data structure and save into self.datasetDictionary
        for i in xrange(len(tempDictionary[self.factorList[0]])):
            oneplaceDictionary = {}
            coLat = str(round(tempDictionary[self.factorList[0]][i][0], 1))
            coLon = str(round(tempDictionary[self.factorList[0]][i][1], 1))
            for l in xrange(len(tempDictionary)):
                oneplaceDictionary[self.factorList[l]] = tempDictionary[
                    self.factorList[l]][i][2:]
            self.datasetDictionary[coLat + '_' + coLon] = oneplaceDictionary
        self.saveToJson()


if __name__ == '__main__':
    # all data (daily)
    # filepathList = ['../data/ncfile/dew_point_depression.nc',
    #                 '../data/ncfile/high_cloud_cover.nc',
    #                 '../data/ncfile/low_cloud_cover.nc',
    #                 '../data/ncfile/medium_cloud_cover.nc',
    #                 '../data/ncfile/total_cloud_cover.nc',
    #                 '../data/ncfile/pecipitable_water.nc',
    #                 '../data/ncfile/precipitation.nc',
    #                 '../data/ncfile/surface_pressure.nc',
    #                 '../data/ncfile/temperature.nc']
    # jsonFilepath = '../data/json/dataset.json'
    # processor = NCFileProcessor(filepathList, jsonFilepath)
    # processor.processNCFile()

    # part data (daily)
    filepathList = ['../data/ncfile/total_cloud_cover.nc',
                    '../data/ncfile/precipitation.nc',
                    '../data/ncfile/surface_pressure.nc',
                    '../data/ncfile/temperature.nc']
    jsonFilepath = '../data/json/datasetpart.json'
    processor = NCFileProcessor(filepathList, jsonFilepath)
    processor.processNCFile()
