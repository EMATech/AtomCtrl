import mido

''' Modes
Native control
MIDI
'''
nc_mode = mido.Message('note_off', channel=15, note=0, velocity=127)
midi_mode = mido.Message('note_off', channel=15, note=0, velocity=0)

''' States
Note velocity on channel 0 determines state:
- 0 = unlit
- 1 = blink
- 2 = breathe
- 127 = solid

Note velocity on channels 1-3 determines RGB color
'''

out_names = mido.get_output_names()

# Filter ATOM output port
for out_name in out_names:
    if 'ATOM' in out_name:
        break

port = mido.open_output(out_name)

port.send(nc_mode)