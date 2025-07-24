
#!/usr/bwain/env python3
import sys

from pathlib import Path

import numpy as np

from matplotlib.figure import Figure

import panel as pn

import rpyc

pn.extension(sizing_mode="stretch_width")

class CurieWebPanel:
    def __init__(self):
        self.conn = rpyc.connect('localhost', 37000)
    
        ACCENT="goldenrod"
        LOGO="assets/pi-radio.png"
        data = np.random.normal(1, 1, size=100)
        fig = Figure(figsize=(8, 4))
        ax = fig.subplots()
        ax.hist(data, bins=20, color=ACCENT)

        filter_options = [
            'bypass', '36MHz', '72MHz', '144MHz',
            '288MHz', '432MHz', '576MHz', '720MHz'
        ]

  
        low_LO = pn.widgets.EditableFloatSlider(
            value=self.srv.get_low_LO()/1e9,
            step=0.1,
            start=0.4,
            end=4.4,
            fixed_start= 0.4,
            fixed_end= 1.8,
            format="0.000000",
            disabled=False,
            name="Low LO Frequency (GHz)")

        high_LO = pn.widgets.EditableFloatSlider(
            value=self.srv.get_high_LO()/1e9,
            step=0.1,
            start=6.0,
            end=22.8,
            fixed_start= 6.0,
            fixed_end= 22.8,
            format="0.000000",
            disabled=False,
            name="High LO Frequency (GHz)")

        RX0_gain = pn.widgets.EditableFloatSlider(
            value=self.srv.get_gain('rx', 0),
            step=0.1,
            start=0,
            end=60.0,
            fixed_start= 0,
            fixed_end= 60.0,
            format="00.0",
            disabled=False,
            name="RX0 Gain (dB)")

        RX0_filter = pn.widgets.Select(
            value=self.srv.get_filter('rx', 0),
            name="RX0 Filter",
            options=filter_options)
        
        RX1_gain = pn.widgets.EditableFloatSlider(
            value=self.srv.get_gain('rx', 1),
            step=0.1,
            start=0,
            end=60.0,
            fixed_start= 0,
            fixed_end= 60.0,
            format="00.0",
            disabled=False,
            name="RX1 Gain (dB)")
        
        RX1_filter = pn.widgets.Select(
            value=self.srv.get_filter('rx', 1),
            name="RX1 Filter",
            options=filter_options)
        
        TX0_gain = pn.widgets.EditableFloatSlider(
            value=self.srv.get_gain('tx', 0),
            step=0.1,
            start=0,
            end=60.0,
            fixed_start= 0,
            fixed_end= 60.0,
            format="00.0",
            disabled=False,
            name="TX0 Gain (dB)")

        TX0_filter = pn.widgets.Select(
            value=self.srv.get_filter('tx', 0),
            name="TX0 Filter",
            options=filter_options)
        
        TX1_gain = pn.widgets.EditableFloatSlider(
            value=self.srv.get_gain('tx', 1),
            step=0.1,
            start=0,
            end=60.0,
            fixed_start= 0,
            fixed_end= 60,
            format="00.0",
            disabled=False,
            name="TX1 Gain (dB)")
        
        TX1_filter = pn.widgets.Select(
            value=self.srv.get_filter('tx', 1),
            name="TX1 Filter",
            options=filter_options)
        
        TX0_I_bias = pn.widgets.EditableFloatSlider(
            value=self.srv.get_mixer_bias(0, "I"),
            step=0.001,
            start=-0.4,
            end=0.4,
            fixed_start= -0.4,
            fixed_end= 0.4,
            format="0.000",
            disabled=False,
            name="TX0 I bias (V)")
        
        TX0_Q_bias = pn.widgets.EditableFloatSlider(
            value=self.srv.get_mixer_bias(0, "Q"),
            step=0.001,
            start=-0.4,
            end=0.4,
            fixed_start= -0.4,
            fixed_end= 0.4,
            format="0.000",
            disabled=False,
            name="TX0 Q bias (V)")
        
        TX1_I_bias = pn.widgets.EditableFloatSlider(
            value=self.srv.get_mixer_bias(1, "I"),
            step=0.001,
            start=-0.4,
            end=0.4,
            fixed_start= -0.4,
            fixed_end= 0.4,
            format="0.000",
            disabled=False,
            name="TX1 I bias (V)")
        
        TX1_Q_bias = pn.widgets.EditableFloatSlider(
            value=self.srv.get_mixer_bias(1, "Q"),
            step=0.001,
            start=-0.4,
            end=0.4,
            fixed_start= -0.4,
            fixed_end= 0.4,
            format="0.000",
            disabled=False,
            name="TX1 Q bias (V)")

        GPIO2 = pn.widgets.Checkbox(name="Use Internal Reference", value=self.srv.get_gpio(2))
        GPIO3 = pn.widgets.Checkbox(name="Use Internal Reference for Low Side", value=self.srv.get_gpio(3))
        GPIO6 = pn.widgets.Checkbox(name="Disable Input 20dB Attenuator", value=self.srv.get_gpio(6))

        reset_lmx = pn.widgets.Button(name="Reset LMX", button_type="primary")
        
        pn.bind(self.update_freq, lo="lo", freq=low_LO, watch=True)
        pn.bind(self.update_freq, lo="hi", freq=high_LO, watch=True)

        pn.bind(self.update_gain, channel="rx0", gain=RX0_gain, watch=True)
        pn.bind(self.update_gain, channel="rx1", gain=RX1_gain, watch=True)
        pn.bind(self.update_gain, channel="tx0", gain=TX0_gain, watch=True)
        pn.bind(self.update_gain, channel="tx1", gain=TX1_gain, watch=True)

        pn.bind(self.update_bias, channel=0, iq="I", v=TX0_I_bias, watch=True)
        pn.bind(self.update_bias, channel=0, iq="Q", v=TX0_Q_bias, watch=True)
        pn.bind(self.update_bias, channel=1, iq="I", v=TX1_I_bias, watch=True)
        pn.bind(self.update_bias, channel=1, iq="Q", v=TX1_Q_bias, watch=True)

        pn.bind(self.update_filter, channel='rx0', v=RX0_filter, watch=True)
        pn.bind(self.update_filter, channel='rx1', v=RX1_filter, watch=True)
        pn.bind(self.update_filter, channel='tx0', v=TX0_filter, watch=True)
        pn.bind(self.update_filter, channel='tx1', v=TX1_filter, watch=True)
        
        pn.bind(self.update_gpio, channel=2, v=GPIO2, watch=True)
        pn.bind(self.update_gpio, channel=3, v=GPIO3, watch=True)
        pn.bind(self.update_gpio, channel=6, v=GPIO6, watch=True)

        pn.bind(self.reset_lmx)
        
        links = pn.pane.Markdown("""
        - [Help](https://www.pi-rad.io/home/getting-started)
        """)
        
        component = pn.Accordion(
            ( "Frequency", pn.Column(low_LO, high_LO) ),
            ( "Filters", pn.Column(RX0_filter, RX1_filter, TX0_filter, TX1_filter) ),
            ( "Gain", pn.Column(RX0_gain, RX1_gain, TX0_gain, TX1_gain) ),
            ( "LO Suppression", pn.Column(TX0_I_bias, TX0_Q_bias, TX1_I_bias, TX1_Q_bias) ),
            #( "Power", pn.Column("Cliff Hanger") ),
            ( "Control", pn.Column(GPIO2, GPIO3, GPIO6, reset_lmx) ),
            ( "Information" , pn.Column(links) ),
        )


        sidebar = pn.pane.image.PNG(LOGO, link_url="https://pi-rad.io/")


        self.t = pn.template.FastListTemplate(
            title="Curie", sidebar=[sidebar], main=[component], accent=ACCENT
        ).servable()

    @property
    def srv(self):
        try:
            self.conn.root.keep_alive()
        except EOFError:
            self.conn = rpyc.connect('localhost', 37000)
            return self.srv

        return self.conn.root
        
    def update_freq(self, lo, freq):
            print(f"Updating frequency for {lo} to {freq}...")
            if lo == "lo":
                self.srv.set_low_LO(freq * 1e9)
            elif lo == "hi":
                self.srv.set_high_LO(freq * 1e9)
        
    
    def update_gain(self, channel, gain):
        print(f"Updating gain for {channel} to {gain}...")
        self.srv.set_gain(channel[:2], int(channel[2]), gain)

    def update_filter(self, channel, v):
        print(f"Updating filter for {channel} to {v}...")
        self.srv.set_filter(channel[:2], int(channel[2]), v)
        
    def update_bias(self, channel, iq, v):
        print(f"Updating bias for TX{channel} {iq} to {v}...")
        self.srv.set_mixer_bias(channel, iq, v)

    def update_gpio(self, channel, v):
        print(f"Updating GPIO {channel} to {v}...")
        self.srv.set_gpio(channel, v)

    def reset_lmx(self):
        self.srv.reset_lmx()

        
if __name__ == '__main__':
    p = CurieWebPanel()
    pn.serve(p.t, show=False, port=5006, static_dirs={'assets': f'{Path(__file__).parent/"assets"}'})
