# ================== IMPORTS 1 ==================
import time
import random
import os
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

init(autoreset=True)

# ================== GITHUB CONFIG ==================
# এখানে আপনার GitHub-এর Raw ফাইল লিঙ্কটি দিন
ADMIN_KEY_URL = "https://raw.githubusercontent.com/xmlcreator320-cpu/AKASH-FB/main/keys.txt"

# ================== KEY SYSTEM ==================
# ইউজারের ডিভাইসে একটি স্থায়ী আইডি তৈরি করবে যা আর বদলাবে না
KEY_FILE = os.path.join(os.path.expanduser("~"), ".akash_permanent_key.txt")

def get_unique_id():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    else:
        new_id = "AKASH-" + str(uuid.uuid4().hex[:6]).upper()
        with open(KEY_FILE, "w") as f:
            f.write(new_id)
        return new_id

def check_key():
    user_id = get_unique_id()
    banner()
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_id}")
    print(f"{Fore.CYAN} STATUS   : {Fore.YELLOW}Checking Approval...")
    print(f"{Fore.WHITE}=" * 60)
    
    try:
        # ক্যাশিং এড়াতে টাইমস্ট্যাম্প সহ রিকোয়েস্ট
        response = requests.get(f"{ADMIN_KEY_URL}?t={time.time()}", timeout=10)
        if response.status_code == 200:
            if user_id in response.text:
                print(f"{Fore.GREEN} [✓] ACCESS GRANTED! WELCOME AKASH.")
                time.sleep(2)
                return True
            else:
                print(f"{Fore.RED} [×] STATUS: NOT ACTIVE")
                print(f"{Fore.WHITE} Contact Admin: @akash_bosss")
                input(f"\n{Fore.RED} Press Enter to Exit...")
                exit()
        else:
            print(f"{Fore.RED} [!] Server Error! Check Connection.")
            exit()
    except:
        print(f"{Fore.RED} [!] Error: Cannot connect to server.")
        exit()

# ================== GLOBALS 2 ==================
stats = {"total": 0, "success": 0, "no_id": 0, "no_sms": 0, "error": 0}
lock = Lock()
HEADLESS = True

# ================== BANNER 3 ==================
def banner():
    os.system("clear")
    print(Fore.RED + Style.BRIGHT + r"""
  █████╗ ██╗  ██╗ █████╗ ███████╗██╗  ██╗
 ██╔══██╗██║ ██╔╝██╔══██╗██╔════╝██║  ██║
 ███████║█████╔╝ ███████║███████╗███████║
 ██╔══██║██╔═██╗ ██╔══██║╚════██║██╔══██║
 ██║  ██║██║  ██╗██║  ██║███████║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)
    print(Fore.MAGENTA + "        >>> FB REST TOOLS v1.0 AKASH <<<")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + " Developer : AKASH | TELEGRAM : @akash_bosss")
    print(Fore.CYAN + "=" * 60)

# ================== SELENIUM SETUP (TERMUX FIXED) ==================
def setup_chrome():
    options = Options()
    options.add_argument("--headless=new") # টার্মাক্সে এটি অবশ্যই লাগবে
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # টার্মাক্সের জন্য সঠিক পাথ সেট করা হলো
    options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
    service = Service("/data/data/com.termux/files/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# ================== CORE PROCESS ==================
log_count = 0
def log_event(msg, color=Fore.WHITE):
    global log_count
    with lock:
        log_count += 1
        print(f"{color}[{log_count}] {msg}{Style.RESET_ALL}")

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
            with open("success_sent.txt", "a") as f:
                f.write(any_number + "\n")
        else:
            with lock: stats["error"] += 1
    except:
        with lock: stats["error"] += 1
    finally:
        if driver: driver.quit()

# ================== MAIN ==================
def main():
    check_key()
    
    if not os.path.exists("numbers.txt"):
        print(Fore.RED + "numbers.txt খুঁজে পাওয়া যায়নি!")
        return

    with open("numbers.txt", "r") as f:
        numbers = [n.strip() for n in f if n.strip()]
    
    stats["total"] = len(numbers)

    try:
        threads = int(input(Fore.WHITE + "Enter Threads (3-10): "))
        threads = max(1, min(threads, 10))
    except: threads = 3

    print(Fore.CYAN + f"\nStarting with {threads} threads...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            executor.submit(process_number, num)

    print(Fore.GREEN + "\nPROCESS COMPLETED")
    input("Press Enter to Exit...")

if __name__ == "__main__":
    main()
