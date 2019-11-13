#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *
from PIL import ImageTk, Image
import os
import time
import threading

'''
鼠标点击事件
<Button-1>  鼠标左键
<Button-2>   鼠标中间键（滚轮）
<Button-3>  鼠标右键
<Double-Button-1>   双击鼠标左键
<Double-Button-3>   双击鼠标右键
<Triple-Button-1>   三击鼠标左键
<Triple-Button-3>   三击鼠标右键
鼠标移动事件
<B1-Motion>   鼠标左键滑动
<B2-Motion>   鼠标滚轮移动
<B3-Motion>   鼠标右键滑动
鼠标释放事件
<ButtonRelease-1>   鼠标释放左键触发（经测试，必须先点到有效区域，同时在有效区域上释放才行）
<ButtonRelease-2>   释放鼠标滚轮
<ButtonRelease-3>   释放鼠标右键
<Enter>             鼠标进入触发事件，仅一次有效。下次光标需移出有效区域再次进入时才再次触发
<Leave>             鼠标离开触发事件，离开那一刹那触发   
'''


def adb_connect_fun():
    global adb_thread_run
    global adb_connect_success
    while adb_thread_run:
        global adb_lable
        out = os.popen("adb devices").read()
        spit = out.split('\n')
        if len(spit) > 2:
            target = spit[1].split('\t')
            if len(target) > 1:
                if 'device' in target[1]:
                    adb_connect_success = True
                    adb_lable["text"] = 'adb已经连接成功'
                    adb_lable["background"] = 'green'
            else:
                adb_connect_success = False
                adb_lable["text"] = 'adb连接失败'
                adb_lable["background"] = 'red'
            time.sleep(2)


def screen_update_fun():
    global screen_update_run
    global adb_connect_success
    while screen_update_run:
        if adb_connect_success:
            os.popen("adb shell screencap -p sdcard/screen.png && adb pull sdcard/screen.png .")
            time.sleep(2)
            try:
                image_file = Image.open('screen.png')
                photo = ImageTk.PhotoImage(image_file)
                screen_cap.create_image(512, 0, anchor='n', image=photo)
            except IOError:
                print("update screen IOError")
            except RuntimeError:
                print("update screen runtimeError")
        else:
            time.sleep(1)


def window_close_fun():
    global adb_thread_run
    global screen_update_run
    global main_window
    global adb_thread
    global screen_update_thread
    adb_thread_run = False
    screen_update_run = False
    adb_thread.join(1)
    screen_update_thread.join(1)
    main_window.destroy()


def screen_cap_click(event):
    print("鼠标左键点击了一次坐标是:x=" + str(event.x) + "-" + str(event.y))
    os.popen("adb shell input tap " + str(event.x) + " " + str(event.y))


def write_wifi_mac(type):
    global wifi_mac_entry
    global mac_error_result
    global adb_connect_success
    if not adb_connect_success:
        mac_error_result["text"] = "adb 连接失败，请先连接adb,并保持连接稳定。"
        mac_error_result["background"] = "red"
        return
    info = wifi_mac_entry.get()
    if len(info) == 17:
        elem = info.split(':')
        if len(elem) == 6:
            cmd = "adb shell wifitest \"-z \'W " + info + "\'\""
            if type == "bt":
                cmd = "adb shell wifitest \"-z \'B " + info + "\'\""
            out = os.popen(cmd).read()
            if "success" in out:
                mac_error_result["text"] = type + "地址写入成功"
                mac_error_result["background"] = "green"
                return
            mac_error_result["text"] = type + "地址写入失败"
            mac_error_result["background"] = "red"
        else:
            mac_error_result["text"] = "数据不符合MAC地址的规范"
            mac_error_result["background"] = "red"
    else:
        mac_error_result["text"] = "无效的数据长度"
        mac_error_result["background"] = "red"


def write_sn():
    global mac_error_info
    global sn_entry
    global adb_connect_success
    if not adb_connect_success:
        mac_error_result["text"] = "adb 连接失败，请先连接adb,并保持连接稳定。"
        mac_error_result["background"] = "red"
        return
    info = sn_entry.get()
    if 0 < len(info) < 65:
        cmd = "adb shell nvram_sn -z " + info
        out = os.popen(cmd).read()
        if "success" in out:
            mac_error_result["text"] = "SN地址写入成功"
            mac_error_result["background"] = "green"
        else:
            mac_error_result["text"] = "SN地址写入失败"
            mac_error_result["background"] = "red"
    else:
        mac_error_result["text"] = "数据不符合SN的规范[1,64]"
        mac_error_result["background"] = "red"


def reboot_device():
    cmd = "adb reboot"
    os.system(cmd)


adb_thread_run = True
screen_update_run = True
adb_connect_success = False

main_window = Tk()
main_window.title('工厂测试')
main_window.geometry('1200x600')
main_window.resizable(False, False)
main_window.protocol('WM_DELETE_WINDOW', window_close_fun)
main_window.update()

menubar = Menu(main_window)
optionmenu = Menu(menubar, tearoff=False)
optionmenu.add_command(label="重启设备", command=reboot_device)
menubar.add_cascade(label="选项", menu=optionmenu)
main_window.config(menu=menubar)

adb_lable = Label(main_window, text='正在连接adb...', background='blue', fg='white', font=('宋体', 14), width=25)
adb_lable.grid(column=0, row=0, pady=15, padx=15)
adb_thread = threading.Thread(target=adb_connect_fun)
adb_thread.start()

'''
mac_frame = Frame(main_window)
mac_frame.grid(column=0, row=1, pady=15, padx=15)

wifi_mac_lable = Label(mac_frame, text="Wifi Mac", font=('宋体', 14))
wifi_mac_entry = Entry(mac_frame, width=50, font=('宋体', 14))
wifi_mac_write = Button(mac_frame, text="写入地址", font=('宋体', 14), command=lambda: write_wifi_mac("wifi"))
wifi_mac_lable.grid(column=0, row=0, pady=15)
wifi_mac_entry.grid(column=1, row=0, padx=20)
wifi_mac_write.grid(column=2, row=0, padx=15)

bt_mac_lable = Label(mac_frame, text="BT Mac", font=('宋体', 14))
bt_mac_entry = Entry(mac_frame, width=50, font=('宋体', 14))
bt_mac_write = Button(mac_frame, text="写入地址", font=('宋体', 14), command=lambda: write_wifi_mac("bt"))
bt_mac_lable.grid(column=0, row=1, pady=15)
bt_mac_entry.grid(column=1, row=1, padx=20)
bt_mac_write.grid(column=2, row=1, padx=15)

sn_lable = Label(mac_frame, text="SN", font=('宋体', 14))
sn_entry = Entry(mac_frame, width=50, font=('宋体', 14))
sn_write = Button(mac_frame, text="写入SN", font=('宋体', 14), command=write_sn)
sn_lable.grid(column=0, row=2, pady=15)
sn_entry.grid(column=1, row=2, padx=20)
sn_write.grid(column=2, row=2, padx=15)

mac_info_frame = Frame(main_window)
mac_info_frame.grid(column=0, row=2)

mac_error_info = Label(mac_info_frame, text="写入结果:", font=('宋体', 14))
mac_error_info.grid(column=0, row=0)
mac_error_result = Label(mac_info_frame, text="...", font=('宋体', 14))
mac_error_result.grid(column=1, row=0)
'''

screen_cap = Canvas(main_window, width=1024, height=600, bd=0, highlightthickness=0)
screen_cap.grid(column=0, row=3)
screen_cap.bind("<Button-1>", screen_cap_click)
screen_update_thread = threading.Thread(target=screen_update_fun)
screen_update_thread.start()

main_window.mainloop()
