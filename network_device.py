

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
from logger import Logger



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

