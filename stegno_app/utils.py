from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from PIL import Image

def encrypt_message(data, key):
    key = key.encode('utf-8').ljust(16, b'0')[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(data, 16))

def lsb_encode(image, data):
    binary_data = ''.join(format(byte, '08b') for byte in data)
    pixels = list(image.getdata())
    new_pixels = []

    if len(binary_data) > len(pixels) * 3:
        raise ValueError("Data too large to hide in image")

    data_index = 0
    for pixel in pixels:
        r, g, b = pixel
        if data_index < len(binary_data):
            r = (r & ~1) | int(binary_data[data_index])
            data_index += 1
        if data_index < len(binary_data):
            g = (g & ~1) | int(binary_data[data_index])
            data_index += 1
        if data_index < len(binary_data):
            b = (b & ~1) | int(binary_data[data_index])
            data_index += 1
        new_pixels.append((r, g, b))

    image.putdata(new_pixels)
    return image

def lsb_decode(image, data_length=1024):
    pixels = list(image.getdata())
    binary_data = ''

    for pixel in pixels:
        for color in pixel[:3]:
            binary_data += str(color & 1)
            if len(binary_data) >= data_length * 8:
                break
        if len(binary_data) >= data_length * 8:
            break

    byte_data = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) == 8:
            byte_data.append(int(byte, 2))
    return bytes(byte_data)

def decrypt_message(encrypted_data, key):
    key = key.encode('utf-8').ljust(16, b'0')[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(encrypted_data), 16)