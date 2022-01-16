from flask import Flask
from datetime import datetime
#from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser


bucket = "mybucket"
MAX_COLS = 7
client = InfluxDBClient(url="http://influxdb:8086", token="MYDUMBASSADMINTOKEN", org="BrendonMcCool")
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()
#client = InfluxDBClient('influxdb', 8086, 'metrics', 'sdfwer234', 'metrics')
app = Flask(__name__)

@app.route("/hello")
def hello():
    p = Point("endpoint_request").tag("endpoint", "/hello").time(datetime.now()).field("value", 1)
    write_api.write(bucket=bucket, record=p)
    return "Hello World!"


@app.route("/bye")
def bye():
    #p = Point("endpoint_request").tag("endpoint", "/bye").time(datetime.now()).field("value", 1)
    #write_api.write(bucket=bucket, record=p)
    #write_log_data()
    return "Bye World!"

@app.route("/load")
def load():
    load_the_data()
    return "Loading World!"


def write_log_data():
    p = create_metabuild_failure({"Category": "build_failure", "process": "linux build", "rootcause": "Toolchain Issue again"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

    p = create_metabuild_failure({"Category": "build_failure", "process": "linux build", "rootcause": "Toolchain Issue again"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

    p = create_metabuild_failure({"Category": "build_failure", "process": "smalls case build", "rootcause": "Toolchain Issue again"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

    p = create_metabuild_failure({"Category": "Transient", "Subcategory": "Network Issue", "process": "spitfireupdate", "Node": "NODE 10", "rootcause": "Node offline"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

    p = create_metabuild_failure({"Category": "Transient", "Subcategory": "Network Issue", "process": "bttest", "Node": "NODE 13", "rootcause": "Node offline"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

    p = create_metabuild_failure({"Category": "Transient", "Subcategory": "Network Issue", "process": "e2etestsmalls", "Node": "NODE 10", "rootcause": "Node offline"})
    write_api.write(bucket=bucket, record=p)
    time.sleep(1)

def create_metabuild_failure(tags, timestamp=None):
    if timestamp is None: timestamp = datetime.now()
    P = Point("Metabuild Failure").time(timestamp).field("value", 1)
    for key in tags:
        P = P.tag(key, tags[key])
    return P

def load_the_data():
    HTMLFileTOBeOpened = open("load_dir/Metabuild Failures and Triaging - Spitfire Software - Bose Confluence.html", "r")
    contents = HTMLFileTOBeOpened.read()
    soup = BeautifulSoup(contents, "html.parser")
    table = soup.find(id="main-content")
    table = table.find(class_="original-table")
    table = table.find_all("tr")
    for row in table:
        columns = row.find_all("td")
        parse_columns(columns)


def get_timedate(columns):
    datetext = columns[0].find("p").text
    try:
        dt = parser.parse(datetext)
    except Exception:
        print(f"Couldn't Parse: {columns[0]}")
        print(f"Text: {datetext}")
        return None
    return dt

def get_category(columns):
    column_index_modifier = len(columns) - MAX_COLS
    category_column_index = 5 + column_index_modifier
    
    """
    build failure
    test failure
    -stage2 and stage3
    Infrastructure
    -Node issues
    Transient
    -Network
    -BT connectivity (edited) 
    """
    try:
        text = columns[category_column_index].text
        if "build failure" in text.lower(): return ("build failure", None)
        if "test failure" in text.lower():
            if "stage2" in text.lower(): return ("test failure", "stage2")
            if "stage3" in text.lower(): return ("test failure", "stage3")
            return ("test failure", "")
        if "transient" in text.lower():
            if "network" in text.lower(): return ("transient", "network")
            if "bt" in text.lower(): return ("transient", "bluetooth")
            if "bluetooth" in text.lower(): return ("transient", "bluetooth")
            return("transient", "TODO")
        if text == "": return ("TODO", "TODO")
        return (text, "NOT IMPL")
    except:
        print("Couldn't find it!")
    return ("TODO", "TODO")
    
def get_component(columns):
    column_index_modifier = len(columns) - MAX_COLS
    category_column_index = 2 + column_index_modifier
    
    """
    build failure
    test failure
    -stage2 and stage3
    Infrastructure
    -Node issues
    Transient
    -Network
    -BT connectivity (edited) 
    """
    try:
        #print(f"columns[{category_column_index}] = {columns[category_column_index].text.lower()}")
        text = columns[category_column_index].text
        if "bluetooth" in text.lower(): return ("Bluetooth")
        if "audio automation" in text.lower(): return ("Audio Automation")
        if "audioautomation" in text.lower(): return ("Audio Automation")
        if "buttons" in text.lower(): return ("Buttons")
        if "led" in text.lower(): return ("LED")
        if "smart anr" in text.lower(): return ("Smart ANR")
        if "spitfire update" in text.lower(): return ("Spitfire Update")
        if "manufacturing " in text.lower(): return ("Manufacturing ")
        if "smalls update" in text.lower(): return ("Smalls Update")
        if "sound management" in text.lower(): return ("Sound Management")
        if "bmap" in text.lower(): return ("BMAP")
        if "e2e" in text.lower(): return ("E2E Test")
        if "dataharvesting" in text.lower(): return ("DataHarvesting")
        if "security" in text.lower(): return ("Security")
        if "build" in text.lower(): return ("Build")
        if "ui" in text.lower(): return ("UI")
        if "sensor" in text.lower(): return ("Sensor")
        if "media player" in text.lower(): return ("Spitfire Media Player")
        if "testcomponent" in text.lower(): return ("Spitfire Test Component")
        

        

        if text == "": return ("TODO")
    except:
        print("Couldn't find it!")
    return ("TODO")


def get_root_cause(columns):
    column_index_modifier = len(columns) - MAX_COLS
    category_column_index = 3 + column_index_modifier
    try:
        #print(f"columns[{category_column_index}] = {columns[category_column_index].text.lower()}")
        text = columns[category_column_index].text
        if text == "": return ("TODO")
        return text #TODO truncate this

    except:
        print("Couldn't find it!")
    return ("TODO")
    

def parse_columns(columns):

    if len(columns) >= 7:
        date = get_timedate(columns)
        category, subcategory = get_category(columns)
        component = get_component(columns)
        root_cause = get_root_cause(columns)

        #print(f"{date} --- {category}/{subcategory} --- {component} --- {root_cause}")
        
        p = create_metabuild_failure({"Category": category,
                                      "Subcategory": subcategory, 
                                      "Component": component,
                                      "Rootcause": root_cause}, date)
        write_api.write(bucket=bucket, record=p)
     

    

if __name__ == "__main__":
    app.run (host="0.0.0.0")
