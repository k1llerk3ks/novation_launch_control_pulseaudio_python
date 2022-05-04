# Control PulseAudio with Novation Launch-Control MIDI Device by Python Script

This Script let's you control Pulseaudio sinks and input streams.

Feel free to Fork and Pull-Request your enhancements to this file!

Hint: This Script does *not* work right out of the box. you need to change your tuple lines to your need to make this work.

---
the script is ran by `launch_control(tuple_list)`
Each tuple defines one knob.

This is the structure of a tuple:

### (button_id, type, target, notification_title)

## button_id
the id of the knob you want to control something

## type
You can either control pulseaudio sinks or input_sinks, e.g. vlc media player sound or Discord or Firefox...
this is defined by the `type`:

normal sink = "volume"
input_sink = "input_volume"

## target

### if type == "volume":
  look at the pulseaudio input_volume streams by typing:
  
  `pactl list sinks`
  
  get `device.description` of your output-device - this is your `target`-String
  (you might need to define yourself an output, e.g. by addin a line like this to `~/.config/pulse/default.pa`)
  
      load-module module-remap-sink sink_name="Focusrite\ Solo\ Front" sink_properties="device.description='Focusrite\ Solo\ Front' " master=0 channels=2 master_channel_map=front-left,front-right channel_map=front-left,front-right remix=no
      
### if type == "input_volume"
  look at the pulseaudio input_volume streams by typing:
  
  `pactl list sink-inputs`
  
  get `application.process.binary` of your input_stream - this is your `target`-String
  
## notification_title

The volume of your stream gets printed out to your notifications. `notification_title` defines the Title of this notification.

---

