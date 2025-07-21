import serial
import time

def calc_bcc(data_bytes):
    bcc = 0
    for b in data_bytes:
        bcc ^= b
    return bcc

def build_command(cmd_str):
    stx = 0x02
    etx = 0x03
    cr = 0x0d
    lf = 0x0a
    cmd_bytes = cmd_str.encode('ascii')
    bcc = 0
    for b in cmd_bytes:
        bcc ^= b
    bcc ^= etx
    bcc_bytes = f"{bcc:02X}".encode('ascii')
    return bytes([stx]) + cmd_bytes + bytes([etx]) + bcc_bytes + bytes([cr, lf])

def send_command(ser, cmd_str):
    cmd = build_command(cmd_str)
    ser.write(cmd)
    time.sleep(0.5)
    return ser.read(100)

def parse_lux(resp_bytes):
    s = resp_bytes.decode('ascii', errors='ignore')
    s_clean = s.strip('\x02\x03\r\n')
    data_str = s_clean[8:].strip()
    for sign_char in ['+', '-', '=']:
        pos = data_str.find(sign_char)
        if pos != -1:
            break
    else:
        return None
    segment = data_str[pos:pos+6]
    sign = segment[0]
    number_str = segment[1:5].replace(' ', '0')
    exponent_str = segment[5]
    try:
        num = int(number_str)
        exp = int(exponent_str)
    except ValueError:
        return None
    val = num * 10**(exp - 4)
    if sign == '-':
        val = -val
    elif sign == '=':
        val = 0.0
    return val

ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=7, parity='E', stopbits=1, timeout=1)
send_command(ser, "00541   ")
resp = send_command(ser, "00100200")
lux = parse_lux(resp)
if lux is not None:
    print("Lux:",lux)
ser.close()
