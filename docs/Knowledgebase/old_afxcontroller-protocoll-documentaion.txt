
AlienFX device-specific protocol
================================

Terminology
-----------

 - **Device**:
    An AlienFX USB device.

 - **Zone**:
    A (or a set of) LED which share a sequence.

 - **Action**:
    The lighting behavior for zones. This includes Morph, Pulse, and Color.

 - **Morph**:
 - **Pulse**:
 - **Color**:

 - **Sequence**:
    An ordered list of actions.

 - **Theme**:
    A set of sequences and corresponding zones.


Device Configuration
--------------------

 - use configuration 1
 - occasionally, kernel drivers need to be disabled


URB Setup
---------

### Sending

 - bmRequestType = 0x21

        0... .... : Host to Device
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface

 - bRequest = 9 (Constant)
 - wValue = 0x0202 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 9 (Constant. Smaller message must be padded with 0)


### Receiving

 - bmRequestType = 0xa1  

        1... .... : Device to Host
        .01. .... : Request Type = Class
        ...0 0001 : Recipient = Interface

 - bRequest = 9 (Constant)
 - wValue = 0x0202 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 9 (Constant)


### (Unkown)

 - AFAIK, not sending this packet does no harm.
 - bmRequestType = 0x21
 - bRequest = 10
 - wValue = 0 (Constant)
 - wIndex = 0 (Constant)
 - wLength = 0 (Constant)


Commands
--------

### 0x01: Morph ###

    02:01:nn:00:zz:zz:rg:bR:GB

    n : Sequence ID
    z : Zone
    r : Red 1
    g : Green 1
    b : Blue 1
    R : Red 2
    G : Green 2
    B : Blue 2

 - The color changes from `rgb` to `RGB`


### 0x02: Pulse ###

    02:02:nn:00:zz:zz:rg:b0:

    n : Sequence ID
    z : Zone
    r : Red
    g : Green
    b : Blue


### 0x03: Color ###

    02:03:nn:00:zz:zz:rg:b0:
    
    n : Sequence ID
    z : Zone
    r : Red
    g : Green
    b : Blue


### 0x04: Loop

    02:04:  :  :  :  :  :  :

 - Without this, LEDs will go off after walking through the user-specified
   color sequence.
 - (TODO: how does this know which sequence is the target? The last one
   mentioned? What happens if sequences are interleaved?)


### 0x05: Execute

    02:05:  :  :  :  :  :  :

 - This must be called at the end.
 - Start executing color sequences.


### 0x06: Update Status code

    02:06:  :  :  :  :  :  :

 - The status code has to be retrieved manually.
   (See URB-Receiving)


### 0x07: Reset?

    02:07:tt:  :  :  :  :  :
    
    t : type

 - This takes some time, and you should wait until the operation ends.
   Premature commands might fail.


### 0x08: Save-To

    02:08:ss:  :  :  :  :  :
    
    s : slot

 - Save the next command to the specified slot.
 - Must be followed by an Action or Loop
 - (TODO: better name?)

### 0x09: Write Slots

    02:09:  :  :  :  :  :  :

 - Save slots permanently.
 - If this command is not called, data slots will be lost on reboot.
   (TODO: direct experiment)
 - (TODO: better name)


### 0x0E: Tempo

    02:0E:tt:tt:  :  :  :  :

    t: Tempo

 - AlienFX sets this value between 00:1e ~ 03:ae
 - Lower is faster


### 0x1C: Dim

    02:1C:oo:bb:  :  :  :  :

    o: 32 (Enable)
       64 (Disable)
    b: 01 (Always)
       00 (in Battery Mode Only)


### 0x1D: (Unknown)

    02:1d:03:  :  :  :  :  :   (on apply)
    02:1d:81:  :  :  :  :  :   (on go-dark)


Contants
--------

### Reset

 - (TODO: tbh, this section, entirely)
 - 00: reset keyboard
 - 01: reset keyboard
 - 02: (TODO)
 - 03: reset all
       this also stops the execution of sequences
 - 04: (TODO)


### Slots

 - 01: Initial State
 - 02: Plugged in - Sleep
   + Only the power-button works in this mode?
 - 05: Plugged in - Normal
 - 06: Plugged in - Charging
 - 07: On Battery - Sleep
 - 08: On Battery - Normal
 - 09: On Battery - Low
 - (TODO: better title)

