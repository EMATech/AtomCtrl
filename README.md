AtomCtrl
========

An experiment with the Presonus ATOM Controller

## LoopMIDI setup (Microsoft Windows)

- Create "from ATOM" and "to ATOM" ports
- Configure the DAW to use these ports rather than the ATOM port

```
 +------+                +----------+                +-----+
 | ATOM | <- USB MIDI -> | AtomCtrl | <- loopMIDI -> | DAW |
 +------+                +----------+                +-----+
```

### DAW ports

```
+----------+                  +-----+
|          | -- from ATOM --> |     |
| AtomCtrl |                  | DAW |
|          | <-- to ATOM ---- |     |
+----------+                  +-----+
```