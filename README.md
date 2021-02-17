# AtomCtrl

Presonus ATOM Controller

## LoopMIDI

Create "from ATOM" and "to ATOM" ports Configure your DAW to use these ports rather than the ATOM port

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