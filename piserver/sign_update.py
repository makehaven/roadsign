import serial

DISPLAY_WIDTH = 96
DISPLAY_HEIGHT = 27
DISPLAY_SIZE = (DISPLAY_WIDTH * DISPLAY_HEIGHT)

PANEL_WIDTH = 24
PANEL_HEIGHT = 9
PANEL_SIZE = (PANEL_WIDTH * PANEL_HEIGHT)
BLOCK_SIZE = (DISPLAY_WIDTH * PANEL_HEIGHT)

SIGN_INIT = b'\xFE\x6C\x00'
SIGN_SYNC = b'\xFE\xAA\x00'

def cartesian_to_pixel_offset(x, y):
    return ((y // PANEL_HEIGHT) * BLOCK_SIZE) + ((y % PANEL_HEIGHT) * PANEL_WIDTH) + (((x // PANEL_WIDTH) * PANEL_SIZE) + PANEL_WIDTH - (x % PANEL_WIDTH)) - 1

def cartesian_offset_to_pixel_offset(offset):
    y = offset // DISPLAY_WIDTH
    x = offset - (y * DISPLAY_WIDTH)

    y = (DISPLAY_HEIGHT - 1) - y

    return cartesian_to_pixel_offset(x, y)

def encode_framebuffer(buf):
    msg = [0,] * (DISPLAY_SIZE // 8)

    for i in range(DISPLAY_SIZE):
        offset = cartesian_offset_to_pixel_offset(i)
        msg[offset // 8] |= int(buf[i]) << (i % 8)
    
    msg = bytes(msg)
    return msg

def update(buf):
    s = serial.Serial(port='/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0', baudrate=57600)
    s.write(SIGN_INIT)
    s.write(SIGN_SYNC)
    msg = encode_framebuffer(buf)
    s.write(msg)
    s.close()        
