import serial
import serial.tools.list_ports
import threading
import os
import sys

program_name = "Console Serial monitor"
BPS = 4800

global_port = None
def find_arduino():
    global global_port
    
    ports = serial.tools.list_ports.comports()
    keywords = {"Arduino", "CH340", "FT232R", "USB SERIAL"}
    
    print("Serial device list")
    for index, port in enumerate(ports):
        print(f"{index+1}. {port.device} - {port.description}")

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
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        port = find_arduino()
        if not port:
            input("[Connection error] Device not found. Check your connection (press [Enter] to retry) . . .")
        else:
            break
    

    print(f"\nDevice found: {port.device}")

    try:
        ser = serial.Serial(port.device, BPS, timeout=1)
        print(f"Connected to the device: {port.device}")
        print('To terminate the program, either cause an [interloop] or type [!exit].')

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
                print("\nProgram terminated")
                os._exit(0)
            sys.stdout.write("\033[F")
            clear_line()
            print(f"User input: {user_input}")

            # user functions
            if user_input.lower() == "!exit":
                print("\nProgram terminated")
                os._exit(0)
            elif user_input.lower():
                os.system("cls" if os.name == "nt" else "clear")

            ser.write((user_input + "\n").encode('utf-8'))

    except Exception as e:
        print("\nFailed to connect to device. Check if other program is running . . . :", e)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

os.system("title " + program_name)
if __name__ == "__main__":
    main()
