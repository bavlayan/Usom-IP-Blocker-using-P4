from typing import Container
import urllib.request
import re
import socket
import threading
import sys
import json
from colorama import Fore

from BlockedUrl import BlockedUrl
import Constants

class UsomUrlHelper:   
    def __init__(self):
        self.thread_count = 2
        self.blocked_url_list = []
        self.usom_url = Constants.USOM_URL

    def __get_blocked_urls_from_usom(self):
        try:
            response = urllib.request.urlopen(self.usom_url, timeout=3)
            for url in response:
                url_name = url.decode("utf-8").rstrip("\n")
                is_ip = self.__check_ip(url_name)
                if is_ip is True:
                    continue            
                blocked_url = BlockedUrl(url_name, '', False)
                self.blocked_url_list.append(blocked_url)
        except:
            print("Url not open")
            sys.exit()


    def __check_ip(self, url):
        ip_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        if(re.search(ip_regex, url)):
            return True
        return False
    
    def __set_ip(self):
        try:
            thread_arr = []
            loop_last_index = int(len(self.blocked_url_list) / self.thread_count)
            first_index = 0
            for i in range(self.thread_count):
                partial_blocked_list = self.blocked_url_list[first_index:loop_last_index]
                first_index = loop_last_index
                loop_last_index = loop_last_index * 2
                t = threading.Thread(target=self.__get_ip_from_url, args=(partial_blocked_list,))
                thread_arr.append(t)

            for t in thread_arr:
                t.start()

            for t in thread_arr:
                t.join()
        except:
            print("Getting error in set ip function")
    
    def __is_ip_private(self, ip):
        priv_lo = re.compile("^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_24 = re.compile("^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        priv_20 = re.compile("^192\.168\.\d{1,3}.\d{1,3}$")
        priv_16 = re.compile("^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$")
        res = priv_lo.match(ip) or priv_24.match(ip) or priv_20.match(ip) or priv_16.match(ip)
        return res is not None

    def __get_ip_from_url(self, blocked_url_list):        
        for blocked_url in blocked_url_list:
            try:
                ip_address = socket.gethostbyname(blocked_url.url_name)
                blocked_url.is_active = True

                if not ip_address:
                    print(Fore.YELLOW + blocked_url.url_name)
                    blocked_url.is_active = False
                    self.blocked_url_list.remove(blocked_url)

                if self.__is_ip_private(ip_address):
                    blocked_url.is_active = False
                    self.blocked_url_list.remove(blocked_url)   

                blocked_url.ip = ip_address                                    
                print(Fore.GREEN + "Url:" + blocked_url.url_name + " Ip:" + blocked_url.ip)                             
            except:
                blocked_url.is_active = False
                print(Fore.RED + "Url:" +blocked_url.url_name + " IP Address not found")
                self.blocked_url_list.remove(blocked_url)
                continue

    def create_json_file(self):
        self.__get_blocked_urls_from_usom()
        self.__set_ip()
        try:
            with open(Constants.BLOCKED_URL_JSON_FILE_NAME, 'w') as json_file:
                json.dump(self.blocked_url_list, json_file, default=vars)
                print(Fore.GREEN + "blocked_url.json file was created...")
        except:
            print(Fore.RED + "An error occured when creating " + Constants.BLOCKED_URL_JSON_FILE_NAME + " json file")


if __name__ == "__main__":
    usom_url_helper = UsomUrlHelper()
    usom_url_helper.create_json_file()