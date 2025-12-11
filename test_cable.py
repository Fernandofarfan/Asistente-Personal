import speech_recognition as sr
import time

print("--- DIAGNÓSTICO DE AUDIO ---")
print("Listando dispositivos...")

try:
    devices = sr.Microphone.list_microphone_names()
    cable_indices = []
    
    for i, name in enumerate(devices):
        if "CABLE Output" in name:
            print(f"  [ENCONTRADO] Índice {i}: {name}")
            cable_indices.append(i)
            
    if not cable_indices:
        print("\n❌ ERROR: No se encontró 'CABLE Output'. Reinstala VB-Cable.")
    else:
        print(f"\n✅ Se encontraron {len(cable_indices)} dispositivos de cable.")
        print("Reproduce un video de YouTube AHORA MISMO para probar el sonido.")
        
        for idx in cable_indices:
            print(f"\n🎧 Probando dispositivo {idx}...")
            r = sr.Recognizer()
            try:
                with sr.Microphone(device_index=idx) as source:
                    print("   Ajustando ruido (espera)...")
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    print("   👂 ESCUCHANDO (3 segundos)...")
                    try:
                        audio = r.listen(source, timeout=3, phrase_time_limit=3)
                        print("   ✅ ¡SONIDO DETECTADO!")
                        try:
                            text = r.recognize_google(audio, language="es-ES")
                            print(f"   📝 Transcripción: '{text}'")
                        except:
                            print("   ⚠️ Se escuchó sonido pero no se pudo transcribir (¿Música?).")
                    except sr.WaitTimeoutError:
                        print("   ❌ SILENCIO TOTAL (No llega audio al cable).")
            except Exception as e:
                print(f"   ❌ Error técnico: {e}")

except Exception as e:
    print(f"Error crítico: {e}")

input("\nPresiona ENTER para salir...")
