from netCDF4 import Dataset
import numpy as np
import json


class NCFileProcessor:

    def __init__(self, filepathList, jsonFilepath):
        self.filepathList = filepathList
        self.jsonFilepath = jsonFilepath
        self.dataList = []
        self.datasetDictionary = {}
        self.factorList = []

    def removeMaskedData(self, filepath):
        dataset = Dataset(filepath, 'r')
        properties = [str(v) for v in dataset.variables]
        lons = dataset.variables[properties[0]][:]
        lats = dataset.variables[properties[1]][:]
        times = dataset.variables[properties[2]][:]
        values = dataset.variables[properties[3]][:]

        dataList = []
        for lt in xrange(len(lats)):
            for ln in xrange(len(lons)):
                contents = [lats[lt], lons[ln]]
                for t in xrange(len(times)):
                    if float(values[t, lt, ln]) is not np.nan:
                        contents.append(float(values[t, lt, ln]))
                if len(contents) > 2:
                    dataList.append(contents)
        self.factorList.append(properties[3])
        return properties[3], dataList

    def saveToJson(self):
        with open(self.jsonFilepath, 'w') as f:
            json.dump(self.datasetDictionary, f)

    def processNCFile(self):
        tempDictionary = {}
        for filepath in self.filepathList:
            factorName, values = self.removeMaskedData(filepath)
            tempDictionary[factorName] = values
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
    filepathList = ['../data/ncfile/total_cloud_cover.nc',
                    '../data/ncfile/precipitation.nc',
                    '../data/ncfile/surface_pressure.nc',
                    '../data/ncfile/temperature.nc']
    jsonFilepath = '../data/json/datasetpartHourly.json'
    processor = NCFileProcessor(filepathList, jsonFilepath)
    processor.processNCFile()
