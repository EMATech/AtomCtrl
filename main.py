import logging
from signal import signal, SIGINT, SIGTERM

import mido.backends.rtmidi

# Log messages to file for further analysis
# logging.basicConfig(filename='AtomCtrl.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# RtMidi is needed for virtual ports
# FIXME: virtual ports are not available in Windows
mido.set_backend(name='mido.backends.rtmidi', load=True)

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


def init():
    global atom_out_port, atom_in_port, loop_in_port, loop_out_port

    out_names = mido.get_output_names()
    in_names = mido.get_input_names()

    found = 0
    # Filter ATOM ports
    for atom_out_name in out_names:
        if 'ATOM' in atom_out_name:
            logging.info("Found ATOM output port: %s" % atom_out_name)
            found += 1
            break
    else:
        logging.warning("ATOM output port not found!")
    for atom_in_name in in_names:
        if 'ATOM' in atom_in_name:
            logging.info("Found ATOM input port: %s" % atom_in_name)
            found += 1
            break
    else:
        logging.warning("ATOM input port not found!")
    # Filter loop ports
    for loop_out_name in out_names:
        if 'from ATOM' in loop_out_name:
            logging.info("Found AtomCtrl loop output port: %s" % loop_out_name)
            found += 1
            break
    else:
        logging.warning("AtomCtrl loop output port not found!")
    for loop_in_name in in_names:
        if 'to ATOM' in loop_in_name:
            logging.info("Found AtomCtrl loop input port: %s" % loop_in_name)
            found += 1
            break
    else:
        logging.warning("AtomCtrl loop input port not found!")
    if found == 4:
        atom_out_port = mido.open_output(atom_out_name)
        atom_in_port = mido.open_input(atom_in_name)
        loop_in_port = mido.open_input(loop_in_name)
        loop_out_port = mido.open_output(loop_out_name)
    else:
        logging.error("Required MIDI ports not found!")
        exit()
    # Switch to native mode
    atom_out_port.send(nc_mode)
    # atom_out_port.send(midi_mode)
    # Blinken light
    atom_out_port.send(mido.Message('note_on', channel=0, note=36, velocity=2))
    # In color!
    rgb = [127, 0, 30]
    atom_out_port.send(mido.Message('note_on', channel=1, note=36, velocity=rgb[0]))
    atom_out_port.send(mido.Message('note_on', channel=2, note=36, velocity=rgb[1]))
    atom_out_port.send(mido.Message('note_on', channel=3, note=36, velocity=rgb[2]))


def cleanup(signal_received, frame):
    # Cleanup gracefully
    logging.debug("Interrupt received. Closing ports now!")
    atom_in_port.close()
    loop_in_port.close()
    atom_out_port.close()
    loop_out_port.close()
    exit(0)


def main():
    signal(SIGINT, cleanup)
    signal(SIGTERM, cleanup)

    init()

    while True:
        # Forward messages to/from ATOM from/to AtomCtrl
        for loop_message in loop_in_port.iter_pending():
            logging.debug("AtomCtrl input: %s" % loop_message)
            atom_out_port.send(loop_message)
        for atom_message in atom_in_port.iter_pending():
            logging.debug("ATOM input: %s" % atom_message)
            loop_out_port.send(atom_message)

        # TODO: Handle inputs


main()
