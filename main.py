#! /usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from datetime import date
from optparse import OptionParser
from multiprocessing import Pool, Lock
from colorama import Fore, Back, Style
from time import strftime, localtime, time, sleep

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

lock = Lock()
thread_count = 1
headless_mode = True
delay_check = 1

def login(browser, target, username, password, delay=1):
    t1 = time()
    try:
        browser.get(f"http://{target}")
        while True:
            try:
                form = browser.find_element(By.TAG_NAME, "form")
                break
            except NoSuchElementException:
                sleep(delay)
            except Exception as error:
                t2 = time()
                return error, t2-t1
        url = browser.current_url
        input_tags = form.find_elements(By.TAG_NAME, "input")
        username_tag = input_tags[0]
        password_tag = input_tags[1]
        username_tag.send_keys(username)
        password_tag.send_keys(password)
        submit_buttons = form.find_elements(By.TAG_NAME, "button")
        for submit_button in submit_buttons:
            if "login" in submit_button.text.lower():
                submit_button.click()
        if browser.current_url == url:
            t2 = time()
            return False, t2-t1
        t2 = time()
        return True, t2-t1
    except Exception as error:
        t2 = time()
        return error, t2-t1
def loginHandler(thread_index, targets, credentials, delay=1, headless=True):
    successful_logins = {}
    options = Options()
    options.headless = True if headless else False
    browser = webdriver.Firefox(options=options)
    for username, password in credentials:
        for target in targets:
            status, time_taken = login(browser, target, username, password, delay)
            if status == True:
                successful_logins[target] = [username, password]
                with lock:
                    display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Back.MAGENTA}{Fore.BLUE}Authorized{Fore.RESET}{Back.RESET}")
            elif status == False:
                with lock:
                    display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Back.RED}{Fore.YELLOW}Access Denied{Fore.RESET}{Back.RESET}")
            else:
                with lock:
                    display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Fore.YELLOW}Error Occured : {Back.RED}{status}{Fore.RESET}{Back.RESET}")
    browser.close()
    return successful_logins

if __name__ == "__main__":
    arguments = get_arguments(('-t', "--target", "target", "Target Servers (Seperated by ',' or File Name)"),
                              ('-u', "--users", "users", "Target Users (seperated by ',') or File containing List of Users"),
                              ('-P', "--password", "password", "Passwords (seperated by ',') or File containing List of Passwords"),
                              ('-c', "--credentials", "credentials", "Name of File containing Credentials in format ({user}:{password})"),
                              ('-H', "--headless", "headless", f"Headless Mode (True/False, Default={headless_mode})"),
                              ('-d', "--delay", "delay", f"Delay Between checking of Form while Page Loading (Default={delay_check} seconds)"),
                              ('-T', "--threads", "threads", f"Number of Threads (Default={thread_count})"),
                              ('-w', "--write", "write", "CSV File to Dump Successful Logins (default=current data and time)"))
    if not arguments.target:
        display('-', f"Please specify {Back.YELLOW}Target Server{Back.RESET}")
        exit(0)
    else:
        try:
            with open(arguments.target, 'r') as file:
                arguments.targets = [target.strip() for target in file.read().split('\n') if target != '']
        except FileNotFoundError:
            arguments.target = arguments.target.split(',')
        except Exception as error:
            display('-', f"Error Occured while Reading File {Back.MAGENTA}{arguments.target}{Back.RESET} => {Back.YELLOW}{error}{Back.RESET}")
    if not arguments.credentials:
        if not arguments.users:
            display('-', f"Please specify {Back.YELLOW}Target Users{Back.RESET}")
            exit(0)
        else:
            try:
                with open(arguments.users, 'r') as file:
                    arguments.users = [user for user in file.read().split('\n') if user != '']
            except FileNotFoundError:
                arguments.users = arguments.users.split(',')
            except:
                display('-', f"Error while Reading File {Back.YELLOW}{arguments.users}{Back.RESET}")
                exit(0)
            display(':', f"Users Loaded = {Back.MAGENTA}{len(arguments.users)}{Back.RESET}")
        if not arguments.password:
            display('-', f"Please specify {Back.YELLOW}Passwords{Back.RESET}")
            exit(0)
        else:
            try:
                with open(arguments.password, 'r') as file:
                    arguments.password = [password for password in file.read().split('\n') if password != '']
            except FileNotFoundError:
                arguments.password = arguments.password.split(',')
            except:
                display('-', f"Error while Reading File {Back.YELLOW}{arguments.password}{Back.RESET}")
                exit(0)
            display(':', f"Passwords Loaded = {Back.MAGENTA}{len(arguments.password)}{Back.RESET}")
        arguments.credentials = []
        for user in arguments.users:
            for password in arguments.password:
                arguments.credentials.append([user, password])
    else:
        try:
            with open(arguments.credentials, 'r') as file:
                arguments.credentials = [[credential.split(':')[0], ':'.join(credential.split(':')[1:])] for credential in file.read().split('\n') if len(credential.split(':')) > 1]
        except:
            display('-', f"Error while Reading File {Back.YELLOW}{arguments.credentials}{Back.RESET}")
            exit(0)
    if arguments.headless == "True":
        arguments.headless = True
    else:
        arguments.headless = headless_mode
    if arguments.delay:
        arguments.delay = float(arguments.delay)
    else:
        arguments.delay = delay_check
    if arguments.threads:
        arguments.threads = int(arguments.threads)
    else:
        arguments.threads = thread_count
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.csv"
    total_servers = len(arguments.targets)
    display('+', f"Total Target Servers = {Back.MAGENTA}{total_servers}{Back.RESET}")
    display('+', f"Total Credentials    = {Back.MAGENTA}{len(arguments.credentials)}{Back.RESET}")
    t1 = time()
    successful_logins = {}
    pool = Pool(arguments.threads)
    server_divisions = [total_servers[group*total_servers//arguments.threads: (group+1)*total_servers//arguments.threads] for group in range(arguments.threads)]
    threads = []
    display(':', f"Staring {Back.MAGENTA}{arguments.threads}{Back.RESET} Threads")
    for index, server_division in enumerate(server_divisions):
        threads.append(pool.apply_async(loginHandler, (index, server_division, arguments.credentials, arguments.delay, arguments.headless)))
    for thread in threads:
        successful_logins.update(thread.get())
    pool.close()
    pool.join()
    t2 = time()
    display(':', f"Successful Logins = {Back.MAGENTA}{len(successful_logins)}{Back.RESET}")
    display(':', f"Total Credentials = {Back.MAGENTA}{len(arguments.credentials)}{Back.RESET}")
    display(':', f"Time Taken        = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
    display(':', f"Rate              = {Back.MAGENTA}{len(arguments.credentials)*total_servers/(t2-t1):.2f} logins / seconds{Back.RESET}")
    if len(successful_logins) > 0:
        display(':', f"Dumping Successful Logins to File {Back.MAGENTA}{arguments.write}{Back.RESET}")
        with open(arguments.write, 'w') as file:
            file.write(f"Server,Username,Password\n")
            file.write('\n'.join([f"{server},{username},{password}" for server, (username, password) in successful_logins.items()]))
        display('+', f"Dumped Successful Logins to File {Back.MAGENTA}{arguments.write}{Back.RESET}")