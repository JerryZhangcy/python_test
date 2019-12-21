#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import datetime
from tkinter import *
import time
import threading
import math


def adb_connect_fun():
    global adb_thread_run
    global adb_connect_success
    while adb_thread_run:
        global adb_label
        out = os.popen("adb devices").read()
        spit = out.split('\n')
        if len(spit) > 2:
            target = spit[1].split('\t')
            if len(target) > 1:
                if 'device' in target[1]:
                    adb_connect_success = True
                    adb_label["text"] = 'adb已经连接成功'
                    adb_label["background"] = 'green'
            else:
                adb_connect_success = False
                adb_label["text"] = 'adb连接失败'
                adb_label["background"] = 'red'
            time.sleep(2)


def window_close_fun():
    global adb_thread_run
    adb_thread_run = False
    main_window.destroy()


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


def get_test_info():
    num = num_v.get()
    avg_cpu_user = 0
    cpu_user_sum = 0
    avg_cpu_sys = 0
    cpu_sys_sum = 0
    avg_mem = 0
    sum_mem = 0
    while num > 0:
        num = num - 1
        cpuinfos = os.popen("adb shell top -n 1").readlines()
        meminfos = os.popen("adb shell dumpsys meminfo").readlines()
        for cpuinfo in cpuinfos:
            if "cpu" in cpuinfo:
                cpuinfo_list = cpuinfo.split(" ")
                print(cpuinfo_list)
                for cpuinfo_item in cpuinfo_list:
                    if "user" in cpuinfo_item:
                        if len(cpuinfo_item) == 7:
                            cpuinfo_user = int(cpuinfo_item[0:2])
                        elif len(cpuinfo_item) == 6:
                            cpuinfo_user = int(cpuinfo_item[0:1])
                        else:
                            cpuinfo_user = int(cpuinfo_item[0:3])
                        cpuuserinfos.append(cpuinfo_user)
                    if "sys" in cpuinfo_item:
                        if len(cpuinfo_item) == 6:
                            cpuinfo_sys = int(cpuinfo_item[0:2])
                        elif len(cpuinfo_item) == 5:
                            cpuinfo_sys = int(cpuinfo_item[0:1])
                        else:
                            cpuinfo_sys = int(cpuinfo_item[0:3])
                        cpusysinfos.append(cpuinfo_sys)
                break
        for meminfo in meminfos:
            if "Free RAM" in meminfo:
                print(meminfo)
                mem_free = int(meminfo[10:meminfo.index("K")].replace(",", ""))
                memfreeinfos.append(mem_free)
                break

    cpu_user_num = len(cpuuserinfos)
    if cpu_user_num > 0:
        for cpuuserinfo in cpuuserinfos:
            cpu_user_sum = cpu_user_sum + cpuuserinfo
        avg_cpu_user = cpu_user_sum / cpu_user_num

    cpu_sys_num = len(cpusysinfos)
    if cpu_sys_num > 0:
        for cpusysinfo in cpusysinfos:
            cpu_sys_sum = cpu_sys_sum + cpusysinfo
        avg_cpu_sys = cpu_sys_sum / cpu_sys_num

    mem_num = len(memfreeinfos)
    if mem_num > 0:
        for memfreeinfo in memfreeinfos:
            sum_mem = sum_mem + memfreeinfo
        avg_mem = sum_mem / mem_num

    test_button['state'] = 'normal'
    status_label["bg"] = "green"
    status_label["text"] = "测试已经结束!"
    cpu_result["text"] = "user:" + str(avg_cpu_user) + "%" + " sys:" + str(avg_cpu_sys) + "%"
    ram_result["text"] = str(avg_mem / 1024)


def start_test():
    if not adb_connect_success:
        status_label["bg"] = "red"
        status_label["text"] = "请确保adb已经连接成功"
        return
    try:
        num = num_v.get()
    except TclError:
        status_label["bg"] = "red"
        status_label["text"] = "非法的字符"
        num_entry.focus_force()
        num_entry.delete(0, END)
        return
    test_button['state'] = 'disabled'
    status_label["bg"] = "green"
    status_label["text"] = "正在测试！"
    cpuuserinfos.clear()
    cpusysinfos.clear()
    memfreeinfos.clear()
    get_info_thread = threading.Thread(target=get_test_info)
    get_info_thread.start()


adb_thread_run = True
adb_connect_success = False
cpusysinfos = []
cpuuserinfos = []
memfreeinfos = []

main_window = Tk()
main_window.title('性能测试')
center_window(main_window, 400, 300)
main_window.resizable(False, False)
main_window.protocol('WM_DELETE_WINDOW', window_close_fun)
main_window.update()

adb_label = Label(main_window, text='正在连接adb...', background='pink', fg='white', font=('宋体', 14), width=25)
adb_label.pack()
adb_thread = threading.Thread(target=adb_connect_fun)
adb_thread.start()

num_v = IntVar(value=1)
module_v = StringVar()

info_frame = Frame(main_window)
num_label = Label(info_frame, text="测试次数", font=('宋体', 14))
num_label.grid(column=0, row=0, pady=10)
num_entry = Entry(info_frame, width=20, textvariable=num_v)
num_entry.focus_force()
num_entry.grid(column=1, row=0, padx=10)

module_label = Label(info_frame, text="测试模块", font=('宋体', 14))
module_label.grid(column=0, row=1, pady=10)
module_entry = Entry(info_frame, width=20, textvariable=module_v)
module_entry.grid(column=1, row=1, pady=10)
info_frame.pack(anchor=W, padx=50, pady=10)

status_label = Label(main_window, text="状态信息", font=('宋体', 14))
status_label.pack()

result_frame = Frame(main_window)
cpu_label = Label(result_frame, text="CPU(avg):", font=('宋体', 14))
cpu_label.grid(column=0, row=0, pady=5)
cpu_result = Label(result_frame, text="", font=('宋体', 14))
cpu_result.grid(column=1, row=0, pady=5)

ram_label = Label(result_frame, text="RAM(MB):", font=('宋体', 14))
ram_label.grid(column=0, row=1, pady=5)
ram_result = Label(result_frame, text="", font=('宋体', 14))
ram_result.grid(column=1, row=1, pady=5)
result_frame.pack(anchor=W, padx=20, pady=5)

test_button = Button(main_window, text="开始测试", font=('宋体', 14), width=10, command=start_test)
test_button.pack()

main_window.mainloop()
