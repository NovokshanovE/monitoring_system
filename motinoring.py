
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
#import asyncssh
import aioconsole

running = True


class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as file:
            file.write(f"{timestamp}: {message}\n")


class DeviceMonitor:
    def __init__(self, config_file):
        self.devices = []  # Список объектов NetworkDevice
        self.logger = None  # Создаем объект для записи логов
        self.load_config(config_file)
        self.run = True  # Метод для загрузки конфигурации из YAML файла
        self.pause_event = asyncio.Event()
        self.paused = False

    async def monitor_devices(self):
        while True:
            if not self.paused:
                # Выполняйте мониторинг сетевых устройств
                print("Мониторинг запущен...")
                self.run = True
                await self.start_monitoring()  # Здесь можно заменить на вашу логику мониторинга
            else:
                print("Мониторинг на паузе...")
                self.run = False

    def pause_monitoring(self):
        self.paused = True

    def resume_monitoring(self):
        self.paused = False
        self.pause_event.set()

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

    def start_monitoring(self):
        print("Start monitoring...")
        # Метод для начала мониторинга устройств
        for device in self.devices:
            device.connect()
            device.setup_ping()
        
            # global running
            # self.run = running
            
        while self.run:
            
                
            for device in self.devices:
                # device.connect()
                # device.setup_ping()
                result = device.ping()
                self.logger.log(result)
                if 'failed' in result:
                    device.count_fail += 1
                if device.count_fail >= device.ping_attempts:
                    print("TO EMAIL")
                    device.count_fail = 0
                    device.notify_admin()
                    device.disconnect()
        print("Stop monitoring...")




class NetworkDevice:
    def __init__(self, data):
        self.ip_address = data['ip_address']
        self.username = data['username']
        self.password = data['password']
        self.log_file = data['log_file']
        self.email = data['email']
        self.ping_attempts = data['ping_attempts']
        self.count_fail = 0

    def connect(self):
        # Метод для подключения к устройству (SSH, Telnet, и т.д.)
        # print(self.username)
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.ip_address, username=self.username, password=self.password)
            return True  # Успешное подключение
        except Exception as e:
            print(f"Error connecting to {self.ip_address}: {str(e)}")
            return False  # Не удалось подключиться

    def setup_ping(self):
        # Метод для настройки устройства для доступности по ICMP пингу
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.ip_address, username=self.username, password=self.password)

            ssh_shell = ssh_client.invoke_shell()
            ssh_shell.send("enable\n")  # Если требуется ввод пароля для привилегированного режима
            ssh_shell.send("configure terminal\n")
            ssh_shell.send(f"ip icmp rate-limit unreachable {self.ping_attempts} 10\n")  # Настройка ICMP rate-limit
            ssh_shell.send("end\n")
            ssh_shell.send("write memory\n")  # Сохранение конфигурации

            # Подождите несколько секунд, чтобы убедиться, что команды выполнились успешно
            time.sleep(5)

            ssh_shell.close()
            ssh_client.close()

            return True  # Успешно настроено
        except Exception as e:
            print(f"Error setting up ping for {self.ip_address}: {str(e)}")
            return False  # Не удалось настроить

    def ping(self):
        # Метод для отправки ICMP пингов и возвращения результатов
        result = self.icmp_ping(timeout=1, count=4)
        #print(result)  # Пингуем устройство 4 раза с таймаутом 1 секунда
        if result:
            return f"Ping to {self.ip_address} successful."
            
        else:
            return f"Ping to {self.ip_address} failed."
    def icmp_ping(self, count=4, interval=1, timeout=2, id=PID):
        #print(f'PING {self.ip_address}: 56 data bytes\n')
        if is_ipv6_address(self.ip_address):
            sock = ICMPv6Socket()
        else:
            sock = ICMPv4Socket()
        for sequence in range(count):
            request = ICMPRequest(
                destination=self.ip_address,
                id=id,
                sequence=sequence)
            try:
                sock.send(request)
                reply = sock.receive(request, timeout)
                #print(f'  {reply.bytes_received} bytes from '
                #    f'{reply.source}: ', end='')
                reply.raise_for_status()

                round_trip_time = (reply.time - request.time) * 1000

                # print(f'icmp_seq={sequence} '
                #     f'time={round(round_trip_time, 3)} ms')

                if sequence < count - 1:
                    time.sleep(interval)

            except TimeoutExceeded:
                
                # print(f'  Request timeout for icmp_seq {sequence}')
                return False

            except ICMPError as err:
                #print(err)
                return False

            except ICMPLibError:
                # print('  An error has occurred.')
                return False

        #print('\nCompleted.')
        return True
    def notify_admin(self):
        print("<<<EMAIL>>>")
        # Метод для отправки уведомления администратору
        subject = f"Device {self.ip_address} is not responding"
        body = "The device is not responding to ICMP ping. Please investigate."

        from_email = "novokshanov.eugene@yandex.ru"  # Замените на ваш электронный адрес
        to_email = self.email

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            print("server_smtp")
            server = smtplib.SMTP('smtp.yandex.ru', 587)  # Используйте свой SMTP-сервер и порт
            print("server_smtp1__")
            server.starttls()
            
            server.login(from_email, 'higvzxioxurztkxd')  # Замените на ваш пароль

            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            return True  # Уведомление отправлено успешно
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False  # Не удалось отправить уведомление

    def disconnect(self):
        # Метод для отключения от устройства
        try:
            self.ssh_client.close()
            return True  # Успешное отключение
        except Exception as e:
            print(f"Error disconnecting from {self.ip_address}: {str(e)}")
            return False  # Не удалось отключиться




# def input_function():
#     while True:
#         data = input(">>")#"Введите данные для отправки в основную функцию: ")
#         if(data == "Stop"):
#                 running = False
#                 #run_thread.join()
#         elif(data == "Start"):

#             running = True
#         elif(data == "Kill"):
#             process = multiprocessing.current_process()
#             process.kill()
#         main_queue.put(data)




def main():
    config_file = "settings.yaml"
    try:

        monitor = DeviceMonitor(config_file)
        # run_thread = threading.Thread(target=monitor.start_monitoring)
        # run_thread.start()
        async def control_monitoring(monitor):
            while True:
                user_input = await aioconsole.ainput("Введите 'pause' для паузы или 'resume' для возобновления мониторинга: ")
                if user_input == "pause":
                    monitor.pause_monitoring()
                elif user_input == "resume":
                    monitor.resume_monitoring()
                else:
                    print("Неверная команда.")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            monitor.monitor_devices(),
            control_monitoring(monitor)
        ))
        loop.close()
        # asyncio.get_event_loop().run_until_complete(asyncio.gather(
        #     monitor.monitor_devices(),
        #     control_monitoring()
        # ))
        #monitor.start_monitoring()
        # while True:
            


        # # Создаем объект DeviceMonitor и передаем конфигурацию
        
        #     print(main_queue.get())
        #     if(main_queue.get() == "Stop"):
        #         monitor.run = False
        #         #run_thread.join()
        #     elif(main_queue.get() == "Start"):
        #         monitor.run = True
        #         run_thread = threading.Thread(target=monitor.start_monitoring)
        #         run_thread.start()
                
        #     # Запускаем мониторинг
            

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
     # Замените на путь к вашему YAML-файлу 
    
    

    # main_queue = queue.Queue()

    # # Создаем и запускаем поток для основной функции
    # main_thread = threading.Thread(target=main)
    # main_thread.start()
    
    main()
    # Создаем и запускаем поток для считывания данных
    # input_thread = threading.Thread(target=input_function)
    # input_thread.start()

    # # Ждем завершения потоков (это можно убрать, чтобы программа работала вечно)
    # main_thread.join()
    # input_thread.join()
    # loop.close()  
    #main(config_file)