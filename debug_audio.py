import speech_recognition as sr
import sys

print("Starting audio debug...")
try:
    print("Listing devices...")
    devices = sr.Microphone.list_microphone_names()
    print(f"Found {len(devices)} devices")
    for i, name in enumerate(devices):
        print(f"{i}: {name}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("Done.")
