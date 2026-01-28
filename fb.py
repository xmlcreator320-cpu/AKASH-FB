import time
import random
import os
import requests
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

init(autoreset=True)

# ================== CONFIG & KEY SYSTEM ==================
GITHUB_KEY_URL = "https://raw.githubusercontent.com/xmlcreator320-cpu/AKASH-FB/main/keys.txt"

stats = {"total": 0, "success": 0, "no_id": 0, "no_sms": 0, "error": 0}
lock = Lock()
log_count = 0
HEADLESS = True
SELECTED_PROXY = None

# ================== PERMANENT KEY ==================
def check_key():
    key_file = os.path.join(os.path.expanduser("~"), ".ng_sport_key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r") as f: user_key = f.read().strip()
    else:
        user_key = f"NG-{uuid.uuid4().hex[:6].upper()}"
        with open(key_file, "w") as f: f.write(user_key)

    os.system("clear")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_key}")
    try:
        active_keys = requests.get(f"{GITHUB_KEY_URL}?t={time.time()}", timeout=10).text
        if user_key in active_keys:
            print(f"{Fore.WHITE} STATUS   : {Fore.GREEN}ACTIVE")
            return True
        else:
            print(f"{Fore.WHITE} STATUS   : {Fore.RED}NOT ACTIVE")
            print(Fore.GREEN + " Contact Admin: @ng_sport_helpline")
            input(" Press Enter to Exit...")
            return False
    except: return True # Offline backup

# ================== BANNER ==================
def banner():
    os.system("clear")
    print(Fore.RED + Style.BRIGHT + r"""
 ███╗   ██╗ ██████╗       ███████╗██████╗  ██████╗ ██████╗ ████████╗
 ████╗  ██║██╔════╝       ██╔════╝██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
 ██╔██╗ ██║██║  ███╗      ███████╗██████╔╝██║   ██║██████╔╝   ██║
 ██║╚██╗██║██║   ██║      ╚════██║██╔═══╝ ██║   ██║██╔══██╗   ██║
 ██║ ╚████║╚██████╔╝      ███████║██║     ╚██████╔╝██║  ██║   ██║
 ╚═╝  ╚═══╝ ╚═════╝       ╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝
    """)
    print(Fore.MAGENTA + Style.BRIGHT + "        >>> FB REST TOOLS v1.0 PHONE CLONE <<<")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + " Developer : NG_SPORT | TELEGRAM : @ng_sport_helpline")
    print(Fore.CYAN + "=" * 60)

# ================== SELENIUM SETUP ==================
def setup_chrome():
    options = Options()
    if HEADLESS: options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if SELECTED_PROXY:
        options.add_argument(f'--proxy-server={SELECTED_PROXY}')

    if os.name == "nt" or (os.name == "posix" and not os.path.exists("/data/data/com.termux")):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
        driver = webdriver.Chrome(service=Service("/data/data/com.termux/files/usr/bin/chromedriver"), options=options)
    return driver

def log_event(msg, color=Fore.WHITE):
    global log_count
    with lock:
        log_count += 1
        print(f"{color}[{log_count}] {msg}{Style.RESET_ALL}")

# ================== CORE PROCESS (YOUR ORIGINAL LOGIC) ==================
def process_number(any_number):
    driver = None
    try:
        driver = setup_chrome()
        driver.get("https://www.facebook.com/recover/initiate/")

        input_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address or mobile number']"))
        )
        input_field.send_keys(any_number)
        driver.find_element(By.XPATH, "//button[contains(text(),'Search')]").click()
        time.sleep(3)

        page_text = driver.page_source
        if "No search results" in page_text:
            log_event(f"{any_number} : Invalid Account", Fore.RED)
            with lock: stats["no_id"] += 1
        elif any(x in page_text for x in ["Send code via SMS", "Try another way", "This is my account"]):
            log_event(f"{any_number} : Success Found", Fore.GREEN)
            with lock: stats["success"] += 1
            with open("success_sent.txt", "a") as f: f.write(any_number + "\n")
        else:
            log_event(f"{any_number} : Unknown Result", Fore.YELLOW)
            with lock: stats["error"] += 1

    except:
        with lock: stats["error"] += 1
    finally:
        if driver: driver.quit()

# ================== PROXY HANDLER ==================
def get_proxy_choice():
    global SELECTED_PROXY
    choice = input(Fore.WHITE + " Use Proxy? (y/n): ").lower()
    if choice == 'y':
        print(Fore.YELLOW + " 1. Manual Entry\n 2. Use proxy.txt")
        p_type = input(" Select: ")
        if p_type == '1':
            SELECTED_PROXY = input(" Enter Proxy (IP:PORT): ")
        else:
            if os.path.exists("proxy.txt"):
                proxies = open("proxy.txt").read().splitlines()
                SELECTED_PROXY = random.choice(proxies)
                print(Fore.GREEN + f" [✓] Random Proxy Loaded: {SELECTED_PROXY}")
            else:
                print(Fore.RED + " proxy.txt not found!")

# ================== MAIN ==================
def main():
    if not check_key(): return
    banner()
    
    file_path = "numbers.txt"
    if not os.path.exists(file_path):
        if os.path.exists("/sdcard/number.txt"): file_path = "/sdcard/number.txt"
        else: print("File numbers.txt not found!"); return

    numbers = open(file_path, "r").read().splitlines()
    numbers = [n.strip() for n in numbers if n.strip()]
    stats["total"] = len(numbers)

    get_proxy_choice()
    
    try:
        threads = int(input(Fore.WHITE + " Enter Threads (1-30): "))
    except: threads = 5

    global HEADLESS
    HEADLESS = input(" Headless Mode? (y/n): ").lower() == 'y'

    print(Fore.CYAN + f"\n Starting with {threads} threads...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            executor.submit(process_number, num)

    print(Fore.GREEN + f"\n PROCESS COMPLETED. SUCCESS: {stats['success']}")
    input(" Press Enter to Exit...")

if __name__ == "__main__":
    main()
