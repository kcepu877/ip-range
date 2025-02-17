import socket
import requests
import concurrent.futures
import random

# Daftar IP Range Indonesia (contoh)
ip_ranges = [
    "36.66.0.0/16", "103.89.0.0/22", "114.4.0.0/14", "182.253.0.0/16"
]

# Fungsi untuk mengecek apakah port terbuka
def check_proxy(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        return result == 0

# Fungsi untuk mendapatkan ISP dari IP
def get_isp(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json").json()
        return response.get("org", "Unknown")
    except:
        return "Unknown"

# Fungsi utama untuk mengecek IP dalam rentang tertentu
def scan_ip_range(ip_range):
    from ipaddress import ip_network
    
    active_proxies = []
    for ip in ip_network(ip_range).hosts():
        ip = str(ip)
        ports_to_check = random.sample(range(1, 65535), 10)  # Pilih 10 port acak
        for port in ports_to_check:
            if check_proxy(ip, port):
                isp = get_isp(ip)
                active_proxies.append(f"{ip},{port},ID,{isp}")
                print(f"[FOUND] {ip}:{port} - {isp}")
    return active_proxies

# Multi-threading untuk scan lebih cepat
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(scan_ip_range, ip_range) for ip_range in ip_ranges]
    for future in concurrent.futures.as_completed(futures):
        results.extend(future.result())

# Simpan hasil ke file
with open("active_proxies.csv", "w") as file:
    file.write("ip,port,id,isp\n")
    file.write("\n".join(results))

print("Scanning selesai. Hasil disimpan di active_proxies.csv")
