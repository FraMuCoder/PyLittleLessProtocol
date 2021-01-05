# Little Less Protocol for Python
#
# Copyright (C) 2021 Frank Mueller
#
# SPDX-License-Identifier: MIT

from enum import Enum

class MessagesType(Enum):
    def __init__(self, value, code):
        self._value_ = value
        self.code = code

    REQUEST = (0, '>')
    RESPONSE = (1, '<')
    ERROR = (2, '!')
    UPDATE = (3, '#')
    
    @classmethod
    def get_from_code(cls, c):
        for msg_type in MessagesType:
            if c == msg_type.code:
                return msg_type
        return None

class ProtocolException(Exception):
    def __init__(self, msg=''):
        self.message = msg

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.message)


class FrameError(ProtocolException):
    pass
