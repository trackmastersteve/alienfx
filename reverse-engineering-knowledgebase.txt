Reverse-Engineering-Knowledgebase:
##################################

Zone addresses:
+++++++++++++++

NOTICE:
It seems that the alienfx-controllers are using doubles for base zone adresses.
Keep an eye on the binary-representation of the values in the following table:
It looks like, the used one bit per zone, so that we are able to set multiple zones by adding their base codes (as for keyboard 0xF)

There are a lot more zone- and command-codes which are doing things we dont know about (yet),
like -for example- setting multiple zones to different colors and such stuff.
i think that these are used (or can be used) by some games.

Zone addresses seem to follow the following pattern:

HEX    | Binary          | Zone on AW17R4
=========================================================================================
0x0001 | 000000000000001 | Keyboard right
0x0002 | 000000000000010 | Keyboard middle-right
0x0004 | 000000000000100 | Keyboard middle-left
0x0008 | 000000000001000 | Keyboard left
0x000F | 000000000001111 | Keyboard: all fields <= interesting: 0x1 + 0x2 + 0x4 + 0x8 = 0xF
0x0010 | 000000000010000 | unknown/unused
0x0020 | 000000000100000 | Alienhead (Display outside)
0x0040 | 000000001000000 | Alienware-Logo
0x0080 | 000000010000000 | Touchpad
0x0100 | 000000100000000 | Power button
0x0200 | 000001000000000 | unknown/unused
0x0400 | 000010000000000 | bottom (speaker) left
0x0800 | 000100000000000 | bottom (speaker) right
0x1000 | 001000000000000 | top (display) left
0x2000 | 010000000000000 | top (display) right
0x4000 | 100000000000000 | keyboard macrokey-bar (left)


States
+++++++
States: Some zone seem to be only be accessed in some states.
Caution: different settings for a zone in different states may interfere, so that flashing can happen...