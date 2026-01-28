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
# আপনার GitHub Raw URL নিশ্চিত করুন
GITHUB_KEY_URL = "https://raw.githubusercontent.com/xmlcreator320-cpu/AKASH-FB/main/keys.txt"

stats = {"total": 0, "success": 0, "no_id": 0, "no_sms": 0, "error": 0}
lock = Lock()
log_count = 0
HEADLESS = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

# ================== PERMANENT KEY SYSTEM ==================
def check_key():
    # টার্মাক্স হোম ডিরেক্টরিতে কি (Key) সেভ করে রাখবে
    key_storage = os.path.join(os.path.expanduser("~"), ".akash_id_permanent.txt")
    
    if os.path.exists(key_storage):
        with open(key_storage, "r") as f:
            user_key = f.read().strip()
    else:
        # প্রথমবার রান করলে একটি ইউনিক আইডি তৈরি করবে যা আর বদলাবে না
        hwid = str(uuid.uuid4().hex[:6]).upper()
        user_key = f"AKASH-{hwid}"
        with open(key_storage, "w") as f:
            f.write(user_key)

    os.system("clear")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_key}")
    
    try:
        # Fresh key check from GitHub
        response = requests.get(f"{GITHUB_KEY_URL}?t={time.time()}", timeout=10)
        active_keys = response.text
        
        if user_key in active_keys:
            print(f"{Fore.WHITE} STATUS   : {Fore.GREEN}ACTIVE")
            print(Fore.CYAN + "=" * 60)
            return True
        else:
            print(f"{Fore.WHITE} STATUS   : {Fore.RED}NOT ACTIVE")
            print(Fore.CYAN + "=" * 60)
            print(f"{Fore.GREEN} Message  : Contact Admin To Activate Key")
            print(f"{Fore.GREEN} Telegram : @akash_bosss")
            input(f"{Fore.YELLOW} Press Enter to Exit...")
            return False
    except:
        print(f"{Fore.RED} [!] Check your internet connection!")
        time.sleep(3)
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
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

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

# ================== PROCESS LOGIC ==================
def process_number(any_number, proxy=None):
    driver = None
    try:
        driver = setup_chrome(proxy)
        driver.get("https://www.facebook.com/recover/initiate/")
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address or mobile number']"))
        )
        input_field.send_keys(any_number)
        driver.find_element(By.XPATH, "//button[contains(text(),'Search')]").click()
        time.sleep(3)
        
        page_text = driver.page_source
        if "No search results" in page_text:
            log_event(f"{any_number} : Invalid Account", Fore.RED)
            with lock: stats["no_id"] += 1
        elif "Send code via SMS" in page_text or "Try another way" in page_text:
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

# ================== MAIN ==================
def main():
    if not check_key(): return
    banner()

    # ফাইল খোঁজার সঠিক এবং অটোমেটিক সিস্টেম
    paths_to_check = ["numbers.txt", "/sdcard/number.txt", "/sdcard/numbers.txt"]
    numbers = []
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    numbers = [line.strip() for line in f if line.strip()]
                if numbers:
                    print(f"{Fore.GREEN} [✓] SUCCESSFULLY LOADED {len(numbers)} NUMBERS FROM: {path}")
                    break
            except: continue

    if not numbers:
        print(Fore.RED + " [!] ERROR: No numbers found! Please create 'number.txt' in SD Card.")
        return

    stats["total"] = len(numbers)
    print(Fore.CYAN + "=" * 60)
    
    try:
        threads = int(input(Fore.WHITE + " Enter Threads (1-15): "))
    except: threads = 3

    global HEADLESS
    HEADLESS = input(" Headless Mode? (y/n): ").lower() == 'y'
    
    print(Fore.CYAN + "\n Starting Process...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            executor.submit(process_number, num, None)

    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.GREEN + f" PROCESS COMPLETED. TOTAL SUCCESS: {stats['success']}")
    input(" Press Enter to Exit...")

if __name__ == "__main__":
    main()
