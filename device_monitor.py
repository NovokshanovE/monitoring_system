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
import multiprocessing
from logger import Logger
from network_device import NetworkDevice


running = True

class DeviceMonitor:
    def __init__(self, config_file):
        self.devices = []  # Список объектов NetworkDevice
        self.logger = None  # Создаем объект для записи логов
        self.load_config(config_file)
        self.run = True  # Метод для загрузки конфигурации из YAML файла
        self.pause_event = asyncio.Event()
        self.paused = False


    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config_data = yaml.load(file, Loader=yaml.FullLoader)

                # Загрузка данных о сетевых устройствах
                devices_data = config_data.get('devices', [])
                for device_data in devices_data:
                    device = NetworkDevice(device_data)
                    self.devices.append(device)

                # Загрузка настроек для логирования
                log_file = config_data.get('log_file', 'monitoring.log')
                self.logger = Logger(log_file)

                # Загрузка адреса электронной почты для уведомлений
                email = config_data.get('email', 'evgeny.novokshanov@gmail.com')

        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
        # Реализуйте метод для загрузки конфигурации из YAML файла
        # И создайте объекты NetworkDevice на основе данных из файла
    def device_thread(self, device):
        result = device.ping()
        self.logger.log(result)
        if 'failed' in result:
            device.count_fail += 1
        elif 'successful' in result:
            device.count_fail = 0
        if device.count_fail == device.ping_attempts:
            #print("TO EMAIL")
            device.count_fail = 0
            device.notify_admin()
            device.disconnect()
        return 

    def start_monitoring(self, queue):
        #print("\nStart monitoring...")
        # Метод для начала мониторинга устройств
        while True:
            if(not queue.empty()):
                    user_input = queue.get()   
                    if user_input == 'pause':
                        self.run = False
                    elif user_input == 'resume':
                        self.run = True
                    elif user_input == 'kill':
                        exit()
            for device in self.devices:
                res_connection = device.connect()
                res_setup = device.setup_ping()
                # if not res_connection or not res_setup:
                #     self.run = False
                #     device.count_fail += 1
                # elif res_connection and res_setup:
                #     device.count_fail = 0
                #     self.run = True
                # if device.count_fail == device.ping_attempts:
                #     #print("TO EMAIL")
                #     device.count_fail = 0
                #     device.notify_admin()
                #     device.disconnect()

            
                # global running
                # self.run = running
            if self.run == False:

                user_input = queue.get()   
                if user_input == 'pause':
                    self.run = False
                elif user_input == 'resume':
                    self.run = True
            while self.run:
                if(not queue.empty()):
                    user_input = queue.get()   
                    if user_input == 'pause':
                        self.run = False
                    elif user_input == 'resume':
                        self.run = True
                    elif user_input == 'kill':
                        exit()
                
                threads = []    
                for device in self.devices:
                    # device.connect()
                    # device.setup_ping()
                    d_thread = threading.Thread(target=self.device_thread, args=(device, ))
                    d_thread.start()
                    threads.append(d_thread)
                for thread in threads:
                    thread.join()
                
                    
            #print("Stop monitoring...")
