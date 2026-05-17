#!/usr/bin/env python3
#mit flask jabe ich mal begonnen, bin aber schon eine Zeit raus, daher evtl. mal 
#etwas anderes anschauen. Tornado scheint speziell fuer websockets zu sein, fastapi
#hat einige gute kritiken bekommen.

import argparse
import sys
import time
import json 
import threading
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

from influxdb import InfluxDBClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import requests
import solaredge_modbus

app = Flask(__name__)
socketio = SocketIO(app,async_mode='eventlet', debug=True)  # WebSocket-Unterstützung

@socketio.on('connect')
def on_connect():
    print('Client connected!')
    socketio.emit('test_event', {'message': 'Hello, Client!'})

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected!')
        
###########################################################################################################
def read_data():
    global data, json_body, inverter, args
    
    while True:
        values = {}
        values = inverter.read_all()
        meters = inverter.meters()
        batteries = inverter.batteries()

        json_body = []
        current_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        inverter_data = {
            "measurement": "inverter",
            "tags": {
#                "c_manufacturer": values["c_manufacturer"],
                "c_model": values["c_model"],
                "c_version": values["c_version"],
                "c_serialnumber": values["c_serialnumber"]
#                "c_deviceaddress": values["c_deviceaddress"],
#               "c_sunspec_did": values["c_sunspec_did"]
            },
            "time": current_time,
            "fields": {}
        }

        for k, v in values.items():
            if (isinstance(v, int) or isinstance(v, float)) and "_scale" not in k:
                k_split = k.split("_")
                scale = 0

                if f"{k_split[len(k_split) - 1]}_scale" in values:
                    scale = values[f"{k_split[len(k_split) - 1]}_scale"]
                elif f"{k}_scale" in values:
                    scale = values[f"{k}_scale"]
                if  k == "power_dc" or k == "power_ac": #starke Reduktion will aber die scale von oben mitnehmen  
                    inverter_data["fields"].update({k: float(v * (10 ** scale))})

        json_body.append(inverter_data)

        for meter, params in meters.items():
            meter_values = params.read_all()

            meter_data = {
                "measurement": "meter",
                "tags": {
#                    "c_manufacturer": meter_values["c_manufacturer"],
                    "c_model": meter_values["c_model"],
#                    "c_option": meter_values["c_option"],
                    "c_version": meter_values["c_version"],
                    "c_serialnumber": meter_values["c_serialnumber"]#,
#                    "c_deviceaddress": meter_values["c_deviceaddress"],
#                    "c_sunspec_did": meter_values["c_sunspec_did"]
                },
                "time": current_time,
                "fields": {}
            }

            for k, v in meter_values.items():
                if (isinstance(v, int) or isinstance(v, float)) and "_scale" not in k:
                    k_split = k.split("_")
                    scale = 0

                    if f"{k_split[len(k_split) - 1]}_scale" in meter_values:
                        scale = meter_values[f"{k_split[len(k_split) - 1]}_scale"]
                    elif f"{k}_scale" in meter_values:
                        scale = meter_values[f"{k}_scale"]
                    if k == "power":
                        meter_data["fields"].update({k: float(v * (10 ** scale))})

            json_body.append(meter_data)

        for battery, params in batteries.items():
            battery_values = params.read_all()
            #I see to batteries, one with c_version False and meaningless values +e38 :-)
            if not battery_values["c_model"] or battery_values["c_version"] == "False":
                continue

            battery_data = {
                "measurement": "battery",
                "tags": {
#                    "c_manufacturer": battery_values["c_manufacturer"],
                    "c_model": battery_values["c_model"],
                    "c_version": battery_values["c_version"],
                    "c_serialnumber": battery_values["c_serialnumber"]#,
#                    "c_deviceaddress": battery_values["c_deviceaddress"],
#                   "c_sunspec_did": battery_values["c_sunspec_did"]
                },
                "time": current_time,
                "fields": {}
            }

            for k, v in battery_values.items():
                #if isinstance(v, int) or isinstance(v, float)  
                if k=="soe" or k=="instantaneous_power" or k=="status":
                    battery_data["fields"].update({k: v})

            json_body.append(battery_data)
        
        #publish by web-socket
        socketio.emit('test_event', {'message': 'Hello, Client!'})
        
        try:
            data["power_ac"] = json_body[0]["fields"]["power_ac"]
            data["power_dc"] = json_body[0]["fields"]["power_dc"]
            data["power"] = json_body[1]["fields"]["power"]
            data["power_bat"] = json_body[2]["fields"]["instantaneous_power"]
            data["soe"] = json_body[2]["fields"]["soe"]
            # Senden der aktualisierten Daten an alle WebSocket-Clients
            print("Daten, die gesendet werden:", data)
            socketio.emit("update_data", data)
        
        except KeyError as e:
            # Wenn ein KeyError auftritt (z.B. falls ein Feld nicht existiert), wird dies hier abgefangen
            print(f"Fehler: Der Schlüssel {e} existiert nicht in den Daten. Weiterer Verlauf ohne diese Daten.")

        except IndexError as e:
            # Falls json_body nicht genug Elemente enthält (IndexError)
            print(f"Fehler: Index {e} außerhalb des gültigen Bereichs in json_body. Weiterer Verlauf ohne diese Daten.")

        except Exception as e:
            # Allgemeiner Fehler, der nicht abgedeckt ist
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")


        time.sleep(args.interval_read)
###########################################################################################################
def write_to_db():
    global influx, args, json_body 
    while True:
        #influx.write(args.influx_db, org, json_body) # der eigentliche schreibprozess
        #print(json.dumps(json_body,indent=2))
        #sys.exit()
        time.sleep(args.interval_write)

############################################################################################################

# API Route, um Daten bereitzustellen
@app.route('/data', methods=['GET'])
def get_data():
    global json_body
    return jsonify(json_body)
    
@app.route('/')
def index():
    #with data_lock:
    return render_template('indexWebSocket.html', data=data)




if __name__ == "__main__":
    # read some configuration
    with open("myConfig.json", "r") as file:
        config = json.load(file)
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--host", type=str, default=config["modbusHost"], help="Modbus TCP address")
    argparser.add_argument("--port", type=int, default=config["modbusPort"], help="Modbus TCP port")
    argparser.add_argument("--timeout", type=int, default=1, help="Connection timeout")
    argparser.add_argument("--unit", type=int, default=1, help="Modbus device address")
    argparser.add_argument("--interval_read", type=int, default=config["intervalRead"], help="Update interval read")
    argparser.add_argument("--interval_write", type=int, default=config["intervalWrite"], help="Update interval write to influx")
    argparser.add_argument("--influx_url", type=str, default=config["influxUrl"], help="InfluxDB URL")
    argparser.add_argument("--influx_org", type=str, help=config["influxOrg"])
    argparser.add_argument("--influx_bucket", type=str, default=config["influxBucket"], help="InfluxDB bucket")
    argparser.add_argument("--influx_token", type=str, default=config["influxToken"],help="InfluxDB token")
    args = argparser.parse_args()

    try:
        influx_client = InfluxDBClient(
            url=args.influx_url,
            token=args.influx_token,
            org=args.influx_org,
        )
        influx = influx_client.write_api(write_options=SYNCHRONOUS)
    except (ConnectionRefusedError, requests.exceptions.ConnectionError):
        print(f"Database connection failed: {args.influx_url}")
        sys.exit()

    inverter = solaredge_modbus.Inverter(
        host=args.host,
        port=args.port,
        timeout=args.timeout,
        unit=args.unit
    )
    
    json_body= {"measurement": "not set"}
    data = {}
    data["power_ac"] = 0
    data["power_dc"] = 0
    data["power"] = 0
    data["power_bat"] = 0
    data["soe"] = 0



    #start threads for reading and writing
    data_thread = threading.Thread(target=read_data, daemon=True)
    data_thread.start()
    
    db_thread = threading.Thread(target=write_to_db, daemon=True)
    db_thread.start()
    
    time.sleep(10) #warte ein wenig, damit die Daten vorliegen

    #app.run(host='0.0.0.0', port=8090)
    socketio.run(app, host='0.0.0.0', port=8090,debug=True)

            