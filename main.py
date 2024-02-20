from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from database import get_vessels, get_vessel_data
import requests
import json


app = FastAPI()
url = "https://api.sensor.community/v1/push-sensor-data/"

class Sensordata():
    sensorID: str
    XPIN: int
    sensordata: dict

    def __init__(self, sensorID, XPIN, sensordata) -> None:
        self.sensorID = sensorID
        self.XPIN = XPIN
        self.sensordata = sensordata

    def getSensorID(self) -> str:
        return self.sensorID

    def getXPIN(self) -> int:
        return self.XPIN

    def getSensordata(self) -> dict:
        return self.sensordata

#TODO SENSORDATA SETTERS
    def toCSV(self) -> str:
        return f"{self.sensorID},{self.XPIN},{self.sensordata}"

def upload_data(data: Sensordata) -> None:
    """
    Uploads the data to the sensor.community API
    And to the local database

    HEADERS:
    - Content-type: application/json
    - X-Pin: The pin representing the sensor
    - X-Sensor: The sensorID

    Parameters:
    - data (Sensordata): The data to be uploaded
    """
    headers = { 'Content-type': 'application/json',
                'X-Pin': '%s' % data.XPIN,
                'X-Sensor': '%s' % data.sensorID,
    }

#TEST
    payload = { "software_version": "1.0.0",
                "sensordatavalues": data.sensordata
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r.status_code)

def local_log(data: Sensordata) -> None:
    """
    Logs the data to a local CSV file

    Parameters:
    - data (Sensordata): The data to be logged
    """
    fp = open('logs.csv', 'a')
    fp.write(data.toCSV() + "\n")
    fp.close()


@app.get("/")
async def root() -> dict:
    return {"message": "toSensor.Community API"}


@app.post("/sensordata")
async def create_item(item: Request) -> dict:
    datapoints: list = []
    if await item.body() == b'':
        return {"message": "The request body must not be empty"}
    try:
        json = await item.json()
    except:
        return {"message": "The request body must be valid JSON"}

    try:
        data = json["data"]
        for i in data:
            datapoints.append(Sensordata(i["sensorID"], i["XPIN"], i["sensordata"]))
    except:
        return {"message": "helkp"}

    for i in datapoints:
        upload_data(i)
        local_log(i)

    return {"message": "Data received"}
