#
# Created by Berke Akyıldız on 11/June/2019
#
import sys
import json
import subprocess
import os


import requests

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


def convertFromHTMLTableToJSON(string):
    table_data = [[cell.text for cell in row("td")]
                  for row in BeautifulSoup(string, features="html.parser")("tr")]
    return json.dumps(dict(table_data))


def writeToHtml(str, fileName, fileType, outputPath):
    f = open(outputPath + fileName + "_" + fileType + ".html", "w")
    f.write(str)
    f.close()


def writeToJSON(str, fileName, fileType, outputPath):
    json = open(outputPath + fileName + "_" + fileType + ".json", "w")
    json.write(str)
    json.close()


def findLocationONLINE(GPS_Position, fileName, fileType, outputPath):
    output = open(outputPath + fileName + "_" + fileType + ".txt", "w")
    geolocator = Nominatim(user_agent="PROCESS")
    location = geolocator.reverse(GPS_Position)
    print(location.address)
    output.write(location.address)
    output.close()


def isImage(fileType):
    return fileType == "JPEG" or fileType == "JPG" or fileType == "PNG" or fileType == "GIF" or fileType == "TIFF" or fileType == "PSD" or fileType == "PDF" or fileType == "EPS" or fileType == "AI" or fileType == "INDD" or fileType == "RAW"


def internet_on():
    url = 'http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False


def main():
    arguments = sys.argv
    usage = "USAGE: python process.py [FILE PATH] [OPTIONS]\nUse -h for help."
    help = usage + "\n[OPTIONS]\n-o : USAGE: python process.py [FILE PATH] -o [OUTPUT PATH]"
    if len(arguments) >= 2:
        if arguments[1] == "-h":
            print(help)
            sys.exit()
        path = arguments[1]
        path.replace("\\", "\\\\")
        # test = subprocess.run(['exiftool', '-n', path], stdout=subprocess.PIPE)
        # string = test.stdout.decode("UTF-8")
        # print(string)
        result = subprocess.run(['exiftool', '-h', '-n', path], stdout=subprocess.PIPE)
        normal_string = result.stdout.decode("UTF-8")

        jsonString = convertFromHTMLTableToJSON(normal_string)

        jsonData = json.loads(jsonString)

        if "File Type" in jsonData:
            fileType = jsonData["File Type"]
        else:
            fileType = "UNKNOWN FILE TYPE"

        fileName = jsonData["File Name"]
        fileSize = jsonData["File Size"]

        if len(arguments) == 4:
            if arguments[2] == "-o":
                arguments[3].replace("\\", "\\\\")
                outputPath = arguments[3] + fileName + "_" + fileType + "\\"
        else:
            outputPath = fileName + "_" + fileType + "\\"
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        writeToHtml(normal_string, fileName, fileType, outputPath)
        writeToJSON(jsonString, fileName, fileType, outputPath)

        if isImage(fileType):
            if "GPS Position" in jsonData:
                GPS_Pos = jsonData["GPS Position"]
                GPS_Lon = jsonData["GPS Longitude"]
                GPS_Lat = jsonData["GPS Latitude"]
                if internet_on():
                    findLocationONLINE(GPS_Pos, fileName, fileType, outputPath)
            else:
                print("No GPS Information in Image")
    else:
        print(usage)
        sys.exit()


if __name__ == "__main__":
    main()
