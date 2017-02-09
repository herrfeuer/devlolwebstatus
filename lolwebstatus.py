#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler,HTTPServer

import paho.mqtt.client as paho

import argparse


spaceOpen = False
brokerHost = "mqtt.devlol.org"
mqttTopic = "devlol/h19/door/lockstatus"


class MyHandler(BaseHTTPRequestHandler):

     def do_HEAD(client):
        client.send_response(200)
        client.send_header("Content-type", "text/html")
        client.end_headers()

     def do_GET(self):
        global spaceOpen
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            if spaceOpen:
                print("return OPEN")
                #self.wfile.write(load('open.html'))
                try:
                    self.wfile.write(load_binary('open.jpg'))
                except BrokenPipeError:
                    pass
            else:
                print("return CLOSED")
                #self.wfile.write(load('closed.html'))
                try:
                    self.wfile.write(load_binary('closed.jpg'))
                except BrokenPipeError:
                    pass


def load_binary(file):
    with open(file, 'rb') as file:
        return file.read()

def load(file):
    with open(file, 'r') as file:
        return encode(str(file.read()))

def encode(file):
    return bytes(file, 'UTF-8')



def on_message(client, userdata, msg):
    global spaceOpen
    payload = msg.payload.decode("utf-8")
    print(payload)
    """ Callback for mqtt message."""
    if mqttTopic == msg.topic:
        if payload == "UNLOCKED":
            spaceOpen = True
            print("UNLOCKED")
        elif payload == "LOCKED":
            spaceOpen = False
            print("LOCKED")


def on_disconnect(client, userdata, foo):
    connected = False
    while not connected:
        try:
            client.reconnect()
            connected = True
            # resubscribe to the topics
            client.subscribe(mqttTopic)
        except:
            print("Failed to reconnect...")
            time.sleep(1)



def run(server_class=HTTPServer,
        handler_class=MyHandler):

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", default=8321, type=int)
    args = parser.parse_args()
    port = args.p

    ## setup MQTT client
    client = paho.Client()
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        client.connect(brokerHost)
    except:
        print("failed to connect")
        on_disconnect(client, None, None)

    client.subscribe(mqttTopic)


    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    while True:
        httpd.handle_request()
        client.loop()

if __name__ == "__main__":
    run()
