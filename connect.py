import asyncio
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000fe95-0000-1000-8000-00805f9b34fb"
CHARACTERISTICS_UUID = {
    "token": "0001",
    "event": "0010",
    "confirmation": "0001"
}
CHALLENGE_RESPONSE = b'\x09\xac\xbf\x93'
CONFIRMATION_EXPECTED = b'\xc9\x58\x9a\x36'
SESSION_START_LOGIN = b'\x00\xbc\x43\xcd'
SESSION_START_REGISTER = b'\x90\xca\x85\xde'
SESSION_END = b'\x92\xab\x54\xfa'

# Device ID
hotoDeviceID = "3FC506E8-1BC2-5E9B-CED1-7588AECFFF26"

CHARACTERISTICS = {
    "AVDTP": None,
    "UPNP": None,
    "TCP": None,
    "Vendor101": None,
    "Vendor102": None
}

xiaomiMainService = "0x0000fe95-0000-1000-8000"

deviceChallengeExpectation = bytearray(b'\x00\x00\x04\x00\x06\xf2')
deviceChallengeResponseExpectation = bytearray(b'\x00\x00\x05\x00\x06\xf2')

async def print_all_info(client: BleakClient):
    for service in client.services:
            print(f"    Service ({service}):")
            print(f"    UUID: {service.uuid}")
            print(f"    Name: {service.handle}")
            print(f"    Decr: {service.description}")
            print(f"    Characteristics:")
            for characteristic in service.characteristics:
                print(characteristic)
                print(f"        UUID: {characteristic.uuid}")
                print(f"        Name: {characteristic.handle}")
                print(f"        Desc: {characteristic.description}")
                print(f"        Type: {characteristic.properties}")
                print(f"        Service Handle: {characteristic.service_handle}")
                print(f"        Props: {characteristic.properties}")
                print(f"        Descriptors:")
                for descriptor in characteristic.descriptors:
                    print(f"            {descriptor}")
                    print(f"            UUID: {descriptor.uuid}")
                    print(f"            Name: {descriptor.handle}")
                    print(f"            Type: {descriptor}")
                    print(f"            Desc: {descriptor.description}")
                # if "notify" in characteristic.properties:
                #     print(f"    Settting Notify: {characteristic}")
                #     await client.start_notify(characteristic.uuid, handle_notification)
                # if "read" in characteristic.properties:
                #     char = await client.read_gatt_char(characteristic.uuid)
                #     print(f"        GATT Frame: {char}")

async def accumulate_UUIDs(client: BleakClient):
    for service in client.services:
        for characteristic in service.characteristics:
            if characteristic.description in CHARACTERISTICS.keys():
                CHARACTERISTICS[characteristic.description] = characteristic
            if characteristic.description == "Unknown":
                if characteristic.uuid.startswith("00000102"):
                    CHARACTERISTICS['Vendor102'] = characteristic
                if characteristic.uuid.startswith("00000101"):
                    CHARACTERISTICS['Vendor101'] = characteristic


async def handle_authentication(client: BleakClient):
    # Enable notification flag on AVDTP
    key_to_observe = 'AVDTP'
    key_to_write_session_start = 'UPNP'
    session_start_trigger_phrase = 0xa4
    OBSERVE_UUID = CHARACTERISTICS[key_to_observe].uuid
    WRITE_UUID = CHARACTERISTICS[key_to_write_session_start].uuid
    async def handle_notification_from_AVDTP(sender, data):
        # Handle incoming notification data here
        print("---->Received notification from AVDTP:", data)
        if data == deviceChallengeExpectation:
            print("     ✅ Device challenge received")
            print("<----Sending challenge response")
            await client.write_gatt_char(OBSERVE_UUID,deviceChallengeResponseExpectation)
    print(f"   Starting Notification for {key_to_observe}...")
    await client.start_notify(OBSERVE_UUID, handle_notification_from_AVDTP)
    print(f"<----Writing session start request on {WRITE_UUID}...")
    await client.write_gatt_char(WRITE_UUID, bytes([session_start_trigger_phrase]))
async def run_main_connection(client: BleakClient):
    # Connect to the device
    await client.connect()
    print(f"Connected to {client.address}")
    await print_all_info(client)
    print("Accumulating UUIDs from index...")
    await accumulate_UUIDs(client)
    print("Beginning authentication...")
    await handle_authentication(client)

    # If characteristic can be notified on, add a notification
    # characteristic
    while client.is_connected:
        await asyncio.sleep(1)
async def discover_and_connect():
    found_device: BleakClient = None
    print("Looking for device...")
    while found_device is None or not found_device.is_connected:
        devices = await BleakScanner.discover()
        for device in devices:
            if device.address == hotoDeviceID:
                print("Found device:", device)
                found_device = BleakClient(device)
                await run_main_connection(found_device)
                print("Disconnected")
                found_device = None





asyncio.run(discover_and_connect())
