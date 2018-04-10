# coding: utf-8

import random

class ApiKey(object):
    
    @staticmethod
    def generate ():
        return '%04x%04x-%04x-%04x-%04x-%04x%04x%04x' % (
            # 32 bits for "time_low"
            random.randint(0, 0xffff), random.randint(0, 0xffff),
            # 16 bits for "time_mid"
            random.randint(0, 0xffff),
            # 16 bits for "time_hi_and_version",
            # four most significant bits holds version number 4
            random.randint(0, 0x0fff) | 0x4000,
            # 16 bits, 8 bits for "clk_seq_hi_res",
            # 8 bits for "clk_seq_low",
            # two most significant bits holds zero and one for variant DCE1.1
            random.randint(0, 0x3fff) | 0x8000,
            # 48 bits for "node"
            random.randint(0, 0xffff), random.randint(0, 0xffff), random.randint(0, 0xffff)
        )
    
