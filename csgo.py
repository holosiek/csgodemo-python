import struct
#-------------------------------------------
# Demo variables
DEMO_HEADER_ID   = b'HL2DEMO\x00'
DEMO_PROTOCOL    = 4

# Flags
FDEMO_NORMAL = 0
FDEMO_USE_ORIGIN2 = 1
FDEMO_USE_ANGLES2 = 2
FDEMO_NOINTERP = 4

# CSGO consts
MAX_SPLITSCREEN_CLIENTS = 2

NET_MAX_PAYLOAD = 252140

# Sizes depends on C++
INT_SIZE = 4
FLOAT_SIZE = 4
DEMOCMDINFO_SIZE = 152
DEMO_HEADER_SIZE = 1072

dem_signon       = b'\x01'
dem_packet       = b'\x02'
dem_synctick     = b'\x03'
dem_consolecmd   = b'\x04'
dem_usercmd      = b'\x05'
dem_datatables   = b'\x06'
dem_stop         = b'\x07'
dem_customdata   = b'\x08'
dem_stringtables = b'\x09'
dem_lastcmd      = b'\x09'
#-------------------------------------------
def b2int(x):
    return int.from_bytes(x, byteorder="little")
def b2float(x):
    return struct.unpack('f', x)[0]
#-------------------------------------------
class Vector:
    x, y, z = 0, 0, 0
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
class QAngle:
    x, y, z = 0, 0, 0
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = x, y, z
#-------------------------------------------
# Demo header structure
class struct_demoheader:
    demofilestamp   = ""       # Should be HL2DEMO
    demoprotocol    = 0        # Should be DEMO_PROTOCOL
    networkprotocol = 0        # Should be PROTOCOL_VERSION
    servername      = ""       # Name of server
    clientname      = ""       # Name of client who recorded the game
    mapname         = ""       # Name of map
    gamedirectory   = ""       # Name of game directory (com_gamedir)
    playback_time   = 0.0      # Time of track
    playback_ticks  = 0        # Number of ticks in track
    playback_frames = 0        # Number of frames in track
    signonlength    = 0        # Length of sigondata in bytes
    
# Split structure
class struct_split:
    flags = FDEMO_NORMAL
    viewOrigin = Vector()
    viewAngles = QAngle()
    localViewAngles = QAngle()
    viewOrigin2 = Vector()
    viewAngles2 = QAngle()
    localViewAngles2 = QAngle()
    #---------------------------------------
    def GetViewOrigin(self):
        if(self.flags & FDEMO_USE_ORIGIN2):
            return self.viewOrigin2
        return self.viewOrigin
    def GetViewAngles(self):
        if(self.flags & FDEMO_USE_ANGLES2):
            return self.viewAngles2
        return self.viewAngles
    def GetLocalViewAngles(self):
        if(self.flags & FDEMO_USE_ANGLES2):
            return self.localViewAngles2
        return self.localViewAngles
    # ---------------------------------------
    def reset(self):
        self.flags = 0
        self.viewOrigin2 = self.viewOrigin
        self.viewAngles2 = self.viewAngles
        self.localViewAngles2 = self.localViewAngles
        
# Demo command information structure
class struct_democmdinfo:
    u = [struct_split()]*MAX_SPLITSCREEN_CLIENTS
    def ReadCmdInfo(self, text):
        textPos = 0
        for i in self.u:
            # flags
            i.flags = b2int(text[textPos:textPos+INT_SIZE])
            textPos += INT_SIZE
            
            # viewOrigin
            i.viewOrigin.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewOrigin.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewOrigin.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            
            # viewAngles
            i.viewAngles.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewAngles.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewAngles.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            
            # localViewAngles
            i.localViewAngles.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.localViewAngles.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.localViewAngles.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE

            # viewOrigin2
            i.viewOrigin2.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewOrigin2.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewOrigin2.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE

            # viewAngles2
            i.viewAngles2.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewAngles2.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.viewAngles2.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE

            # localViewAngles2
            i.localViewAngles2.x = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.localViewAngles2.y = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
            i.localViewAngles2.z = b2float(text[textPos:textPos + FLOAT_SIZE])
            textPos += FLOAT_SIZE
    def reset(self):
        for i in self.u:
            i.reset()