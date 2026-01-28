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

# ================== CONFIG & AUTH ==================
GITHUB_KEY_URL = "https://raw.githubusercontent.com/xmlcreator320-cpu/AKASH-FB/main/keys.txt"

stats = {"total": 0, "success": 0, "no_id": 0, "no_sms": 0, "error": 0}
lock = Lock()
log_count = 0
HEADLESS = False

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

# ================== PERMANENT KEY SYSTEM ==================
def check_key():
    key_storage = os.path.join(os.path.expanduser("~"), ".akash_id_permanent.txt")
    if os.path.exists(key_storage):
        with open(key_storage, "r") as f:
            user_key = f.read().strip()
    else:
        hwid = str(uuid.uuid4().hex[:6]).upper()
        user_key = f"AKASH-{hwid}"
        with open(key_storage, "w") as f:
            f.write(user_key)

    os.system("clear")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_key}")
    
    try:
        response = requests.get(f"{GITHUB_KEY_URL}?t={time.time()}", timeout=10)
        active_keys = response.text
        if user_key in active_keys:
            print(f"{Fore.WHITE} STATUS   : {Fore.GREEN}ACTIVE")
            print(Fore.CYAN + "=" * 60)
            return True
        else:
            print(f"{Fore.WHITE} STATUS   : {Fore.RED}NOT ACTIVE")
            print(Fore.CYAN + "=" * 60)
            input(f"{Fore.YELLOW} Press Enter to Exit...")
            return False
    except:
        print(f"{Fore.RED} [!] No Internet Connection!")
        return False

# ================== BANNER ==================
def banner():
    print(Fore.RED + Style.BRIGHT + r"""
  █████╗ ██╗  ██╗ █████╗ ███████╗██╗  ██╗
 ██╔══██╗██║ ██╔╝██╔══██╗██╔════╝██║  ██║
 ███████║█████╔╝ ███████║███████╗███████║
 ██╔══██║██╔═██╗ ██╔══██║╚════██║██╔══██║
 ██║  ██║██║  ██╗██║  ██║███████║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)
    print(Fore.MAGENTA + Style.BRIGHT + "        >>> FB REST TOOLS v2.0 PHONE CLONE <<<")
    print(Fore.CYAN + "=" * 60)

# ================== CHROME SETUP ==================
def setup_chrome(proxy=None):
    options = Options()
    if HEADLESS: options.add_argument("--headless=new")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if proxy: options.add_argument(f'--proxy-server={proxy}')

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

def process_number(any_number, proxy=None):
    driver = None
    try:
        driver = setup_chrome(proxy)
        driver.get("https://www.facebook.com/recover/initiate/")
        input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address or mobile number']")))
        input_field.send_keys(any_number)
        driver.find_element(By.XPATH, "//button[contains(text(),'Search')]").click()
        time.sleep(3)
        if "No search results" in driver.page_source:
            log_event(f"{any_number} : Invalid", Fore.RED)
        else:
            log_event(f"{any_number} : Found/Sent", Fore.GREEN)
            with lock: stats["success"] += 1
            with open("success_sent.txt", "a") as f: f.write(any_number + "\n")
    except: pass
    finally:
        if driver: driver.quit()

# ================== MAIN ==================
def main():
    if not check_key(): return
    banner()

    # অটোমেটিক ফাইল রিডার (সব ফোল্ডারে খুঁজবে)
    paths = ["numbers.txt", "number.txt", "/sdcard/number.txt", "/sdcard/numbers.txt"]
    numbers = []
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                numbers = [l.strip() for l in f if l.strip()]
            if numbers:
                print(f"{Fore.GREEN} [✓] LOADED {len(numbers)} NUMBERS FROM {p}")
                break

    if not numbers:
        print(Fore.RED + " [!] No numbers found!")
        return

    stats["total"] = len(numbers)
    
    # থ্রেড সংখ্যা টার্মাক্সের জন্য অপ্টিমাইজ করা
    print(Fore.YELLOW + " [!] Pro-Tip: Use 2-5 threads for Termux stability.")
    try:
        threads = int(input(Fore.WHITE + " Enter Threads (1-10): "))
    except: threads = 2

    global HEADLESS
    HEADLESS = input(" Headless Mode? (y/n): ").lower() == 'y'
    
    print(Fore.CYAN + "\n Starting...\n")
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            executor.submit(process_number, num)

    print(Fore.CYAN + "\n PROCESS COMPLETED")
    input(" Press Enter to Exit...")

if __name__ == "__main__":
    main()
