
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


def input_process(queue):
    while True:
        user_input = input()
        queue.put(user_input)
        

def main(queue):
    config_file = "settings.yaml"
    try:

        monitor = DeviceMonitor(config_file)

        # async def control_monitoring(monitor):
        #     while True:
        #         user_input = await aioconsole.ainput("Введите 'pause' для паузы или 'resume' для возобновления мониторинга: ")
        #         if user_input == "pause":
        #             monitor.pause_monitoring()
        #         elif user_input == "resume":
        #             monitor.resume_monitoring()
        #         else:
        #             print("Неверная команда.")
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(asyncio.gather(
        #     monitor.monitor_devices(),
        #     control_monitoring(monitor)
        # ))
        # loop.close()
        monitor.start_monitoring(queue)


    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    message_queue = Queue()
    #root_proc = multiprocessing.current_process()
    
    input_proc = Process(target=input_process, args=(message_queue, ))
    main_proc = Process(target=main, args=(message_queue,))

    input_proc.start()
    main_proc.start()

    input_proc.join()
    main_proc.join()
    main()
