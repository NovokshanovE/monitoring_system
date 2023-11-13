
import datetime
import queue
from ping3 import ping, verbose_ping
import paramiko
import yaml
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from icmplib import *
import asyncio
import threading
from multiprocessing import Process, Pipe, Queue
import aioconsole
import multiprocessing
from device_monitor import DeviceMonitor

from logger import Logger

message_queue = queue.Queue()


def input_process(queue):
    while True:
        user_input = input()
        queue.put(user_input)
        if(user_input == 'kill'):
            exit()
        
def input_thread():
    while True:
        user_input = input("Список команд: help или ?\nВведите  команду: ")
        message_queue.put(user_input) # Помещаем сообщение в очередь
        if(user_input == 'kill'):
            exit()  
        elif(user_input == 'help' or user_input == '?'):
            print("Commands:\n\tpause : система приостанавливает свою работу\
                  \n\tresume : система возобновляет свою работу\
                  \n\tkill : система завршает свою работу\n")

def main(queue):
    config_file = "settings.yaml"
    try:

        monitor = DeviceMonitor(config_file)

        
        monitor.start_monitoring(queue)


    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    input_thread = threading.Thread(target=input_thread)
    input_thread.start()
    
    main(message_queue)
    input_thread.join()
