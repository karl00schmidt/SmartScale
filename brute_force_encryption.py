from Cryptodome.Cipher import AES, DES3  # Importing AES and Triple DES from PyCryptodome

# Define the encrypted data
encrypted_data = bytes.fromhex("13009cca5364a39ac214983f2ce410ae")  # Example encrypted data
mac = 'dced8374780a'

# Define the key
# key = "09cc35c663b9c299f551f717"  # Key in hexadecimal format
key = bytes.fromhex("076688ba6ef833212d03a83693dd7f9f")  # Key from BLE token

# Define the possible encryption algorithms to try
encryption_algorithms = ['AES', 'DES3']  # Add other algorithms as needed


def parse_value(hexvalue):
    length = hexvalue[4]
    weightValue = (hexvalue[6] & 0xff) << 8 | hexvalue[5] & 0xff
    print("weightValue", weightValue)
    return weightValue


def decrypt_payload(payload, key, nonce, mac):
    token = payload[-4:]  # mic
    cipherpayload = payload[:-4]  # EncodeData
    # print("Nonce: %s" % nonce.hex())
    # print("CryptData: %s" % cipherpayload.hex(), "Mic: %s" % token.hex())
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    data = None
    try:
        data = cipher.decrypt_and_verify(cipherpayload, token)
    except ValueError as error:
        print(error)
        mac = mac.hex()
        macReversed = ""
        for x in range(-1, -len(mac), -2):
            macReversed += mac[x - 1] + mac[x] + ":"
        macReversed = macReversed.upper()[:-1]
        print("ERROR: Decryption failed with sensor MAC (probably wrong key provided):", macReversed)
        return None
    print("DecryptData:", data.hex())
    # print()
    # if parse_value(data) != None:
    # 	return 1
    # #print('??')
    # return None
    return parse_value(data)


def decrypt_aes_ccm(key, mac, data):
    print("MAC:", mac.hex(), "Binkey:", key.hex())
    # print()
    adslength = len(data)
    if adslength > 8:
        pkt = data[:data[0] + 1]
        # nonce: mac[6] + head[4] + cnt[1]
        nonce = b"".join([mac, pkt[:5]])
        return decrypt_payload(pkt[5:], key, nonce, mac)
    else:
        print("Error: format packet!")
    return None

macReversed=""
for x in range(-1, -len(mac), -2):
    macReversed += mac[x-1] + mac[x]
macReversed = bytes.fromhex(macReversed.lower())
decrypt_aes_ccm(key, macReversed, encrypted_data)
# nonce = b"".join([macReversed, encrypted_data[:5]])
# token = encrypted_data[-4:]  # mic
# cipherpayload = encrypted_data[:-4]  # EncodeData
# cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
# print(cipher.decrypt(bytes(cipherpayload)))