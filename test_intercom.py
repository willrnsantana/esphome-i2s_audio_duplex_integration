#!/usr/bin/env python3
"""
Intercom API Test Script
Tests all call scenarios systematically.
"""
import asyncio
import aiohttp
import json
import sys

HA_URL = "ws://192.168.1.10:8123/api/websocket"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlMTc5YzQ2ZmVkOGM0ZjU1OTQyOWRkNDg1OTI4ZDk2MiIsImlhdCI6MTc2ODQ5MTE3NywiZXhwIjoyMDgzODUxMTc3fQ.W6iHGkX1rLKNkmVjZgeTukWRUuBSqIupU2L1VYEOgWY"

XIAOZHI_IP = "192.168.1.31"
MINI_IP = "192.168.1.18"

msg_id = 1

async def send_ws(ws, msg_type, **kwargs):
    global msg_id
    msg = {"id": msg_id, "type": msg_type, **kwargs}
    msg_id += 1
    await ws.send_json(msg)
    return msg["id"]

async def recv_result(ws, expected_id, timeout=5):
    """Wait for result with specific ID"""
    try:
        async with asyncio.timeout(timeout):
            while True:
                msg = await ws.receive_json()
                if msg.get("id") == expected_id:
                    return msg
                # Print other messages for debugging
                if msg.get("type") not in ["auth_required", "auth_ok", "event"]:
                    print(f"  [Other msg] {msg.get('type', 'unknown')}: {msg}")
    except asyncio.TimeoutError:
        return {"error": "timeout"}

async def connect_ha():
    """Connect to HA WebSocket"""
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(HA_URL)

    # Wait for auth_required
    msg = await ws.receive_json()
    assert msg["type"] == "auth_required"

    # Send auth
    await ws.send_json({"type": "auth", "access_token": HA_TOKEN})

    # Wait for auth_ok
    msg = await ws.receive_json()
    if msg["type"] != "auth_ok":
        raise Exception(f"Auth failed: {msg}")

    print("✓ Connected to HA")
    return session, ws

async def list_devices(ws):
    """List available intercom devices"""
    mid = await send_ws(ws, "intercom_native/list_devices")
    result = await recv_result(ws, mid)
    if "result" in result:
        return result["result"].get("devices", [])
    return []

async def test_start(ws, device_id, host):
    """Test: Card starts call to ESP"""
    print(f"\n--- TEST: Card -> ESP (start) ---")
    print(f"  Device: {device_id}, Host: {host}")

    mid = await send_ws(ws, "intercom_native/start", device_id=device_id, host=host)
    result = await recv_result(ws, mid, timeout=10)

    if "result" in result:
        print(f"  ✓ Result: {result['result']}")
        return result["result"]
    else:
        print(f"  ✗ Error: {result}")
        return None

async def test_stop(ws, device_id):
    """Test: Stop call"""
    print(f"\n--- TEST: Stop call ---")
    mid = await send_ws(ws, "intercom_native/stop", device_id=device_id)
    result = await recv_result(ws, mid)
    print(f"  Result: {result.get('result', result)}")

async def test_answer(ws, device_id):
    """Test: Answer ringing call"""
    print(f"\n--- TEST: Answer (for ringing ESP) ---")
    mid = await send_ws(ws, "intercom_native/answer", device_id=device_id)
    result = await recv_result(ws, mid)
    if "result" in result:
        print(f"  ✓ Result: {result['result']}")
    else:
        print(f"  ✗ Error: {result}")
    return result

async def test_answer_esp_call(ws, device_id, host):
    """Test: Answer ESP-initiated call to HA"""
    print(f"\n--- TEST: Answer ESP call (ESP->HA) ---")
    mid = await send_ws(ws, "intercom_native/answer_esp_call", device_id=device_id, host=host)
    result = await recv_result(ws, mid, timeout=10)
    if "result" in result:
        print(f"  ✓ Result: {result['result']}")
    else:
        print(f"  ✗ Error: {result}")
    return result

async def test_decline(ws, device_id):
    """Test: Decline call"""
    print(f"\n--- TEST: Decline ---")
    mid = await send_ws(ws, "intercom_native/decline", device_id=device_id)
    result = await recv_result(ws, mid)
    print(f"  Result: {result.get('result', result)}")
    return result

async def test_bridge(ws, source_id, source_host, source_name, dest_id, dest_host, dest_name):
    """Test: Bridge between two ESPs"""
    print(f"\n--- TEST: Bridge {source_name} -> {dest_name} ---")
    mid = await send_ws(ws, "intercom_native/bridge",
        source_device_id=source_id,
        source_host=source_host,
        source_name=source_name,
        dest_device_id=dest_id,
        dest_host=dest_host,
        dest_name=dest_name,
    )
    result = await recv_result(ws, mid, timeout=10)
    if "result" in result:
        print(f"  ✓ Result: {result['result']}")
    else:
        print(f"  ✗ Error: {result}")
    return result

async def main():
    print("=" * 60)
    print("INTERCOM API TEST")
    print("=" * 60)

    session, ws = await connect_ha()

    try:
        # List devices
        print("\n--- Listing devices ---")
        devices = await list_devices(ws)
        for d in devices:
            print(f"  {d['name']}: {d['host']} ({d['device_id'][:8]}...)")

        if len(devices) < 2:
            print("ERROR: Need at least 2 devices")
            return

        # Find Xiaozhi and Mini
        xiaozhi = next((d for d in devices if "xiaozhi" in d['name'].lower()), None)
        mini = next((d for d in devices if "mini" in d['name'].lower()), None)

        if not xiaozhi or not mini:
            print("ERROR: Could not find Xiaozhi and Mini")
            print(f"  Found: {[d['name'] for d in devices]}")
            return

        print(f"\n  Xiaozhi: {xiaozhi['host']} ({xiaozhi['device_id'][:8]})")
        print(f"  Mini: {mini['host']} ({mini['device_id'][:8]})")

        # Test menu
        while True:
            print("\n" + "=" * 60)
            print("TEST MENU:")
            print("  1. Card -> Xiaozhi (start)")
            print("  2. Card -> Mini (start)")
            print("  3. Answer (for ringing ESP)")
            print("  4. Answer ESP call (ESP->HA)")
            print("  5. Decline")
            print("  6. Stop")
            print("  7. Bridge: Xiaozhi -> Mini")
            print("  8. Bridge: Mini -> Xiaozhi")
            print("  9. List devices")
            print("  0. Exit")
            print("=" * 60)

            choice = input("Choice: ").strip()

            if choice == "1":
                await test_start(ws, xiaozhi['device_id'], xiaozhi['host'])
            elif choice == "2":
                await test_start(ws, mini['device_id'], mini['host'])
            elif choice == "3":
                device = input("  Which device (x=xiaozhi, m=mini)? ").strip().lower()
                d = xiaozhi if device == "x" else mini
                await test_answer(ws, d['device_id'])
            elif choice == "4":
                device = input("  Which device called HA (x=xiaozhi, m=mini)? ").strip().lower()
                d = xiaozhi if device == "x" else mini
                await test_answer_esp_call(ws, d['device_id'], d['host'])
            elif choice == "5":
                device = input("  Which device (x=xiaozhi, m=mini)? ").strip().lower()
                d = xiaozhi if device == "x" else mini
                await test_decline(ws, d['device_id'])
            elif choice == "6":
                device = input("  Which device (x=xiaozhi, m=mini)? ").strip().lower()
                d = xiaozhi if device == "x" else mini
                await test_stop(ws, d['device_id'])
            elif choice == "7":
                await test_bridge(ws,
                    xiaozhi['device_id'], xiaozhi['host'], xiaozhi['name'],
                    mini['device_id'], mini['host'], mini['name'])
            elif choice == "8":
                await test_bridge(ws,
                    mini['device_id'], mini['host'], mini['name'],
                    xiaozhi['device_id'], xiaozhi['host'], xiaozhi['name'])
            elif choice == "9":
                devices = await list_devices(ws)
                for d in devices:
                    print(f"  {d['name']}: {d['host']}")
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    finally:
        await ws.close()
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
