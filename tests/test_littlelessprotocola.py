# Little Less Protocol for Python
#
# Copyright (C) 2021 Frank Mueller
#
# SPDX-License-Identifier: MIT

import unittest
from unittest.mock import Mock
from littlelessprotocol import LittleLessProtocolA, MessagesType

class LittleLessProtocolAMock(LittleLessProtocolA):
    def __init__(self):
        super().__init__()
        self.get_cmd_id = Mock(return_value=0)
        self.get_cmd_str = Mock(return_value='TST')
        self.handle_msg = Mock()
        self.handle_unknown_frame = Mock()

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.test_obj = LittleLessProtocolAMock()
        self.test_obj.connection_made(Mock())

    def tearDown(self):
        self.test_obj.connection_lost(Mock())
        self.test_obj = None

    def test_rx_valid_request(self):
        test_frame = bytearray('>TST:01:AB:FF\r\n', 'ascii')
        
        self.test_obj.data_received(test_frame)
        
        self.test_obj.get_cmd_id.assert_called_once_with('TST')
        self.test_obj.get_cmd_str.assert_not_called()
        self.test_obj.handle_msg.assert_called_once_with(MessagesType.REQUEST, 0, bytearray.fromhex('AB'))
        self.test_obj.handle_unknown_frame.assert_not_called()

    def test_rx_valid_response(self):
        test_frame = bytearray('<abc:03:010203:FF\r\n', 'ascii')
        self.test_obj.get_cmd_id.return_value = 1
        
        self.test_obj.data_received(test_frame)
        
        self.test_obj.get_cmd_id.assert_called_once_with('abc')
        self.test_obj.get_cmd_str.assert_not_called()
        self.test_obj.handle_msg.assert_called_once_with(MessagesType.RESPONSE, 1, bytearray.fromhex('010203'))
        self.test_obj.handle_unknown_frame.assert_not_called()

    def test_rx_valid_error(self):
        test_frame = bytearray('!ERR:00::FF\r\n', 'ascii')
        self.test_obj.get_cmd_id.return_value = 100
        
        self.test_obj.data_received(test_frame)
        
        self.test_obj.get_cmd_id.assert_called_once_with('ERR')
        self.test_obj.get_cmd_str.assert_not_called()
        self.test_obj.handle_msg.assert_called_once_with(MessagesType.ERROR, 100, bytearray())
        self.test_obj.handle_unknown_frame.assert_not_called()

    def test_rx_valid_update(self):
        test_frame = bytearray('#dat:02:CAFE:FF\r\n', 'ascii')
        self.test_obj.get_cmd_id.return_value = 13
        
        self.test_obj.data_received(test_frame)
        
        self.test_obj.get_cmd_id.assert_called_once_with('dat')
        self.test_obj.get_cmd_str.assert_not_called()
        self.test_obj.handle_msg.assert_called_once_with(MessagesType.UPDATE, 13, bytearray.fromhex('CAFE'))
        self.test_obj.handle_unknown_frame.assert_not_called()

    def test_rx_valid_ascii(self):
        test_frame = bytearray('#dat:04:"Text":FF\r\n', 'ascii')
        
        self.test_obj.data_received(test_frame)
        
        self.test_obj.get_cmd_id.assert_called_once_with('dat')
        self.test_obj.get_cmd_str.assert_not_called()
        self.test_obj.handle_msg.assert_called_once_with(MessagesType.UPDATE, 0, 'Text'.encode('ascii'))
        self.test_obj.handle_unknown_frame.assert_not_called()

    def test_tx_valid_request(self):
        self.test_obj.send_message(MessagesType.REQUEST, 0, b'\x01\x02\x03')
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(0)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'>TST:03:010203:ff\r\n')
        
    def test_tx_valid_response(self):
        self.test_obj.get_cmd_str.return_value = 'abc'

        self.test_obj.send_message(MessagesType.RESPONSE, 1, b'\xCA\xFE')
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(1)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'<abc:02:cafe:ff\r\n')

    def test_tx_valid_error(self):
        self.test_obj.get_cmd_str.return_value = 'XYZ'

        self.test_obj.send_message(MessagesType.ERROR, 123, b'\xEE')
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(123)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'!XYZ:01:ee:ff\r\n')

    def test_tx_valid_update(self):
        self.test_obj.get_cmd_str.return_value = 'dat'

        self.test_obj.send_message(MessagesType.UPDATE, 99)
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(99)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'#dat:00::ff\r\n')

    def test_tx_valid_ascii(self):
        self.test_obj.send_message(MessagesType.UPDATE, 0, 'Hello World!')
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(0)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'#TST:0c:"Hello World!":ff\r\n')

    def test_tx_valid_mixed(self):
        self.test_obj.send_message(MessagesType.UPDATE, 0, '', b'\x05', 'Hello', b'\x06', 'World!','')
        
        self.test_obj.get_cmd_id.assert_not_called()
        self.test_obj.get_cmd_str.assert_called_once_with(0)
        self.test_obj.handle_msg.assert_not_called()
        self.test_obj.handle_unknown_frame.assert_not_called()
        self.test_obj.transport.write.assert_called_once_with(b'#TST:0d:""05"Hello"06"World!""":ff\r\n')

if __name__ == '__main__':
    unittest.main()