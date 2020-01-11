#!/usr/bin/python3
import re

def pythonize_iso_timestamp(timestamp):
    """ Convert ISO 8601 timestamp to python .fromisoformat()-compliant format """
    # 'Z'-timezone to '+00:00'-timezone
    timestamp = timestamp.replace('Z', '+00:00')
    # '+0000'-timezone to '+00:00'-timezone
    def repl(matchobj):
        sign = matchobj.group(1)
        offset = matchobj.group(2)
        hh, mm = offset[0:2], offset[2:4]
        return "{}{}:{}".format(sign, hh, mm)
    timestamp = re.sub(r'(\+|-)(\d{4})', repl, timestamp)
    # '.39' microseconds to '.390000' microseconds
    def repl2(matchobj):
        ms = matchobj.group(1)
        sign = matchobj.group(2)
        return ".{}{}".format(ms[:6].ljust(6, '0'), sign)
    timestamp = re.sub(r'\.(\d*)($|\+|-)', repl2, timestamp)
    return timestamp
