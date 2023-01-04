try:
    import sundanceRS485
except ImportError:
    import sundanceRS485 as SundanceRS485

import asyncio
import paho.mqtt.client as mqtt
import os
from datetime import datetime
from collections import OrderedDict
import json

mqtt_host = "192.168.50.178" #os.environ.get("MQTT_HOST")
mqtt_port = 1883 #int(os.environ.get("MQTT_PORT"))
mqtt_user = "user" #os.environ.get("MQTT_USER")
mqtt_password = "mqttuserx" #os.environ.get("MQTT_PASSWORD")

serial_ip = "192.168.50.53" #os.environ.get("SERIAL_IP")
serial_port = 8899 #int(os.environ.get("SERIAL_PORT"))

base_topic = "homeassistant"
flora_name = "hottub"

currenttemp_topic = '{}/climate/{}/currenttemp'.format(flora_name, flora_name.lower())
currentsetpoint_topic = '{}/climate/{}/currentsetpoint'.format(flora_name, flora_name.lower()) 
setpoint_topic = '{}/climate/{}/setpoint'.format(flora_name, flora_name.lower()) 
state_topic = '{}/climate/{}/state'.format(flora_name, flora_name.lower()) 
modes = ["heat"];

def on_connect(mqttc, obj, flags, rc):
    print("Connected to MQTT.")


def on_message(mqttc, obj, msg):
    print(
        "MQTT message received on topic: "
        + msg.topic
        + " with value: "
        + msg.payload.decode()
    )
    if msg.topic == setpoint_topic:
        spa.targetTemp = float(msg.payload.decode())
    else:
        print("No logic for this topic, discarding.")


async def read_spa_data(spa, lastupd):
    await asyncio.sleep(1)
    if spa.lastupd != lastupd:
        lastupd = spa.lastupd
        print(
            "New data as of "
            + datetime.utcfromtimestamp(spa.lastupd).strftime("%d-%m-%Y %H:%M:%S")
        )

        data = OrderedDict()

        print("Set Temp: {0}".format(spa.get_settemp()))
        print("Current Temp: {0}".format(spa.curtemp))
        
        mqtt_client.publish(currenttemp_topic, spa.curtemp, retain=True)
        
        mqtt_client.publish(currentsetpoint_topic, spa.get_settemp(), retain=True) 
        mqtt_client.publish(state_topic, "heat", retain=True) 

        print()
    return lastupd


async def start_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client("jacuzzi_rs485")
    mqtt_client.username_pw_set(username=mqtt_user, password=mqtt_password)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(mqtt_host, mqtt_port)
    mqtt_client.loop_start()



    discovery_topic = 'homeassistant/climate/{}/{}/config'.format(flora_name.lower(), "temperature")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "temperature")
    payload['unique_id'] = "{}-{}".format("Jorgensen","123")
    #payload['unit_of_measurement'] = "°F"
    #payload['type'] = "climate"
    #payload['state_class'] = params['state_class']
    payload['value_template'] = "{{value}}"
    payload['current_temperature_topic'] = currenttemp_topic
    payload['current_temperature_template'] = "{{value}}"
    payload['temperature_command_topic'] = setpoint_topic
    payload['temperature_state_topic'] = currentsetpoint_topic
    payload['temperature_state_template'] = "{{value}}"
    payload['mode_state_topic'] = state_topic
    payload['icon'] = "mdi:hot-tub"
    payload['modes'] = modes
    payload['temp_step'] = "1"
    payload['precision '] = "1"
    payload['tempUnit  '] = "°F"
    payload['min_temp'] = "60"
    payload['max_temp'] = "104"
    payload['device'] = {
            'identifiers' : ["HotTub"],
            'manufacturer' : 'Sundance',
            'name' : flora_name,
            'model' : 'TBD',
    }
    payload['expire_after'] = str(int(300 * 1.5))
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)


    # Subscribe to MQTT
    mqtt_client.subscribe(setpoint_topic)




async def start_app():
    """Test a miniature engine of talking to the spa."""
    global spa
    # Connect to MQTT
    await start_mqtt()

    # Connect to Spa (Serial Device)
    spa = sundanceRS485.SundanceRS485(serial_ip, serial_port)
    await spa.connect()

    asyncio.ensure_future(spa.listen())
    lastupd = 0

    while True:
        lastupd = await read_spa_data(spa, lastupd)


if __name__ == "__main__":
    asyncio.run(start_app())