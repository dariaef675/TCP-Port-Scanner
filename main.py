import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

host = input("Пожалуйста, введите имя хоста или IP-адрес для сканирования: ")

try:
    host_ip = socket.gethostbyname(host)
except socket.gaierror:
    print(f"Имя хоста '{host}' не может быть разрешено. Выход.")
    sys.exit()

start_port = 1
end_port = 1024

print(f"Начинаем сканирование хоста {host} ({host_ip}) с порта {start_port} до {end_port}")


def scan_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host_ip, port))
    sock.close()
    if result == 0:
        return port
    else:
        return None


open_ports = []

try:
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_port = {executor.submit(scan_port, port): port for port in range(start_port, end_port + 1)}

        with tqdm(total=end_port - start_port + 1, desc="Сканирование портов") as pbar:
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result is not None:
                        open_ports.append(result)
                except KeyboardInterrupt:
                    print("\nСканирование прервано пользователем.")
                    sys.exit()
                except Exception as exc:
                    print(f"Порт {port} вызвал исключение: {exc}")
                finally:
                    pbar.update(1)
except KeyboardInterrupt:
    print("\nСканирование прервано пользователем.")
    sys.exit()
except socket.error as e:
    print(f"Ошибка сокета: {e}")
    sys.exit()

open_ports.sort()
if open_ports:
    print("Открытые порты:")
    for port in open_ports:
        print(f"Порт {port} открыт")
else:
    print("В указанном диапазоне не найдено открытых портов.")

print("Сканирование завершено.")