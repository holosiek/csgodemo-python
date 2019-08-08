import struct
import netmessages_public_pb2 as protonet
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

# ENUMS
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

up_enterPVS    = 0
up_leavePVS    = 1
up_deltaEnt    = 2
up_preserveEnt = 3
up_finished    = 4
up_failed      = 5

fhdr_zero      = 0
fhdr_leavePVS  = 1
fhdr_delete    = 2
fhdr_enterPVS  = 4
#-------------------------------------------
def b2int(x):
    return int.from_bytes(x, byteorder="little")
def b2float(x):
    return struct.unpack('f', x)[0]
def b2str(x):
    return x.decode("utf-8")

# Remove \x00 bytes in string
def readString_raw(a_str):
    return a_str.split(b'\0',1)[0]
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

# Flattened prop entry
class flattenedPropEntry:
    prop = protonet.CSVCMsg_SendTable().sendprop_t()
    arrayElementProp = protonet.CSVCMsg_SendTable().sendprop_t()

    def __init__(self, a_prop, a_arrayProp):
        self.prop             = protonet.CSVCMsg_SendTable().sendprop_t().ParseFromString(a_prop)
        self.arrayElementProp = protonet.CSVCMsg_SendTable().sendprop_t().ParseFromString(a_arrayProp)

# Server class information
class serverClass_t:
    classID = 0
    name = ""
    DTname = ""
    dataTable = 0
    flattenedProps = []

# Player information
class player_info_t:
    version         = 0
    xuid            = 0
    name            = ""
    userID          = 0
    guid            = ""
    friendsID       = 0
    friendsName     = ""
    fakeplayer      = False
    ishltv          = False
    customFiles     = []
    filesDownloaded = 0
    entityID        = 0

    def parse(self, a_data, a_entry):
        parsed = struct.unpack("2Q128si33sI128s2?3LBi", a_data)
        self.version = parsed[0]
        self.xuid = parsed[1]
        self.name = b2str(readString_raw(parsed[2]))
        self.userID = parsed[3]
        self.guid = b2str(readString_raw(parsed[4]))
        self.friendsID = parsed[5]
        self.friendsName = b2str(readString_raw(parsed[6]))
        self.fakeplayer = parsed[7]
        self.ishltv = parsed[8]
        self.customFiles = parsed[9]
        self.filesDownloaded = [parsed[10], parsed[11], parsed[12], parsed[13]]
        self.entityID = a_entry

# Buffer reader
class CBitRead:
    data      = ""
    dataBytes = 0
    dataPart  = ""

    posByte   = 0
    bitsFree  = 0
    overflow  = False
    # ---------------------------------------------------------
    # Grab another part of data to buffer
    def grabNext4Bytes(self):
        if(self.posByte >= len(self.data)):
            self.bitsFree = 1
            self.dataPart = 0
            self.overflow = True
        else:
            self.dataPart = self.data[self.posByte] + (self.data[self.posByte + 1] << 8) + (self.data[self.posByte + 2] << 16) + (self.data[self.posByte + 3] << 24)
            self.posByte += 4

    # Add 32 bits free to use and grab new data to buffer
    def fetchNext(self):
        self.bitsFree = 32
        self.grabNext4Bytes()
    # ---------------------------------------------------------
    # Read VAR
    def readUBitVar(self):
        ret = self.readUBitLong(6)
        if(ret & 48 == 16):
            ret = (ret & 15) |  (self.readUBitLong(4) << 4)
        elif(ret & 48 == 32):
            ret = (ret & 15) |  (self.readUBitLong(8) << 4)
        elif (ret & 48 == 48):
            ret = (ret & 15) | (self.readUBitLong(28) << 4)
        return ret

    # Read unsigned n-bits
    def readUBitLong(self, a_bits):
        if(self.bitsFree >= a_bits):
            # By using mask take data needed from buffer
            res = self.dataPart & ((2**a_bits)-1)
            self.bitsFree -= a_bits
            # Check if we need to grab new data to buffer
            if(self.bitsFree == 0):
                self.fetchNext()
            else:
                # Move buffer to the right
                self.dataPart >>= a_bits
            return res
        else:
            # Take whats left
            res = self.dataPart
            a_bits -= self.bitsFree
            # Save how many free bits we used
            t_bitsFree = self.bitsFree
            # Grab new data to buffer
            self.fetchNext()
            # Append new data to result
            if(self.overflow):
                return 0
            res |= ((self.dataPart & ((2**a_bits)-1)) << t_bitsFree)
            self.bitsFree -= a_bits
            # Move buffer to the right
            self.dataPart >>= a_bits
            return res

    # Read signed n-bits
    def readSBitLong(self, a_bits):
        return (self.readUBitLong(a_bits) << (32 - a_bits)) >> (32 - a_bits)

    # Read string
    def readString(self):
        res = ""
        while True:
            char = self.readSBitLong(8)
            if(char == 0):
                break
            res += chr(char)
        return res

    # Read n-bits
    def readBits(self, a_bits):
        res = b''
        bitsleft = a_bits
        while(bitsleft >= 32):
            res += bytes([self.readUBitLong(8), self.readUBitLong(8), self.readUBitLong(8), self.readUBitLong(8)])
            bitsleft -= 32
        while(bitsleft >= 8):
            res += bytes([self.readUBitLong(8)])
            bitsleft -= 8
        if(bitsleft):
            res += bytes([self.readUBitLong(bitsleft)])
        return res

    # Read n-bytes
    def readBytes(self, a_bytes):
        return self.readBits(a_bytes << 3)

    # Read 1 bit
    def readBit(self):
        aBit = self.dataPart & 1
        self.bitsFree -= 1
        if(self.bitsFree == 0):
            self.fetchNext()
        else:
            self.dataPart >>= 1
        return aBit
    # ---------------------------------------------------------
    def __init__(self, a_data):
        # Save data to vars
        self.data      = a_data
        self.dataBytes = len(a_data)

        # Calculate head
        head = self.dataBytes%4

        # If there is less bytes than potencial head OR head exists
        if( self.dataBytes < 4 or head > 0 ):
            if(head > 2):
                self.dataPart = self.data[0] + (self.data[1] << 8) + (self.data[2] << 16)
                self.posByte = 3
            elif(head > 1):
                self.dataPart = self.data[0] + (self.data[1] << 8)
                self.posByte = 2
            else:
                self.dataPart = self.data[0]
                self.posByte = 1
            self.bitsFree = head << 3
        else:
            self.posByte = head
            self.dataPart = self.data[self.posByte] + (self.data[self.posByte + 1] << 8) + (self.data[self.posByte + 2] << 16) + (self.data[self.posByte + 3] << 24)
            if(self.data):
                self.fetchNext()
            else:
                self.dataPart = 0
                self.bitsFree = 1
            self.bitsFree = min(self.bitsFree, 32)