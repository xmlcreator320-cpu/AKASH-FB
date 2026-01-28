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
# আপনার GitHub Raw URL এখানে দিন যেখানে আপনি অনুমোদিত Key গুলো রাখবেন
GITHUB_KEY_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/keys.txt"

stats = {"total": 0, "success": 0, "no_id": 0, "no_sms": 0, "error": 0}
lock = Lock()
log_count = 0
HEADLESS = False

# বাস্তবসম্মত ব্রাউজার লিস্ট (Randomly used for stealth)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

# ================== LICENSE SYSTEM ==================
def check_key():
    hwid = str(uuid.getnode())
    user_key = f"AKASH-{hwid[:6]}" # ইউজারের জন্য ইউনিক কি
    os.system("cls" if os.name == "nt" else "clear")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.WHITE} YOUR KEY : {Fore.YELLOW}{user_key}")
    print(f"{Fore.WHITE} STATUS   : {Fore.RED}NOT ACTIVE")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.GREEN} Message  : Contact Admin To Activate Key")
    print(f"{Fore.GREEN} Telegram : @akash_bosss")
    print(Fore.CYAN + "=" * 60)
    
    try:
        # গিটহাব থেকে কি চেক করা
        active_keys = requests.get(GITHUB_KEY_URL).text
        if user_key in active_keys:
            print(f"{Fore.GREEN} [✓] KEY ACTIVATED SUCCESSFULLY!")
            time.sleep(2)
            return True
        else:
            input(f"{Fore.YELLOW} Press Enter to Exit...")
            return False
    except:
        print(f"{Fore.RED} [!] Check your internet connection!")
        return False

# ================== BANNER ==================
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

    # PC vs Termux detection
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

# ================== PROCESS NUMBER (Original Logic) ==================
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

        # Logic for "This is my account"
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
                # SMS Trigger
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

    except Exception as e:
        with lock: stats["error"] += 1
    finally:
        if driver: driver.quit()

# ================== MAIN ==================
def main():
    if not check_key(): return
    banner()

    if not os.path.exists("numbers.txt"):
        print(Fore.RED + "numbers.txt not found!")
        return

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

    print(Fore.CYAN + "\nStarting...\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for num in numbers:
            p = random.choice(proxies) if use_proxy and proxies else None
            executor.submit(process_number, num, p)

    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.GREEN + " PROCESS COMPLETED")
    print(Fore.CYAN + "="*60)
    input("Press Enter to Exit...")

if __name__ == "__main__":
    main()
