#!/usr/bin/env python3
import click
import rpyc
import os
import time
import threading

from pathlib import Path
from json import JSONEncoder

from curiectl import Curie
from flask import Flask, request

curie = Curie()

flask_app = Flask("curiectld")

@flask_app.route("/")
def hello():
    return "Rest API"

@flask_app.route("/low_lo", methods=[ "GET", "POST", "PUT" ])
def flask_low_lo():
    if 'freq' in request.args:
        try:
            new_freq = float(request.args.get('freq'))
            
            curie.set_low_LO(new_freq)
        except:
            return f"Failed to set new frequency {e}"

    d = { 'frequency': curie.get_low_LO() }
        
    return JSONEncoder().encode(d)

@flask_app.route("/high_lo", methods=[ "GET", "POST", "PUT" ])
def flask_high_lo():
    if 'freq' in request.args:
        try:
            new_freq = float(request.args.get('freq'))
            
            curie.set_high_LO(new_freq)
        except:
            return f"Failed to set new frequency {e}"
        
    d = { 'frequency': curie.get_high_LO() }
        
    return JSONEncoder().encode(d)


@flask_app.route("/bias", methods=[ "GET",  "POST", "PUT" ])
def flask_bias():
    if 'chan' in request.args and 'iq' in request.args and 'v' in request.args:
        try:
            chan = int(request.args.get('chan'))
            iq = request.args.get('iq')
            v = float(request.args.get('v'))
            
            curie.set_mixer_bias(chan, iq, v)
        except Exception as e:
            return f"Failed to set new bias {e}"
    elif 'chan' in request.args or 'iq' in request.args or 'v' in request.args:
        return "bias requires 3 argumens: chan, iq and v"
        
    d = { 0:
          {
              'I': curie.get_mixer_bias(0, 'I'),
              'Q': curie.get_mixer_bias(0, 'Q'),
          },
          1:
          {
              'I': curie.get_mixer_bias(1, 'I'),
              'Q': curie.get_mixer_bias(1, 'Q'),
          },
         }
    
    return JSONEncoder().encode(d)

@flask_app.route("/gain", methods=[ "GET",  "POST", "PUT" ])
def flask_gain():
    if 'trx' in request.args and 'chan' in request.args and 'v' in request.args:
        try:
            trx = request.args.get('trx')
            chan = int(request.args.get('chan'))
            v = float(request.args.get('v'))
            
            curie.set_gain(trx, chan, v)
        except Exception as e:
            return f"Failed to set new gain {e}"
    elif 'trx' in request.args or 'chan' in request.args or 'v' in request.args:
        return f"gain requires 3 argumens: trx, chan and v"

        
    d = { 'tx':
          {
              0: curie.get_gain('tx', 0),
              1: curie.get_gain('tx', 1),
          },
          'rx':
          {
              0: curie.get_gain('rx', 0),
              1: curie.get_gain('rx', 1),
          }
         }
          
    return JSONEncoder().encode(d)


def launch_flask():
    flask_app.run(host="0.0.0.0", port=5111)
    

@rpyc.service
class CurieCtlService(rpyc.Service):    
    def on_connect(self, conn):
        print("Client connected")
        
    def on_disconnect(self, conn):
        print("Client disconnected")

    @rpyc.exposed
    def keep_alive(self) -> None:
        pass

    @rpyc.exposed
    def get_high_LO(self):
        return curie.get_high_LO()

    @rpyc.exposed
    def get_low_LO(self):
        return curie.get_low_LO()
    
    @rpyc.exposed
    def set_high_LO(self, f):
        print(f"Setting high LO to {f}")
        curie.set_high_LO(f)

    @rpyc.exposed
    def set_low_LO(self, f):
        print(f"Setting low LO to {f}")
        curie.set_low_LO(f)

    @rpyc.exposed
    def get_mixer_bias(self, chan, iq):
        return curie.get_mixer_bias(chan, iq)
        
    @rpyc.exposed
    def set_mixer_bias(self, chan, iq, v):
        print(f"Setting chan {chan} {iq} bias to {v}")
        curie.set_mixer_bias(chan, iq, v)

    @rpyc.exposed
    def get_gain(self, trx, chan):
        return curie.get_gain(trx, chan)
        
    @rpyc.exposed
    def set_gain(self, trx, chan, v):
        print(f"Setting {trx}{chan} gain to {v}")
        curie.set_gain(trx, chan, v)

    @rpyc.exposed
    def get_gpio(self, chan):
        print(f"Get GPIO {chan} {curie.get_gpio(chan)}")
        return curie.get_gpio(chan)
        
    @rpyc.exposed
    def set_gpio(self, chan, v):
        print(f"Setting GPIO {chan} to {v}")
        curie.set_gpio(chan, v)

    @rpyc.exposed
    def reset_lmx(self, chan, v):
        print(f"Resetting LMX(s)")
        curie.reset_lmx()
        
        
        
@click.command()
def curiectld():
    print("Launching control daemon")

    if not Path("/etc/curie.conf").exists():
        print("Creating new configuration")
        CurieConfig().dumps()
    
    pid = os.fork()

    if pid == 0:
        time.sleep(5)
        os.system(f"python {Path(__file__).parent / 'ctrl_panel.py'}")
        exit()

    flask_thread = threading.Thread(target=launch_flask)
    flask_thread.daemon=True
    flask_thread.start()
    
    t = rpyc.utils.server.ThreadedServer(CurieCtlService, port=37000)
    t.start()


if __name__ == '__main__':
    curiectld()
