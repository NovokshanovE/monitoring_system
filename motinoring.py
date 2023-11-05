
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
from device_monitor import DeviceMonitor




def main():
    config_file = "settings.yaml"
    try:

        monitor = DeviceMonitor(config_file)

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


    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
