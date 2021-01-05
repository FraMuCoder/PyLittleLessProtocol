# Little Less Protocol for Python
#
# Copyright (C) 2021 Frank Mueller
#
# SPDX-License-Identifier: MIT

import serial.threaded
from littlelessprotocol.types import *

class FrameState(Enum):
    TYPE = 1            # < > ! #
    CMD = 2             # 3 chars
    COLON1 = 3          # :
    LEN = 4             # 2 x hex
    COLON2 = 5          # :
    DATA_BIN = 6        # n x 2 x hex
    DATA_ASCII = 7      # "ascii"
    DATA_ASCII_ESC = 8  # backslash
    COLON3 = 9          # :
    CHECKSUM = 10       # 2 x hex
    DONE = 11           # \r\n
    ERROR = 12

class LittleLessProtocolA(serial.threaded.Protocol):
    def __init__(self):
        self.rx_buffer = bytearray()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        self.transport = None
        super().connection_lost(exc)
        
    def can_send(self):
        return self.transport is not None

    def data_received(self, data):
        self.rx_buffer.extend(data.replace(b'\r\n', b'\n').replace(b'\r', b'\n'))
        while b'\n' in self.rx_buffer:
            frame, self.rx_buffer = self.rx_buffer.split(b'\n', 1)
            self.handle_frame(frame)

    def handle_frame(self, frame):
        try:
            frame = frame.decode('ascii')
            
            # minimum frame is something like '>abc:00::FF' => 11 bytes
            if len(frame) < 11: raise FrameError('Frame to short for min size')
            
            msg_type = MessagesType.get_from_code(frame[0])
            if msg_type is None: raise FrameError('Unknown message type')
            
            cmd_str = frame[1:4]
            cmd_id = self.get_cmd_id(cmd_str)
            if (cmd_id < 0) or (cmd_id >= 255): raise FrameError('Unknown CMD "{}"'.format(cmd_str))
            
            if frame[4] != ':': raise FrameError('Colon1 expected but found "{}"'.format(frame[4]))
            
            msg_len = int(frame[5:7], 16)

            if frame[7] != ':': raise FrameError('Colon2 expected but found "{}"'.format(frame[7]))

            msg_raw = frame[8:-3]
            ascii_mode = False
            ascii_esc_mode = False
            i = 0
            msg = bytearray()
            while i < len(msg_raw):
                if ascii_mode:
                    if msg_raw[i] == '"':
                        ascii_mode = False
                    elif msg_raw[i] == '\\':
                        ascii_esc_mode = True
                    elif ascii_esc_mode:
                        msg.extend(msg_raw[i].encode('ascii'))
                        ascii_esc_mode = False
                    else:
                        msg.extend(msg_raw[i].encode('ascii'))
                else:
                    if msg_raw[i] == '"':
                        ascii_mode = True
                        ascii_esc_mode = False
                    else:
                        if i+1 >= len(msg_raw): raise FrameError('Last data byte has not two hex digits')
                        msg.append(int(msg_raw[i:i+2], 16))
                        i += 1
                i += 1
            
            if frame[-3] != ':': raise FrameError('Colon3 expected but found "{}"'.format(frame[-3]))
            
            chksum = int(frame[-2:], 16)
            # ToDo chksum
            
            self.handle_msg(msg_type, cmd_id, msg)

        except (UnicodeError, FrameError, ValueError) as e:
            self.handle_unknown_frame(frame, e)

    def get_cmd_id(self, cmd_str: str) -> int:
        return 0xFF

    def get_cmd_str(self, cmd_id: int) -> str:
        return None

    def handle_msg(self, msg_type: MessagesType, cmd_id: int, msg):
        pass

    def handle_unknown_frame(self, frame, err):
        pass

    def send_message(self, msg_type: MessagesType, cmd, *args, encoding='utf-8'):
        if not self.can_send(): raise ProtocolException('Can not send')
        if isinstance(cmd, int):
            cmd_str = self.get_cmd_str(cmd)
        elif isinstance(cmd, str):
            cmd_str = cmd
        else:
            return
        if len(cmd_str) != 3: raise ProtocolException('CMD must be 3 character long')
        
        length = 0
        msg_str = ''
        chksum = 255
        for arg in args:
            if isinstance(arg, (bytearray, bytes)):
                msg_str += arg.hex()
                length += len(arg)
            elif isinstance(arg, str):
                msg_str += '"'
                ascii_mode = True
                for c in arg:
                    o = ord(c)
                    if o < ord(' ') and o > ord('~'):
                        if ascii_mode:
                            msg_str += '"'
                            ascii_mode = False
                        data = c.encode(encoding)
                        msg_str += data.hex()
                        length += len(data)
                    else:
                        length += 1
                        if not ascii_mode:
                            msg_str += '"'
                            ascii_mode = True
                        if c == '\\' or c == '"':
                            msg_str += '\\' + c
                        else:
                            msg_str += c
                if ascii_mode: msg_str += '"'
        
        if length > 255: raise ProtocolException('Frame to long')
        
        frame = "{}{}:{}:{}:{:x}\r\n".format(msg_type.code, cmd_str, bytearray([length]).hex(), msg_str, chksum);
        self.transport.write(frame.encode('ascii'))
