import struct, sys, csgo, json
import cstrike15_usermessages_public_pb2 as protocs
import netmessages_public_pb2 as protonet
#------------------------------
#    Options
#------------------------------

PRINT_DATATABLE = False
SIMPLIFY_TICK   = True
SIMPLIFY_SOUND  = True
SIMPLIFY_EVENT  = True
SIMPLIFY_DATA   = True

SAVE_AS_JSON = True

#------------------------------
#    Demo & file variables
#------------------------------

FILE_BUFFER_POS  = 0       # Position in input file
DEMO_FINISHED    = False   # Has demo finished?

DEMO_TICK        = 0       # Tick right now
DEMO_CMD         = 0       # Command parsed right now
DEMO_PLAYER_SLOT = 0       # Player slot

PREV_DEMO_TICK   = -1      # Previous demo tick, used for json output

HAS_ROUND_ON     = False   # Check if round started
ROUND_NUM        = 1       # Number of the round

#------------------------------
#    Open input and output file
#------------------------------

jsonbuff = {"ticks":[], "events":{}, "players":{}}
jsonbuff_tick = {"tick": PREV_DEMO_TICK, "commands": []}
inFile  = open("test.dem", "rb")
if(SAVE_AS_JSON):
    outFile = open("output.json", "w")
else:
    outFile = open("output.txt", "w", encoding="utf-8")

#------------------------------
#    Read from input file
#------------------------------

# Return bytes
def bread(a_Nbytes):
    global FILE_BUFFER_POS
    val = inFile.read(a_Nbytes)
    FILE_BUFFER_POS += a_Nbytes
    return val

# Return int
def bread_int(a_Nbytes):
    global FILE_BUFFER_POS
    val = inFile.read(a_Nbytes)
    FILE_BUFFER_POS += a_Nbytes
    return int.from_bytes(val, byteorder="little")

# Return float
def bread_float(a_Nbytes):
    global FILE_BUFFER_POS
    val = inFile.read(a_Nbytes)
    FILE_BUFFER_POS += a_Nbytes
    return struct.unpack('f', val)[0]

#------------------------------
#    Read headers
#------------------------------

# Read sequance info [seems no use?]
def readSequenceInfo():
    int1 = bread_int(4)
    int2 = bread_int(4)
    return [int1, int2]

# Read command header
def readCmdHeader():
    t_cmd        = bread(1)
    t_tick       = bread_int(4)
    t_playerSlot = bread(1)
    return [t_cmd, t_tick, t_playerSlot]

#------------------------------
#    Misc functions
#------------------------------

# Decide which event type is used
def whichEventType(a_data, a_type):
    if (a_type == 1):
        return str(a_data.val_string)
    elif (a_type == 2):
        return str(a_data.val_float)
    elif (a_type == 3):
        return str(a_data.val_long)
    elif (a_type == 4):
        return str(a_data.val_short)
    elif (a_type == 5):
        return str(a_data.val_byte)
    elif (a_type == 6):
        return str(a_data.val_bool)
    elif (a_type == 7):
        return str(a_data.val_uint64)
    elif (a_type == 8):
        return str(a_data.val_wstring)
    
# Change bytes to string
def b_str(a_bytes):
    return a_bytes.decode("utf-8")

# Remove \x00 bytes in string
def readString_raw(a_str):
    return a_str.split(b'\0',1)[0]

# Read int32 [the way its compressed]
def readvarint32(x, pos):
    result = ""
    count = 0
    t_pos = pos
    isIt = True
    while (isIt):
        if (count == 5):
            result = int(result, 2)
            return result, pos
        b = bin(x[t_pos])[2:].zfill(8)
        t_pos += 1
        result = b[1:] + result
        count += 1
        isIt = int(b, 2) & 0x80
    result = int(result, 2)
    return result, t_pos

# Read string [the way its compressed]
def readString(a_data, a_pos):
    strin = ""
    while True:
        charz = a_data[a_pos]
        if (charz == 0):
            break
        strin += chr(charz)
        a_pos += 1
    return [strin, a_pos]

#------------------------------
#    Save to output
#------------------------------

def styleKey(a_name, a_key, a_padding):
    return (a_name+": ").ljust(a_padding) + str(a_key) + "\n"

#------------------------------
#    Handle output
#------------------------------

# Demo Header info
def outputDemoHeader(a_data):
    if(SAVE_AS_JSON):
        buff = {}
        buff["demofilestamp"]   = b_str(a_data.demofilestamp)[:-1]
        buff["demoprotocol"]    = a_data.demoprotocol
        buff["networkprotocol"] = a_data.networkprotocol
        buff["servername"]      = b_str(readString_raw(a_data.servername))
        buff["clientname"]      = b_str(readString_raw(a_data.clientname))
        buff["mapname"]         = b_str(readString_raw(a_data.mapname))
        buff["gamedirectory"]   = b_str(readString_raw(a_data.gamedirectory))
        buff["playback_time"]   = a_data.playback_time
        buff["demofilestamp"]   = a_data.playback_ticks
        buff["playback_ticks"]  = a_data.playback_frames
        buff["signonlength"]    = a_data.signonlength
        jsonbuff["demoHeader"] = buff
    else:
        buff = ""
        buff += ">>> CSGO DEMO INFO\n"
        buff += styleKey("demofilestamp", b_str(a_data.demofilestamp)[:-1], 20)
        buff += styleKey("demoprotocol", a_data.demoprotocol, 20)
        buff += styleKey("networkprotocol", a_data.networkprotocol, 20)
        buff += styleKey("servername", b_str(readString_raw(a_data.servername)), 20)
        buff += styleKey("clientname", b_str(readString_raw(a_data.clientname)), 20)
        buff += styleKey("mapname", b_str(readString_raw(a_data.mapname)), 20)
        buff += styleKey("gamedirectory", b_str(readString_raw(a_data.gamedirectory)), 20)
        buff += styleKey("playback_time", a_data.playback_time, 20)
        buff += styleKey("demofilestamp", a_data.playback_ticks, 20)
        buff += styleKey("playback_ticks", a_data.playback_frames, 20)
        buff += styleKey("signonlength", a_data.signonlength, 20)
        buff += "\n>>> CSGO DEMO TRANSCRIPTION\n"
        outFile.write(buff)

# CMD 4
def outputTick(a_data):
    pb_tick = protonet.CNETMsg_Tick()
    pb_tick.ParseFromString(a_data)
    # Save to output
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 4}
        buff["tick"]                               = pb_tick.tick
        buff["host_computationtime"]               = pb_tick.host_computationtime
        buff["host_computationtime_std_deviation"] = pb_tick.host_computationtime_std_deviation
        buff["host_framestarttime_std_deviation"]  = pb_tick.host_framestarttime_std_deviation
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        if(SIMPLIFY_TICK):
            buff += ">> Current tick: ".ljust(30) + str(pb_tick.tick) + "\n\n"
        else:
            buff += "\n##### cmd 4 - Tick\n"
            buff += styleKey("Current tick count", pb_tick.tick, 50)
            buff += styleKey("Host frame computation time in usec", pb_tick.host_computationtime, 50)
            buff += styleKey("Host frame computation time stddev in usec", pb_tick.host_computationtime_std_deviation, 50)
            buff += styleKey("Host frame start time stddev in usec", pb_tick.host_framestarttime_std_deviation, 50)
        outFile.write(buff)
    
# CMD 5
def outputStrCmd(a_data):
    pb_strcomm = protonet.CNETMsg_StringCmd()
    pb_strcomm.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 5}
        buff["command"] = pb_strcomm.command
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 5 - String Command\n"
        buff += styleKey("Command", pb_strcomm.command, 10)
        outFile.write(buff)

# CMD 6
def outputSetCVar(a_data):
    pb_cvar = protonet.CNETMsg_SetConVar()
    pb_cvar.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 6, "cvars": []}
        for i in pb_cvar.convars.cvars:
            buff_i = {}
            buff_i["name"]  = i.name
            buff_i["value"] = i.value
            buff["cvars"].append(buff_i)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 6 - Set CVar\n"
        for i in pb_cvar.convars.cvars:
            buff += styleKey("Name of Cvar", i.name, 17)
            buff += styleKey("Value of Cvar", i.value, 17)
            buff += "\n"
        outFile.write(buff)

# CMD 7
def outputSignOn(a_data):
    pb_signon = protonet.CNETMsg_SignonState()
    pb_signon.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 7}
        buff["signon_state"]       = pb_signon.signon_state
        buff["spawn_count"]        = pb_signon.spawn_count
        buff["num_server_players"] = pb_signon.num_server_players
        buff["map_name"]           = pb_signon.map_name
        buff["players_networkids"] = [i for i in pb_signon.players_networkids]
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 7 - Sign on state\n"
        buff += styleKey("See SIGNONSTATE_ defines", pb_signon.signon_state, 70)
        buff += styleKey("Server spawn count (session number)", pb_signon.spawn_count, 70)
        buff += styleKey("Number of players the server discloses as connected to the server", pb_signon.num_server_players, 70)
        if (len(pb_signon.players_networkids) > 0):
            buff += styleKey("Player network ids", pb_signon.players_networkids[0], 70)
            for i in pb_signon.players_networkids[1:]:
                buff += styleKey("", i, 70)
        else:
            buff += styleKey("Player network ids", "???", 70)
        buff += styleKey("Name of the current map", pb_signon.map_name, 70)
        outFile.write(buff)

# CMD 8
def outputServerInfo(a_data):
    pb_serverInfo = protonet.CSVCMsg_ServerInfo()
    pb_serverInfo.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 8}
        buff["signon_state"]                  = pb_serverInfo.protocol
        buff["spawn_count"]                   = pb_serverInfo.server_count
        buff["is_dedicated"]                  = pb_serverInfo.is_dedicated
        buff["is_official_valve_server"]      = pb_serverInfo.is_official_valve_server
        buff["is_hltv"]                       = pb_serverInfo.is_hltv
        buff["is_redirecting_to_proxy_relay"] = pb_serverInfo.is_redirecting_to_proxy_relay
        buff["c_os"]                          = str(pb_serverInfo.c_os).upper()
        buff["map_crc"]                       = pb_serverInfo.map_crc
        buff["client_crc"]                    = pb_serverInfo.client_crc
        buff["string_table_crc"]              = pb_serverInfo.string_table_crc
        buff["max_clients"]                   = pb_serverInfo.max_clients
        buff["max_classes"]                   = pb_serverInfo.max_classes
        buff["player_slot"]                   = pb_serverInfo.player_slot
        buff["tick_interval"]                 = pb_serverInfo.tick_interval
        buff["game_dir"]                      = pb_serverInfo.game_dir
        buff["map_name"]                      = pb_serverInfo.map_name
        buff["map_group_name"]                = pb_serverInfo.map_group_name
        buff["sky_name"]                      = pb_serverInfo.sky_name
        buff["host_name"]                     = pb_serverInfo.host_name
        buff["ugc_map_id"]                    = pb_serverInfo.ugc_map_id
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 8 - Server Info\n"
        buff += styleKey("Protocol version", pb_serverInfo.protocol, 50)
        buff += styleKey("Number of changelevels since server start", pb_serverInfo.server_count, 50)
        buff += styleKey("Dedicated server", pb_serverInfo.is_dedicated, 50)
        buff += styleKey("Official Valve Server", pb_serverInfo.is_official_valve_server, 50)
        buff += styleKey("HLTV server", pb_serverInfo.is_hltv, 50)
        buff += styleKey("Will be redirecting to proxy relay", pb_serverInfo.is_redirecting_to_proxy_relay, 50)
        buff += styleKey("L = linux, W = Win32", str(pb_serverInfo.c_os).upper(), 50)
        buff += styleKey("Server map CRC", pb_serverInfo.map_crc, 50)
        buff += styleKey("client.dll CRC server is using", pb_serverInfo.client_crc, 50)
        buff += styleKey("String table CRC server is using", pb_serverInfo.string_table_crc, 50)
        buff += styleKey("Max number of clients on server", pb_serverInfo.max_clients, 50)
        buff += styleKey("Max number of server classes", pb_serverInfo.max_classes, 50)
        buff += styleKey("Our client slot number", pb_serverInfo.player_slot, 50)
        buff += styleKey("Server tick interval", pb_serverInfo.tick_interval, 50)
        buff += styleKey("Game directory", pb_serverInfo.game_dir, 50)
        buff += styleKey("Name of current map", pb_serverInfo.map_name, 50)
        buff += styleKey("Name of current map group name", pb_serverInfo.map_group_name, 50)
        buff += styleKey("Name of current skybox", pb_serverInfo.sky_name, 50)
        buff += styleKey("Server name", pb_serverInfo.host_name, 50)
        buff += styleKey("Ugc map id", pb_serverInfo.ugc_map_id, 50)
        outFile.write(buff)
    
# CMD 10
def outputClassInfo(a_data):
    pb_classinfo = protonet.CSVCMsg_ClassInfo()
    pb_classinfo.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 10}
        buff["create_on_client"] = pb_classinfo.create_on_client
        buff["classes"]          = []
        for i in pb_classinfo.classes:
            buff_i = {}
            buff_i["class_id"]        = i.class_id
            buff_i["data_table_name"] = i.data_table_name
            buff_i["class_name"]      = i.class_name
            buff["classes"].append(buff_i)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 10 - Class Info\n"
        buff += styleKey("Create on client", pb_classinfo.create_on_client, 25)
        for i in pb_classinfo.classes:
            buff += styleKey("Class ID", i.class_id, 17)
            buff += styleKey("Data table name", i.data_table_name, 17)
            buff += styleKey("Class name", i.class_name, 17)
        outFile.write(buff)
    
# CMD 12
def outputCStrTable(a_data):
    pb_cstable = protonet.CSVCMsg_CreateStringTable()
    pb_cstable.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 12}
        buff["name"]                  = pb_cstable.name
        buff["max_entries"]           = pb_cstable.max_entries
        buff["num_entries"]           = pb_cstable.num_entries
        buff["user_data_fixed_size"]  = pb_cstable.user_data_fixed_size
        buff["user_data_size"]        = pb_cstable.user_data_size
        buff["user_data_size_bits"]   = pb_cstable.user_data_size_bits
        buff["flags"]                 = pb_cstable.flags
        buff["string_data"]           = str(pb_cstable.string_data)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 12 - Create String Table\n"
        buff += styleKey("Name", pb_cstable.name, 25)
        buff += styleKey("Max entries", pb_cstable.max_entries, 25)
        buff += styleKey("Num entries", pb_cstable.num_entries, 25)
        buff += styleKey("User data fixed size", pb_cstable.user_data_fixed_size, 25)
        buff += styleKey("User data size", pb_cstable.user_data_size, 25)
        buff += styleKey("User data size bits", pb_cstable.user_data_size_bits, 25)
        buff += styleKey("Flags", pb_cstable.flags, 25)
        buff += styleKey("String data", pb_cstable.string_data, 25)
        outFile.write(buff)
    
# CMD 13
def outputUStrTable(a_data):
    pb_ustrtable = protonet.CSVCMsg_UpdateStringTable()
    pb_ustrtable.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 13}
        buff["table_id"]            = pb_ustrtable.table_id
        buff["num_changed_entries"] = pb_ustrtable.num_changed_entries
        if(not SIMPLIFY_DATA):
            buff["string_data"]         = pb_ustrtable.string_data
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 13 - Update String Table\n"
        buff += styleKey("Table ID", pb_ustrtable.table_id, 25)
        buff += styleKey("Num of changed entries", pb_ustrtable.num_changed_entries, 25)
        if(not SIMPLIFY_DATA):
            buff += styleKey("String data", pb_ustrtable.string_data, 25)
        outFile.write(buff)
    
# CMD 14
def outputVoiceInit(a_data):
    pb_voiceinit = protonet.CSVCMsg_VoiceInit()
    pb_voiceinit.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 14}
        buff["quality"] = pb_voiceinit.quality
        buff["codec"]   = pb_voiceinit.codec
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 14 - Voice Init\n"
        buff += styleKey("Quality", pb_voiceinit.quality, 10)
        buff += styleKey("Codec", pb_voiceinit.codec, 10)
        outFile.write(buff)
    
# CMD 17
def outputSound(a_data):
    pb_sounds = protonet.CSVCMsg_Sounds()
    pb_sounds.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 17}
        buff["reliable_sound"] = pb_sounds.reliable_sound
        buff["sounds"]         = []
        for i in pb_sounds.sounds:
            buff_i = {}
            buff_i["origin_x"]         = i.origin_x
            buff_i["origin_y"]         = i.origin_y
            buff_i["origin_z"]         = i.origin_z
            buff_i["volume"]           = i.volume
            buff_i["delay_value"]      = i.delay_value
            buff_i["sequence_number"]  = i.sequence_number
            buff_i["entity_index"]     = i.entity_index
            buff_i["channel"]          = i.channel
            buff_i["pitch"]            = i.pitch
            buff_i["flags"]            = i.flags
            buff_i["sound_num"]        = i.sound_num
            buff_i["sound_num_handle"] = i.sound_num_handle
            buff_i["speaker_entity"]   = i.speaker_entity
            buff_i["random_seed"]      = i.random_seed
            buff_i["sound_level"]      = i.sound_level
            buff_i["is_sentence"]      = i.is_sentence
            buff_i["is_ambient"]       = i.is_ambient
            buff["sounds"].append(buff_i)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 17 - Sounds\n"
        buff += styleKey("Reliable sound", pb_sounds.reliable_sound, 25)
        buff += "Sounds:\n"
        for i in pb_sounds.sounds:
            if(SIMPLIFY_SOUND):
                buff += styleKey("> Sound", " ".join([str(x) for x in [i.origin_x, i.origin_y, i.origin_z, i.volume, i.delay_value, i.sequence_number, i.entity_index, i.channel, i.pitch, i.flags, i.sound_num, i.sound_num_handle, i.speaker_entity, i.random_seed, i.sound_level, i.is_sentence, i.is_ambient]]), 10)
            else:
                buff += styleKey("> Origin X", i.origin_x, 25)
                buff += styleKey("> Origin Y", i.origin_y, 25)
                buff += styleKey("> Origin Z", i.origin_z, 25)
                buff += styleKey("> Volume", i.volume, 25)
                buff += styleKey("> Delay Value", i.delay_value, 25)
                buff += styleKey("> Sequence Number", i.sequence_number, 25)
                buff += styleKey("> Entity Index", i.entity_index, 25)
                buff += styleKey("> Channel", i.channel, 25)
                buff += styleKey("> Pitch", i.pitch, 25)
                buff += styleKey("> Flags", i.flags, 25)
                buff += styleKey("> Sound num", i.sound_num, 25)
                buff += styleKey("> Sound num handle", i.sound_num_handle, 25)
                buff += styleKey("> Speaker_entity", i.speaker_entity, 25)
                buff += styleKey("> Random seed", i.random_seed, 25)
                buff += styleKey("> Sound level", i.sound_level, 25)
                buff += styleKey("> Is sentence", i.is_sentence, 25)
                buff += styleKey("> Is ambient ", i.is_ambient, 25)
        outFile.write(buff)
   
# CMD 18
def outputSetView(a_data):
    pb_setview = protonet.CSVCMsg_SetView()
    pb_setview.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 18}
        buff["entity_index"] = pb_setview.entity_index
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 18 - Set View\n"
        buff += styleKey("Entity index", pb_setview.entity_index, 15)
        outFile.write(buff)
    
# CMD 23
def outputUserMsg(a_data):
    pb_usermsg = protonet.CSVCMsg_UserMessage()
    pb_usermsg.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 23}
        buff["msg_type"] = pb_usermsg.msg_type
        buff["msg_data"] = str(pb_usermsg.msg_data)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 23 - User Message\n"
        buff += styleKey("Msg type", pb_usermsg.msg_type, 10)
        buff += styleKey("Msg data", pb_usermsg.msg_data, 10)
        outFile.write(buff)
    
# CMD 25
def outputGameEvent(a_data):
    pb_gameevent = protonet.CSVCMsg_GameEvent()
    pb_gameevent.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 25}
        buff["event_name"] = pb_gameevent.event_name
        buff["eventid"] = pb_gameevent.eventid
        buff["keys"] = []
        for i in pb_gameevent.keys:
            buff_i = {}
            buff_i["type"] = i.type
            if (i.type == 1):
                buff_i["value"] = i.val_string
            elif (i.type == 2):
                buff_i["value"] = i.val_float
            elif (i.type == 3):
                buff_i["value"] = i.val_long
            elif (i.type == 4):
                buff_i["value"] = i.val_short
            elif (i.type == 5):
                buff_i["value"] = str(i.val_byte)
            elif (i.type == 6):
                buff_i["value"] = i.val_bool
            elif (i.type == 7):
                buff_i["value"] = i.val_uint64
            elif (i.type == 8):
                buff_i["value"] = i.val_wstring
            buff["keys"].append(buff_i)
        jsonbuff_tick["commands"].append(buff)
        
        # Parse events for simplicity
        if(pb_gameevent.eventid == 7):
            jsonbuff["players"][buff["keys"][2]["value"]] = {"name": buff["keys"][0]["value"]}
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 25 - Game Event\n"
        if(SIMPLIFY_EVENT):
            buff += styleKey("Event", str(pb_gameevent.event_name) + " " + str(pb_gameevent.eventid) + " | " + ", ".join([whichEventType(i, i.type) for i in pb_gameevent.keys]), 10)
        else:
            buff += styleKey("Event name", pb_gameevent.event_name, 20)
            buff += styleKey("Event id", pb_gameevent.eventid, 20)
            buff += "Keys:\n"
            for i in pb_gameevent.keys:
                buff += styleKey("> Type", i.type, 20)
                if(i.type == 1):
                    buff += styleKey("> String", i.val_string, 20)
                elif(i.type == 2):
                    buff += styleKey("> Float", i.val_float, 20)
                elif (i.type == 3):
                    buff += styleKey("> Long", i.val_long, 20)
                elif (i.type == 4):
                    buff += styleKey("> Short", i.val_short, 20)
                elif (i.type == 5):
                    buff += styleKey("> Byte", i.val_byte, 20)
                elif (i.type == 6):
                    buff += styleKey("> Bool", i.val_bool, 20)
                elif (i.type == 7):
                    buff += styleKey("> UINT64", i.val_uint64, 20)
                elif (i.type == 8):
                    buff += styleKey("> Wstring", i.val_wstring, 20)
        outFile.write(buff)

# CMD 26
def outputPEntities(a_data):
    pb_pentities = protonet.CSVCMsg_PacketEntities()
    pb_pentities.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 26}
        buff["max_entries"]     = pb_pentities.max_entries
        buff["updated_entries"] = pb_pentities.updated_entries
        buff["is_delta"]        = pb_pentities.is_delta
        buff["update_baseline"] = pb_pentities.update_baseline
        buff["baseline"]        = pb_pentities.baseline
        buff["delta_from"]      = pb_pentities.delta_from
        if(not SIMPLIFY_DATA):
            buff["entity_data"] = pb_pentities.entity_data
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 26 - Packet Entities\n"
        buff += styleKey("Max entries", pb_pentities.max_entries, 20)
        buff += styleKey("Updated entries", pb_pentities.updated_entries, 20)
        buff += styleKey("Is delta", pb_pentities.is_delta, 20)
        buff += styleKey("Update baseline", pb_pentities.update_baseline, 20)
        buff += styleKey("Baseline", pb_pentities.baseline, 20)
        buff += styleKey("Delta from", pb_pentities.delta_from, 20)
        if (not SIMPLIFY_DATA):
            buff += styleKey("Entity data", pb_pentities.entity_data, 20)
        outFile.write(buff)
    
# CMD 27
def outputTEntities(a_data):
    pb_tentities = protonet.CSVCMsg_TempEntities()
    pb_tentities.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 27}
        buff["reliable"]    = pb_tentities.reliable
        buff["num_entries"] = pb_tentities.num_entries
        if(not SIMPLIFY_DATA):
            buff["entity_data"] = pb_tentities.entity_data
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 27 - Temp Entities\n"
        buff += styleKey("Reliable", pb_tentities.reliable, 15)
        buff += styleKey("Num entries", pb_tentities.num_entries, 15)
        if (not SIMPLIFY_DATA):
            buff += styleKey("Entity data", pb_tentities.entity_data, 15)
        outFile.write(buff)
    
# CMD 28
def outputPrefetch(a_data):
    pb_prefetch = protonet.CSVCMsg_Prefetch()
    pb_prefetch.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 28}
        buff["sound_index"] = pb_prefetch.sound_index
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 28 - Prefetch\n"
        buff += styleKey("Sound index", pb_prefetch.sound_index, 15)
        outFile.write(buff)
    
# CMD 30
def outputGameEventList(a_data):
    pb_eventlist = protonet.CSVCMsg_GameEventList()
    pb_eventlist.ParseFromString(a_data)
    if(SAVE_AS_JSON):
        buff = {"comm_nr": 30, "descriptors": []}
        for i in pb_eventlist.descriptors:
            buff_i = {}
            buff_i["eventid"] = i.eventid
            buff_i["name"]    = i.name
            buff_i["keys"]    = []
            jsonbuff["events"][i.eventid] = {"name": i.name, "keys": []}
            for j in i.keys:
                buff_j = {}
                buff_j["type"] = j.type
                buff_j["name"] = j.name
                jsonbuff["events"][i.eventid]["keys"].append(buff_j)
                buff_i["keys"].append(buff_j)
            buff["descriptors"].append(buff_i)
        jsonbuff_tick["commands"].append(buff)
    else:
        buff = ""
        # Save to output
        buff += "\n##### cmd 30 - Game Event List\n"
        for i in pb_eventlist.descriptors:
            buff += styleKey("Event ID", i.eventid, 10)
            buff += styleKey("Name", i.name, 10)
            buff += "Keys:\n"
            for j in i.keys:
                buff += styleKey("> Key type", j.type, 10)
                buff += styleKey("> Key name", j.name, 10)
            buff += "\n"
        outFile.write(buff)
    
#------------------------------
#     WIP
#------------------------------
def handleStringTable():
    lens = bread_int(4)
    poz = 0
    numTables = bread_int(1)
    data = bread(lens-1)
    # for i in range(numTables):
    #     tableName, poz = readString(data, poz)
    #     numstrings = int.from_bytes(data[poz:poz+2], byteorder="little")
    #     poz += 2
    #     for j in range(numstrings):
    #         word, poz = readString(data, poz)
            #print(numstrings)
def handleDataTable():
    lens = bread_int(4)
    poz = 0
    data = bread(lens)
    pb_sendtable = protonet.CSVCMsg_SendTable()
    if(SAVE_AS_JSON):
        buff = {}
        while True:
            typed, poz = readvarint32(data, poz)
            size, poz = readvarint32(data, poz)
            pb_sendtable.ParseFromString(data[poz:poz+size])
            if (pb_sendtable.is_end):
                break
            poz += size
    else:
        outFile.write("#### Data Table" + "\n")
        while True:
            typed, poz = readvarint32(data, poz)
            size, poz = readvarint32(data, poz)
            pb_sendtable.ParseFromString(data[poz:poz+size])
            if(PRINT_DATATABLE):
                outFile.write("Is end: ".ljust(20) + str(pb_sendtable.is_end) + "\n")
                outFile.write("Table name: ".ljust(20) + str(pb_sendtable.net_table_name) + "\n")
                outFile.write("Need decoder: ".ljust(20) + str(pb_sendtable.needs_decoder) + "\n\n")
                for i in pb_sendtable.props:
                    outFile.write("Type: ".ljust(20) + str(i.type) + "\n")
                    outFile.write("Var name: ".ljust(20) + str(i.var_name) + "\n")
                    outFile.write("Flags: ".ljust(20) + str(i.flags) + "\n")
                    outFile.write("Priority: ".ljust(20) + str(i.priority) + "\n")
                    outFile.write("Dt name: ".ljust(20) + str(i.dt_name) + "\n")
                    outFile.write("Num of elements: ".ljust(20) + str(i.num_elements) + "\n")
                    outFile.write("Low value: ".ljust(20) + str(i.low_value) + "\n")
                    outFile.write("High value: ".ljust(20) + str(i.high_value) + "\n")
                    outFile.write("Num bits: ".ljust(20) + str(i.num_bits) + "\n\n")
            if(pb_sendtable.is_end):
                break
            poz += size

#------------------------------
#     Handle Demo Packet
#------------------------------

def handleDemoPacket():
    info = csgo.struct_democmdinfo()
    info.ReadCmdInfo(bread(csgo.DEMOCMDINFO_SIZE))        # Read command info
    dummy, dummy = readSequenceInfo()                     # Seems no use
    lens = bread_int(4)
    data = bread(lens)
    pos = 0
    while(pos < lens):
        cmd, pos  = readvarint32(data, pos)
        size, pos = readvarint32(data, pos)
        buffer = data[pos:pos + size]
        # Tick
        if(cmd == 4):
            outputTick(buffer)
        # String Command
        elif(cmd == 5):
            outputStrCmd(buffer)
        # Sends one/multiple convar/userinfo settings
        elif(cmd == 6):
            outputSetCVar(buffer)
        # Signon State
        elif (cmd == 7):
            outputSignOn(buffer)
        # Server info
        elif(cmd == 8):
            outputServerInfo(buffer)
        # Class info
        elif(cmd == 10):
            outputClassInfo(buffer)
        # Create String Table
        elif(cmd == 12):
            outputCStrTable(buffer)
        # Update String Table
        elif(cmd == 13):
            outputUStrTable(buffer)
        # Voice Init
        elif(cmd == 14):
            outputVoiceInit(buffer)
        # Sounds
        elif(cmd == 17):
            outputSound(buffer)
        # Set View
        elif(cmd == 18):
            outputSetView(buffer)
        # User Message
        elif(cmd == 23):
            outputUserMsg(buffer)
        # Game Event
        elif(cmd == 25):
            outputGameEvent(buffer)
        # Packet Entities
        elif(cmd == 26):
            outputPEntities(buffer)
        # Temp Entities
        elif(cmd == 27):
            outputTEntities(buffer)
        # Prefetch
        elif(cmd == 28):
            outputPrefetch(buffer)
        # Game Event List
        elif(cmd == 30):
            outputGameEventList(buffer)
        # Unhandled event
        elif(0 <= cmd < 32):
            print("---UNHANDLED EVENT---")
            print(cmd, size)
            print(buffer)
            sys.exit(0)
            
        pos += size
        
#------------------------------
#    Main function
#------------------------------

# Process demo header
demoHeader = csgo.struct_demoheader()
demoHeader.demofilestamp   = bread(8)
demoHeader.demoprotocol    = bread_int(4)
demoHeader.networkprotocol = bread_int(4)
demoHeader.servername      = bread(260)
demoHeader.clientname      = bread(260)
demoHeader.mapname         = bread(260)
demoHeader.gamedirectory   = bread(260)
demoHeader.playback_time   = bread_float(4)
demoHeader.playback_ticks  = bread_int(4)
demoHeader.playback_frames = bread_int(4)
demoHeader.signonlength    = bread_int(4)

outputDemoHeader(demoHeader)

# Dump demo
s_bMatchStartOccured = False
if (demoHeader.demofilestamp == csgo.DEMO_HEADER_ID and demoHeader.demoprotocol == csgo.DEMO_PROTOCOL):
    while not DEMO_FINISHED:
        DEMO_CMD, DEMO_TICK, DEMO_PLAYER_SLOT = readCmdHeader()
        if(PREV_DEMO_TICK != DEMO_TICK):
            if(PREV_DEMO_TICK != -1):
                if(PREV_DEMO_TICK < 1000000):
                    jsonbuff["ticks"].append(jsonbuff_tick)
                else:
                    jsonbuff_tick["tick"] = "start"
                    jsonbuff["ticks"].append(jsonbuff_tick)
            PREV_DEMO_TICK = DEMO_TICK
            jsonbuff_tick = {"tick": DEMO_TICK, "commands": []}
        if (DEMO_CMD == csgo.dem_signon or DEMO_CMD == csgo.dem_packet):
            handleDemoPacket()
            
        elif (DEMO_CMD == csgo.dem_usercmd):
            DEMO_FINISHED = True
            print("dem_usercmd")
            
        elif (DEMO_CMD == csgo.dem_stringtables):
            handleStringTable()
            print("dem_stringtables")
            
        elif (DEMO_CMD == csgo.dem_datatables):
            handleDataTable()
            print("dem_datatables")
            
        elif (DEMO_CMD == csgo.dem_consolecmd):
            DEMO_FINISHED = True
            print("dem_consolecmd")
            
        elif (DEMO_CMD == csgo.dem_stop):
            DEMO_FINISHED = True
            if(SAVE_AS_JSON):
                json.dump(jsonbuff, outFile)
            print("dem_stop")
            
        elif (DEMO_CMD == csgo.dem_synctick):
            pass