import serialx.tools.list_ports


def find_ports():
    """Returns the available ports"""
    return serialx.tools.list_ports.comports()
