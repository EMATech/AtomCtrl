import logging
from signal import signal, SIGINT, SIGTERM

import mido
import mido.backends.rtmidi

# TODO: Write an ATOM library?
''' Modes
Channel 15, note 0, velocity
- 0: MIDI compatible (default, autonomous)
- 127: Native control (advanced, software slave)
'''
ATOM_MODE_MIDI = mido.Message('note_off', channel=15, note=0, velocity=0)
ATOM_MODE_NC = mido.Message('note_off', channel=15, note=0, velocity=127)

# TODO: Map all buttons messages
'''MAPS
- MIDI mode
- Native control mode
    - Pads are velocity sensitive on channel 0.
    Velocity on channels 1,2 and 3 set the respective red, green and blue colors.
    - Rotary CC value is 1 when turned clockwise and 65 counterclockwise
    - Buttons CC value is 127 when depressed and 0 when released
'''
NC_PAD_1 = mido.Message('note_on', channel=9, note=36)
NC_PAD_2 = mido.Message('note_on', channel=9, note=37)
NC_PAD_3 = mido.Message('note_on', channel=9, note=38)
NC_PAD_4 = mido.Message('note_on', channel=9, note=39)

NC_PAD_5 = mido.Message('note_on', channel=9, note=40)
NC_PAD_6 = mido.Message('note_on', channel=9, note=41)
NC_PAD_7 = mido.Message('note_on', channel=9, note=42)
NC_PAD_8 = mido.Message('note_on', channel=9, note=43)

NC_PAD_9 = mido.Message('note_on', channel=9, note=44)
NC_PAD_10 = mido.Message('note_on', channel=9, note=45)
NC_PAD_11 = mido.Message('note_on', channel=9, note=46)
NC_PAD_12 = mido.Message('note_on', channel=9, note=47)

NC_PAD_13 = mido.Message('note_on', channel=9, note=48)
NC_PAD_14 = mido.Message('note_on', channel=9, note=49)
NC_PAD_15 = mido.Message('note_on', channel=9, note=50)
NC_PAD_16 = mido.Message('note_on', channel=9, note=51)

NC_ROT_1 = mido.Message('control_change', channel=0, control=14)
NC_ROT_2 = mido.Message('control_change', channel=0, control=15)
NC_ROT_3 = mido.Message('control_change', channel=0, control=16)
NC_ROT_4 = mido.Message('control_change', channel=0, control=17)

NC_ROT_RIGHT = mido.Message('control_change', channel=0, value=1)
NC_ROT_LEFT = mido.Message('control_change', channel=0, value=65)

NC_MODE_NOTE_REPEAT = mido.Message('control_change', channel=0, control=24, value=127)
NC_MODE_FULL_LEVEL = mido.Message('control_change', channel=0, control=25, value=127)

NC_INST_BANK = mido.Message('control_change', channel=0, control=26, value=127)
NC_INST_PRESET_UP_DOWN = mido.Message('control_change', channel=0, control=27, value=127)
NC_INST_SHOW_HIDE = mido.Message('control_change', channel=0, control=29, value=127)

NC_EVENT_NUDGE = mido.Message('control_change', channel=0, control=30, value=127)
NC_EVENT_EDITOR = mido.Message('control_change', channel=0, control=31, value=127)

NC_SHIFT = mido.Message('control_change', channel=0, control=32, value=127)

NC_SONG_SET_LOOP = mido.Message('control_change', channel=0, control=85, value=127)
NC_SONG_SETUP = mido.Message('control_change', channel=0, control=86, value=127)

NC_NAV_UP = mido.Message('control_change', channel=0, control=87, value=127)
NC_NAV_DOWN = mido.Message('control_change', channel=0, control=89, value=127)
NC_NAV_LEFT = mido.Message('control_change', channel=0, control=90, value=127)
NC_NAV_RIGHT = mido.Message('control_change', channel=0, control=102, value=127)
NC_NAV_SELECT = mido.Message('control_change', channel=0, control=103, value=127)
NC_NAV_ZOOM = mido.Message('control_change', channel=0, control=104, value=127)

NC_TRANS_CLICK = mido.Message('control_change', channel=0, control=105, value=127)
NC_TRANS_RECORD = mido.Message('control_change', channel=0, control=107, value=127)
NC_TRANS_PLAY = mido.Message('control_change', channel=0, control=109, value=127)
NC_TRANS_STOP = mido.Message('control_change', channel=0, control=111, value=127)

''' States
Note velocity on channel 0 determines state:
- 0 = unlit
- 1 = blink
- 2 = breathe
- 127 = solid

Note velocity on channels 1-3 determines RGB color
'''
NC_PAD_STATE_UNLIT = 0
NC_PAD_STATE_BLINK = 1
NC_PAD_STATE_BREATHE = 2
NC_PAD_STATE_SOLID = 127

NC_BUTTON_UNLIT = 0
NC_BUTTON_SOLID = 127

atom_out_port = None
atom_in_port = None
loop_in_port = None
loop_out_port = None

# Log messages to file for further analysis
# logging.basicConfig(filename='AtomCtrl.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# RtMidi is needed for virtual ports
# FIXME: virtual ports are not available in Windows
mido.set_backend(name='mido.backends.rtmidi', load=True)


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
    # FIXME: use virtual ports on supported platforms instead of LoopMIDI
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
    atom_out_port.send(ATOM_MODE_NC)
    # atom_out_port.send(midi_mode)
    # Blinken light
    pad1_breathe = NC_PAD_1.copy(velocity=NC_PAD_STATE_BREATHE)
    atom_out_port.send(pad1_breathe)
    # In color!
    rgb = [127, 0, 30]
    atom_out_port.send(mido.Message('note_on', channel=1, note=36, velocity=rgb[0]))
    atom_out_port.send(mido.Message('note_on', channel=2, note=36, velocity=rgb[1]))
    atom_out_port.send(mido.Message('note_on', channel=3, note=36, velocity=rgb[2]))

    # Button test
    atom_out_port.send(NC_TRANS_STOP.copy(value=NC_BUTTON_SOLID))


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

            # React to touch
            reply = None
            if atom_message.type == 'note_on':
                reply = atom_message.copy(velocity=127)
            if atom_message.type == 'note_off':
                reply = mido.Message(type='note_on', channel=atom_message.channel, note=atom_message.note, velocity=0)
            if atom_message.type == 'control_change':
                reply = atom_message.copy(value=atom_message.value)

            atom_out_port.send(reply)


main()
