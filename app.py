import serial
import serial.tools.list_ports
import threading
import os
import sys

BPS = 4800
global_port = None

def find_arduino():
    global global_port
    
    ports = serial.tools.list_ports.comports()
    keywords = {"Arduino", "CH340", "FT232R", "USB SERIAL"}
    
    global_port = next((port for port in ports if any(keyword.lower() in port.description.lower() for keyword in keywords)), None)
    
    return global_port

def clear_line():
    sys.stdout.write("\033[K")
    sys.stdout.flush()

def read_from_arduino(ser):
    while True:
        try:
            raw_data = ser.readline()
            data = raw_data.decode('utf-8', errors='ignore').rstrip("\r\n")
            
            if data:
                sys.stdout.write(f"\033[F")
                clear_line()
                print(data)
                print("-" * 50)
                print(f"{global_port.description} >", end=" ", flush=True)

        except Exception as e:
            print(f"\n[Connection error] {e}")
            os._exit(1)

def main():
    while True:
        port = find_arduino()
        if not port:
            input("[Connection error] Device not found. Check your connection(Press [Enter] to retry) . . .")
        else:
            break
    
    os.system("cls" if os.name == "nt" else "clear")

    print(f"\nDevice found: {port.device}")

    try:
        ser = serial.Serial(port.device, BPS, timeout=1)
        print(f"Connected to the device: {port.device}")
        print('To exit the program, either cause an [interrupt] or type [!exit].')

        if ser.in_waiting:
            first_data = ser.readline().decode('utf-8', errors='ignore').rstrip("\r\n")
            if first_data:
                print(first_data)
        
        threading.Thread(target=read_from_arduino, args=(ser,), daemon=True).start()

        print("-" * 50)

        while True:
            sys.stdout.write(f"{port.description} > ")
            sys.stdout.flush()
            try:
                user_input = input().strip()
            except KeyboardInterrupt:
                print("\nProgram terminated.")
                os._exit(0)
            sys.stdout.write("\033[F")
            clear_line()
            print(f"Your input: {user_input}")

            if user_input.lower() == "!exit":
                print("\nProgram terminated.")
                os._exit(0)
            ser.write((user_input + "\n").encode('utf-8'))

    except Exception as e:
        print("\nFailed to connect to device. Make sure it is not open in another program . . . :", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
