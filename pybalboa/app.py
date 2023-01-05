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

current_temperature_topic = '{}/current_temperature_topic'.format(flora_name)
temperature_state_topic  = '{}/temperature_state_topic'.format(flora_name)
temperature_command_topic = '{}/temperature_command_topic'.format(flora_name)
mode_state_topic = '{}/mode_state_topic'.format(flora_name)
action_topic = '{}/action_topic'.format(flora_name)
availability_topic = '{}/availability_topic'.format(flora_name)
pump1_command_topic = '{}/pump1_command_topic'.format(flora_name)
pump1_state_topic = '{}/pump1_state_topic'.format(flora_name)
pump2_command_topic = '{}/pump2_command_topic'.format(flora_name)
pump2_state_topic = '{}/pump2_state_topic'.format(flora_name)
ciculationmanual_command_topic = '{}/ciculationmanual_command_topic'.format(flora_name)
ciculationmanual_state_topic = '{}/ciculationmanual_state_topic'.format(flora_name)
ciculationpump_state_topic = '{}/ciculationpump_state_topic'.format(flora_name)
brightness_command_topic  = '{}/brightness_command_topic'.format(flora_name)
brightness_state_topic = '{}/brightness_state_topic'.format(flora_name)
light_command_topic = '{}/light_command_topic'.format(flora_name)
rgb_state_topic  = '{}/rgb_state_topic'.format(flora_name)
effect_state_topic  = '{}/effect_state_topic'.format(flora_name)
effect_command_topic   = '{}/effect_command_topic'.format(flora_name)
light_state_topic = '{}/light_state_topic '.format(flora_name)

modes = ["heat"];

deviceInfo = {
            'identifiers' : ["HotTub"],
            'manufacturer' : 'Sundance',
            'name' : flora_name,
    }




def on_connect(mqttc, obj, flags, rc):
    print("Connected to MQTT.")


def on_message(mqttc, obj, msg):
    print(
        "MQTT message received on topic: "
        + msg.topic
        + " with value: "
        + msg.payload.decode()
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    if msg.topic == temperature_command_topic:
        loop.run_until_complete(spa.send_temp_change(float(msg.payload.decode())))
    elif msg.topic == pump1_command_topic:
        loop.run_until_complete(spa.change_pump(0, float(msg.payload.decode())))
    elif msg.topic == pump2_command_topic:
        loop.run_until_complete(spa.change_pump(1, float(msg.payload.decode())))
    elif msg.topic == ciculationmanual_command_topic:
        loop.run_until_complete(spa.change_pump(2, float(msg.payload.decode())))
    elif msg.topic == brightness_command_topic:
        command = float(msg.payload.decode())
        if command == 0:
            res = "White"
            for x,y in spa.LIGHT_MODE_MAP:
                if x == spa.lightMode:
                   res = y 
                   break
            spa.lastRGBMode = res 
            loop.run_until_complete(spa.change_rgbmode(0, 0))  
        elif command > 0 and spa.spa.lightMode == 0:
            loop.run_until_complete(spa.change_rgbmode(0, spa.lastRGBMode))
            loop.run_until_complete(spa.change_rgbbrightness(0, float(msg.payload.decode())))
        else:
            loop.run_until_complete(spa.change_rgbbrightness(0, float(msg.payload.decode())))
    elif msg.topic == light_command_topic:
        command = float(msg.payload.decode())
        if command == 0:
            res = "White"
            for x,y in spa.LIGHT_MODE_MAP:
                if x == spa.lightMode:
                   res = y 
                   break
            spa.lastRGBMode = res
            loop.run_until_complete(spa.change_rgbmode(0, 0))
        else:
            loop.run_until_complete(spa.change_rgbmode(0, spa.lastRGBMode))
    elif msg.topic == effect_command_topic:
        command = msg.payload.decode()
        loop.run_until_complete(spa.change_rgbmode(0, command))
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

        print("CRC Errors: {0}".format(spa.crcerror))
        print("Dropped Bytes: {0}".format(spa.dropped))
        print("Last Command Attempts: {0}".format(spa.attemptsToCommand))
        
        print("Current Temp: {0}".format(spa.curtemp))
        print("Current Temp2: {0}".format(spa.temp2))
        print("Set Temp: {0}".format(spa.get_settemp()))          
        print("Target Temp: {0}".format(spa.targetTemp))  
        print("Heat State: {1} {0}".format(spa.get_heatstate(True),spa.heatState2))
        print("Pump Status: {0}".format(str(spa.pump_status)))
        print("Pump Target Status: {0}".format(str(spa.target_pump_status)))
        print("Circulation Pump: {0}  Auto:  {1}  Manual: {2}  Unkfield: {3}".format(spa.get_circ_pump(True), spa.autoCirc, spa.manualCirc, spa.unknownCirc))

        res = "unknown"
        for x,y in spa.DISPLAY_MAP:
            if x == spa.get_displayText():
               res = y 
               break
        
        print("Display Text: {} {} ".format(spa.get_displayText(),res))
        
        
        res = "unknown"
        for x,y in spa.HEAT_MODE_MAP:
            if x == spa.get_heatMode():
               res = y 
               break
        
        print("Heat Mode: {} {} ".format(spa.get_heatMode(), res))
        
        print("UnknownField3: {}".format(spa.UnknownField3))
        print("UnknownField9: {}".format(spa.UnknownField9))

        lightModeText = "unknown"
        for x,y in spa.LIGHT_MODE_MAP:
            if x == spa.lightMode:
               lightModeText = y 
               break

        print("Light Status: Mode: {0} {6} Brightness: {1} Time: {5} Colors: R: {2} G: {3} B: {4} ".format(spa.lightMode, spa.lightBrightnes, spa.lightR, spa.lightG, spa.lightB, spa.lightCycleTime, lightModeText))

        res = "unknown"
        for x,y in spa.LIGHT_MODE_MAP:
            if x == spa.targetlightMode:
               res = y 
               break
        

        print("Target Light Status: Mode: {0} {2} Brightness: {1} ".format(spa.targetlightMode, spa.targetlightBrightnes,  res))  

        print("Spa Time: Y{0:04d} M{1:02d} D{2:02d} {3:02d}:{4:02d} {5}".format(
            spa.year,
            spa.month,
            spa.day,
            spa.time_hour,
            spa.time_minute,
            spa.get_timescale(True)
        ))
        
        mqtt_client.publish(current_temperature_topic, spa.curtemp, retain=True)      
        mqtt_client.publish(temperature_state_topic, spa.get_settemp(), retain=True) 
        mqtt_client.publish(action_topic, spa.get_heatstate(True), retain=True) 
        mqtt_client.publish(pump1_state_topic, spa.pump_status[0], retain=True) 
        mqtt_client.publish(pump2_state_topic, spa.pump_status[1], retain=True) 
        mqtt_client.publish(ciculationpump_state_topic, spa.get_circ_pump(), retain=True) 
        mqtt_client.publish(ciculationmanual_state_topic, spa.get_circ_pump(), retain=True)  
        
        mqtt_client.publish(brightness_state_topic, spa.lightBrightnes, retain=True)  
        mqtt_client.publish(rgb_state_topic, "{},{},{}".format(spa.lightR,spa.lightG,spa.lightB,), retain=True)  
        mqtt_client.publish(effect_state_topic, lightModeText, retain=True)  
        
        if(spa.lightMode > 0):
            mqtt_client.publish(light_state_topic, 1, retain=True)   
        else:
            mqtt_client.publish(light_state_topic, 0, retain=True)   
 
        print()
    if spa.connected:     
        mqtt_client.publish(availability_topic, "online", retain=True) 
    else:
        mqtt_client.publish(availability_topic, "offline", retain=True) 
    
    return lastupd


async def start_mqtt(spa):
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
    payload['unique_id'] = "{}-{}".format(flora_name,"climate")
    payload['value_template'] = "{{value}}"
    payload['current_temperature_topic'] = current_temperature_topic
    payload['current_temperature_template'] = "{{value}}"
    payload['temperature_command_topic'] = temperature_command_topic
    payload['temperature_state_topic'] = temperature_state_topic
    payload['temperature_state_template'] = "{{value}}"
    payload['mode_state_topic'] = mode_state_topic
    payload['action_topic'] = action_topic 
    payload['availability_topic'] = availability_topic
    payload['icon'] = "mdi:hot-tub"
    payload['modes'] = modes
    payload['temp_step'] = "1"
    payload['precision '] = "1"
    payload['tempUnit  '] = "°F"
    payload['min_temp'] = "60"
    payload['max_temp'] = "104"
    payload['device'] = deviceInfo
    payload['expire_after'] = str(int(300 * 1.5))
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)
    
    
    
    discovery_topic = 'homeassistant/switch/{}/{}/config'.format(flora_name.lower(), "Pump1")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "Pump1")
    payload['unique_id'] = "{}-{}".format(flora_name,"Pump1")
    payload['value_template'] = "{{value}}"
    payload['state_topic'] = pump1_state_topic
    payload['state_on'] = 1
    payload['payload_on'] = 1
    payload['state_off'] = 0
    payload['payload_off'] = 0
    payload['command_topic'] = pump1_command_topic
    payload['availability_topic'] = availability_topic
    payload['device'] = deviceInfo
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)

    discovery_topic = 'homeassistant/switch/{}/{}/config'.format(flora_name.lower(), "Pump2")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "Pump2")
    payload['unique_id'] = "{}-{}".format(flora_name,"Pump2")
    payload['value_template'] = "{{value}}"
    payload['state_topic'] = pump2_state_topic
    payload['state_on'] = 1
    payload['payload_on'] = 1
    payload['state_off'] = 0
    payload['payload_off'] = 0
    payload['command_topic'] = pump2_command_topic
    payload['availability_topic'] = availability_topic
    payload['device'] = deviceInfo
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)


    discovery_topic = 'homeassistant/switch/{}/{}/config'.format(flora_name.lower(), "ManualCiculationPump")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "Manual Circ Pump")
    payload['unique_id'] = "{}-{}".format(flora_name,"ManCircPump")
    payload['value_template'] = "{{value}}"
    payload['state_topic'] = ciculationmanual_state_topic
    payload['state_on'] = 1
    payload['payload_on'] = 1
    payload['state_off'] = 0
    payload['payload_off'] = 0
    payload['command_topic'] = ciculationmanual_command_topic
    payload['availability_topic'] = availability_topic
    payload['device'] = deviceInfo
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)

    discovery_topic = 'homeassistant/binary_sensor/{}/{}/config'.format(flora_name.lower(), "CiculationPump")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "Circulation Pump")
    payload['unique_id'] = "{}-{}".format(flora_name,"CircPump")
    payload['value_template'] = "{{value}}"
    payload['state_topic'] = ciculationpump_state_topic
    payload['state_on'] = 1
    payload['payload_on'] = 1
    payload['state_off'] = 0
    payload['payload_off'] = 0
    payload['availability_topic'] = availability_topic
    payload['device'] = deviceInfo
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)


    lightModes = []
    for x,y in spa.LIGHT_MODE_MAP:
        lightModes.append(y)

    discovery_topic = 'homeassistant/light/{}/{}/config'.format(flora_name.lower(), "Lights")
    payload = OrderedDict()
    payload['name'] = "{} {}".format(flora_name, "Lights")
    payload['unique_id'] = "{}-{}".format(flora_name,"Lights")

    payload['brightness_command_topic'] = brightness_command_topic 
    payload['brightness_scale'] = 255
    payload['brightness_state_topic'] = brightness_state_topic
    payload['command_topic'] = light_command_topic
    payload['state_topic'] = light_state_topic 
    payload['rgb_state_topic'] = rgb_state_topic 

    payload['effect_list'] = lightModes
    payload['effect_state_topic'] = effect_state_topic
    payload['effect_command_topic'] = effect_command_topic 
    
    payload['payload_on'] = 1
    payload['payload_off'] = 0
    payload['availability_topic'] = availability_topic
    payload['device'] = deviceInfo
    mqtt_client.publish(discovery_topic, json.dumps(payload), 1, True)


    #Only support heat mode for now
    mqtt_client.publish(mode_state_topic, "heat", retain=True) 

    # Subscribe to MQTT
    mqtt_client.subscribe(temperature_command_topic)
    mqtt_client.subscribe(pump1_command_topic)
    mqtt_client.subscribe(pump2_command_topic)
    mqtt_client.subscribe(ciculationmanual_command_topic)
    mqtt_client.subscribe(brightness_command_topic)
    mqtt_client.subscribe(light_command_topic)
    mqtt_client.subscribe(effect_command_topic)


async def start_app():
    """Test a miniature engine of talking to the spa."""
    global spa

    # Connect to Spa (Serial Device)
    spa = sundanceRS485.SundanceRS485(serial_ip, serial_port)
    await spa.connect()

    # Connect to MQTT
    await start_mqtt(spa)

    asyncio.ensure_future(spa.listen())
    lastupd = 0

    while True:
        lastupd = await read_spa_data(spa, lastupd)


if __name__ == "__main__":
    asyncio.run(start_app())