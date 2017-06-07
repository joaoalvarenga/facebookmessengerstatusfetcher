# -*- coding: utf-8 -*-
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from datetime import datetime
from pymongo import MongoClient
from threading import Thread

debugging = False

def debug(msg):
    if debugging:
        print("DEBUG::{}".format(msg))

def parse_status(fid, status_msg):
    status_bool = status_msg.lower().find("online") == -1 # Depends on language
    on_messenger = None
    if status_bool:
        on_messenger = status_msg.lower().find("messenger") != -1
    return {"fid": fid, "status_msg": status_msg, "online": status_bool, "date": datetime.now(), "on_messenger": on_messenger}

class Fetcher(Thread):
    def __init__(self, fid, email, password):
        Thread.__init__(self)
        self.__fid = fid
        self.__email = email
        self.__password = password

    def log_in(self):
        debug("[{}][{}] Log in".format(datetime.now(), self.__fid))
        email_field = self.__browser.wait.until(EC.presence_of_element_located((By.NAME, "email")))
        password_field = self.__browser.find_element_by_name("pass")
        email_field.send_keys(self.__email)
        password_field.send_keys(self.__password)
        send_button = self.__browser.find_element_by_name("login")
        send_button.click()
        sleep(2)
        while self.__browser.execute_script('return document.readyState;') != "complete":
            sleep(0.5)

    def retrieve_messenger(self):
        try:
            self.__browser.get("https://www.facebook.com/messages/t/{}".format(self.__fid))
            name = self.__browser.wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='_3oh-']"))).text
            print("[{}][{}] Monitoring: {}".format(datetime.now(), self.__fid, name))
            return name
        except TimeoutException:
            # Some times it doesn't have enough time to log in, this is very common in poor connections
            debug("[{}][{}] Retrying to retrieve Messenger".format(datetime.now(), self.__fid))
            self.log_in()
            return self.retrieve_messenger()


    def run(self):
        collection = MongoClient().local['fb_messenger_fetcher']

        self.__browser = webdriver.PhantomJS()
        self.__browser.wait = WebDriverWait(self.__browser, 10)
        self.__browser.get("https://facebook.com")
        debug("[{}][{}] Retrieving facebook".format(datetime.now(), self.__fid))

        self.log_in()
        

        debug("[{}][{}] Retrieving Messenger".format(datetime.now(), self.__fid))
        name = self.retrieve_messenger()

        status = self.__browser.wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='_2v6o']")))
        current_status = status.text

        last_status = collection.find_one({'fid': self.__fid})
        if last_status == None or (last_status['online'] != parse_status(self.__fid, current_status)['online']):
            collection.insert(parse_status(self.__fid, current_status))


        print("[{}][{}] Current status: {}".format(str(datetime.now()), self.__fid, current_status))
        while True:
            status = self.__browser.find_element_by_xpath("//span[@class='_2v6o']")
            if current_status != status.text:
                if(parse_status(self.__fid,status.text)['online'] != parse_status(self.__fid, current_status)['online']):
                    debug("[{}][{}] Inserting new register on db".format(datetime.now(), self.__fid))
                    collection.insert(parse_status(self.__fid, status.text))
                    if parse_status(self.__fid, status.text)['online']:
                        print("[{}][{}] {} is now online.".format(datetime.now(), self.__fid, name))
                    else:
                        print("[{}][{}] {} is now offline.".format(datetime.now(), self.__fid, name))
                current_status = status.text
                print("[{}][{}] New status: {}".format(str(datetime.now()), self.__fid, current_status))
            sleep(0.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Messenger Status Fetcher")
    parser.add_argument('--id', action='store', dest='fid', required=True,
                           help='File containing list fids(per line)')
    parser.add_argument('--email', action='store', dest='email', required=True,
                           help='Facebook login email')
    parser.add_argument('--password', action='store', dest='password',
                           required=True, help='Facebook login password')
    parser.add_argument('-d', action='store_true', dest='debug', default=False, help='Debug')
    arguments = parser.parse_args()

    debugging = arguments.debug

    email = arguments.email
    password = arguments.password

    fetchers = []
    with open(arguments.fid) as f:
        for fid in f.read().strip().split("\n"):
            if len(fid) > 1:
                fetcher = Fetcher(fid, email, password)
                print("[{}][CONTROLLER] Starting fetcher for {}".format(str(datetime.now()), fid))
                fetcher.start()
                fetchers.append(fetcher)

    for f in fetchers:
        f.join()
    