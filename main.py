import mido


def atom_in_callback(message):
    """
    MIDI input callback
    :param message:
    """
    print(message)


''' Modes
- Native control
- MIDI
'''
nc_mode = mido.Message('note_off', channel=15, note=0, velocity=127)
midi_mode = mido.Message('note_off', channel=15, note=0, velocity=0)

# TODO: Map all buttons messages
'''MAPS
- MIDI mode
- Native control mode
'''

''' States
Note velocity on channel 0 determines state:
- 0 = unlit
- 1 = blink
- 2 = breathe
- 127 = solid

Note velocity on channels 1-3 determines RGB color
'''

out_names = mido.get_output_names()
in_names = mido.get_input_names()

# Filter ATOM ports
for atom_out_name in out_names:
    if 'ATOM' in atom_out_name:
        print("Found ATOM output port: %s" % atom_out_name)
        break
else:
    print("ATOM output port not found!")

for atom_in_name in in_names:
    if 'ATOM' in atom_in_name:
        print("Found ATOM input port: %s" % atom_in_name)
        break
else:
    print("ATOM input port not found!")

atom_out_port = mido.open_output(atom_out_name)
atom_in_port = mido.open_input(atom_in_name, callback=atom_in_callback)

# TODO: Filter AtomCtrl loop ports

# Switch to native mode
atom_out_port.send(nc_mode)

# Blinken light
light = mido.Message('note_on', channel=0, note=36, velocity=1)
atom_out_port.send(light)

# Catch inputs indefinitely
while True:
    pass

# TODO: Cleanup gracefully
atom_out_port.close()
atom_in_port.close()
