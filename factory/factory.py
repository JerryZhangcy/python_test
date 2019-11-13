#!/usr/bin/python
# -*- coding: UTF-8 -*-
from tkinter import *
import os
import time
import threading
import math


def adb_connect_fun():
    global adb_thread_run
    global adb_connect_success
    global button_start
    while adb_thread_run:
        global adb_label
        out = os.popen("adb devices").read()
        spit = out.split('\n')
        if len(spit) > 2:
            target = spit[1].split('\t')
            if len(target) > 1:
                if 'device' in target[1]:
                    adb_connect_success = True
                    button_start["state"] = "normal"
                    adb_label["text"] = 'adb已经连接成功'
                    adb_label["background"] = 'green'
            else:
                adb_connect_success = False
                button_start["state"] = "disabled"
                adb_label["text"] = 'adb连接失败'
                adb_label["background"] = 'red'
                test_window.destroy()
            time.sleep(2)


def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


def window_close_fun():
    global adb_thread_run
    adb_thread_run = False
    main_window.destroy()


def top_window_close_fun():
    global write_window_show
    write_window_show = False
    write_window.destroy()


def reboot_device():
    cmd = "adb reboot"
    os.system(cmd)


def entry_info_check(entry_type):
    if "Wifi" == entry_type:
        wifi_info = wifi_v.get()
        if len(wifi_info) == 17:
            elem = wifi_info.split(':')
            if len(elem) == 6:
                check_label["text"] = "[Wifi]数据输入正确"
                check_label["background"] = "green"
            else:
                wifi_entry.delete(0, END)
                check_label["text"] = "[Wifi]数据不符合MAC地址的规范"
                check_label["background"] = "red"
        else:
            wifi_entry.delete(0, END)
            check_label["text"] = "[Wifi]无效的数据长度"
            check_label["background"] = "red"
    elif "BT" == entry_type:
        bt_info = bt_v.get()
        if len(bt_info) == 17:
            elem = bt_info.split(':')
            if len(elem) == 6:
                check_label["text"] = "[BT]数据输入正确"
                check_label["background"] = "green"
            else:
                bt_entry.delete(0, END)
                check_label["text"] = "[BT]数据不符合MAC地址的规范"
                check_label["background"] = "red"
        else:
            bt_entry.delete(0, END)
            check_label["text"] = "[BT]无效的数据长度"
            check_label["background"] = "red"
    elif "Barcode" == entry_type:
        barcode_info = barcode_v.get()
        if 1 < len(barcode_info) < 65:
            check_label["text"] = "[Barcode]数据输入正确"
            check_label["background"] = "green"
        else:
            barcode_entry.delete(0, END)
            check_label["text"] = "[Barcode]数据不符合规范[1,64]"
            check_label["background"] = "red"
    return True


def start_input_info():
    global check_label
    global wifi_entry
    global bt_entry
    global barcode_entry
    global write_window
    global write_window_show
    item_check = False
    for item_value in item_values:
        if item_value.get() == 1:
            item_check = True
    if not item_check:
        return
    if write_window_show:
        return
    write_window_show = True
    write_window = Toplevel(main_window)
    write_window.resizable(False, False)
    write_window.title("Scan Data")
    center_window(write_window, 500, 400)
    write_window.protocol('WM_DELETE_WINDOW', top_window_close_fun)
    write_window.attributes("-toolwindow", True)
    write_window.wm_attributes("-topmost", True)
    write_window.focus_force()
    if item_values[0].get() == 1:
        wifi_entry_label = Label(write_window, text="Wifi", font=('宋体', 14))
        wifi_entry_label.grid(column=0, row=0, pady=10)
        wifi_entry = Entry(write_window, width=40, textvariable=wifi_v, validate="focusout",
                           validatecommand=lambda: entry_info_check("Wifi"))
        wifi_entry.grid(column=1, row=0, padx=10)
        wifi_entry.focus_force()
    if item_values[1].get() == 1:
        bt_entry_label = Label(write_window, text="BT", font=('宋体', 14))
        bt_entry_label.grid(column=0, row=1, pady=10)
        bt_entry = Entry(write_window, width=40, textvariable=bt_v, validate="focusout",
                         validatecommand=lambda: entry_info_check("BT"))
        bt_entry.grid(column=1, row=1, padx=10)
        if item_values[0].get() == 0:
            bt_entry.focus_force()
    if item_values[2].get() == 1:
        barcode_entry_label = Label(write_window, text="Barcode", font=('宋体', 14))
        barcode_entry_label.grid(column=0, row=2, pady=10)
        barcode_entry = Entry(write_window, width=40, textvariable=barcode_v, validate="focusout",
                              validatecommand=lambda: entry_info_check("Barcode"))
        barcode_entry.grid(column=1, row=2, padx=10)
        if item_values[0].get() == 0 and item_values[1].get() == 0:
            barcode_entry.focus_force()
    check_label = Label(write_window, font=('宋体', 14))
    check_label.grid(column=0, row=3, columnspan=5, padx=10, pady=15)
    write_button_frame = Frame(write_window)
    write_button_frame.grid(column=0, row=4, columnspan=6, pady=15)
    cancel_button = Button(write_button_frame, text="Cancel", font=('宋体', 14), command=top_window_close_fun)
    cancel_button.grid(column=0, row=0, columnspan=2, padx=25)
    start_button = Button(write_button_frame, text="Start", font=('宋体', 14), command=write_info_to_device)
    start_button.grid(column=4, row=0, columnspan=2, padx=25)


def write_info_to_device():
    wifi_to_device = True
    bt_to_device = True
    barcode_to_device = True
    # write wifi mac
    if item_values[0].get() == 1:
        wifi_info = wifi_v.get()
        if len(wifi_info) == 17:
            elem = wifi_info.split(':')
            if len(elem) == 6:
                cmd = "adb shell wifitest \"-z \'W " + wifi_info + "\'\""
                out = os.popen(cmd).read()
                if "success" in out:
                    wifi_to_device = True
                else:
                    wifi_to_device = False
            else:
                wifi_entry.delete(0, END)
                check_label["text"] = "[Wifi]数据不符合MAC地址的规范"
                check_label["background"] = "red"
                return
        else:
            wifi_entry.delete(0, END)
            check_label["text"] = "[Wifi]无效的数据长度"
            check_label["background"] = "red"
            return
    # write bt mac
    if item_values[1].get() == 1:
        bt_info = bt_v.get()
        if len(bt_info) == 17:
            elem = bt_info.split(':')
            if len(elem) == 6:
                cmd = "adb shell wifitest \"-z \'B " + bt_info + "\'\""
                out = os.popen(cmd).read()
                if "success" in out:
                    bt_to_device = True
                else:
                    bt_to_device = False
            else:
                bt_entry.delete(0, END)
                check_label["text"] = "[BT]数据不符合MAC地址的规范"
                check_label["background"] = "red"
                return
        else:
            bt_entry.delete(0, END)
            check_label["text"] = "[BT]无效的数据长度"
            check_label["background"] = "red"
            return
    # write barcode
    if item_values[2].get() == 1:
        barcode_info = barcode_v.get()
        if 1 < len(barcode_info) < 65:
            cmd = "adb shell nvram_sn -z " + barcode_info
            out = os.popen(cmd).read()
            if "success" in out:
                barcode_to_device = True
            else:
                barcode_to_device = False
        else:
            barcode_entry.delete(0, END)
            check_label["text"] = "[Barcode]数据不符合规范[1,64]"
            check_label["background"] = "red"
            return
    write_result = ''
    if not wifi_to_device:
        write_result = write_result + "[Wifi]写入失败 "
    if not bt_to_device:
        write_result = write_result + "[BT]写入失败 "
    if not barcode_to_device:
        write_result = write_result + "[Barcode]写入失败 "
    if write_result == '':
        check_label["text"] = "数据写入成功"
        check_label["background"] = "green"
        if item_values[0].get() == 1:
            wifi_entry.delete(0, END)
            wifi_entry.focus_force()
        if item_values[1].get() == 1:
            bt_entry.delete(0, END)
            if item_values[0].get() == 0:
                bt_entry.focus_force()
        if item_values[2].get() == 1:
            barcode_entry.delete(0, END)
            if item_values[0].get() == 0 and item_values[1].get() == 0:
                barcode_entry.focus_force()
    else:
        check_label["text"] = write_result
        check_label["background"] = "red"


def no_symbol_to_symbol(value):
    symbol_value = value
    # 取补码并且+1
    c_value = (value ^ 0x7fff) + 1
    # 判断符号位
    symbol_bit = c_value >> 15
    # 如果是1就转为负数
    if symbol_bit == 1:
        del_symbol_value = c_value & 0x7fff
        symbol_value = del_symbol_value.__neg__()
    return symbol_value


def detach_channels(file_content=b'', channel=0):
    if 7 < channel < 0:
        return 0
    count = 0
    sum_value = 0
    for i in range(0, len(file_content), 16):
        item_value = (file_content[i + 2 * channel + 1] << 8) | (file_content[i + 2 * channel] & 0xff)
        item_value = no_symbol_to_symbol(item_value)
        sum_value += abs(item_value) * abs(item_value)
        count += 1
    avg = math.sqrt(sum_value / count)
    if avg == 0:
        return 0
    rms = 20 * math.log10(avg / 32767)
    return rms


def get_channels_rms(file_name=None):
    audio_file = open(file_name, 'rb')
    file_content = audio_file.read()
    rms_list = []
    for channel in range(0, 4):
        rms = '%5.2f' % detach_channels(file_content, channel)
        rms_list.append(rms)
    audio_file.close()
    return rms_list


def get_consistency_result(mic_list=[]):
    if mic_list:
        max_value = abs(float(mic_list[0]))
        min_value = abs(float(mic_list[0]))
        for item in mic_list:
            item_value = abs(float(item))
            if item_value > max_value:
                max_value = item_value
            if item_value < min_value:
                min_value = item_value
        if max_value == 0 or min_value == 0:
            return False
        return max_value - min_value <= 6
    else:
        return False


def get_airtightness_result(normal_list=[], block_list=[]):
    success = True
    if normal_list and block_list:
        for i in range(0, len(normal_list)):
            if abs(abs(float(normal_list[i])) - abs(float(block_list[i]))) <= 15:
                success = False
        return success
    return False


def start_test_item(type):
    global test_info
    global test_button
    global test_result
    global test_window
    test_window = Toplevel(main_window)
    test_window.resizable(False, False)
    test_window.title("Testing")
    center_window(test_window, 500, 400)
    # test_window.protocol('WM_DELETE_WINDOW', top_window_close_fun)
    test_window.attributes("-toolwindow", True)
    test_window.wm_attributes("-topmost", True)
    test_window.focus_force()

    if 'mic' == type:
        test_tip = Label(test_window, text="1.请确保已经开启白噪音\n2.点击开始按钮开始测试", font=('宋体', 16))
        test_tip.pack(pady=15)
        test_info = Label(test_window, font=('宋体', 16))
        test_info.pack(pady=15)
        test_result = Label(test_window, font=('宋体', 14))
        test_result.pack(pady=15)
        test_button = Button(test_window, text="开始测试", font=('宋体', 16), command=mic_test)
        test_button.pack(pady=25)


def mic_record_thread():
    global mic_test_state
    global mic_normal_list
    global mic_blocking_list
    global mic_test_result
    if mic_test_state == 'Normal':
        os.popen("adb shell tinycap sdcard/mic_test_normal.pcm -D 0 -d 2 -r 16000 -b 16 -c 8 -T 3")
        time.sleep(4)
        os.popen("adb pull sdcard/mic_test_normal.pcm .")
        time.sleep(1)
        test_info['text'] = '正在进行一致性分析请稍等...'
        test_info['bg'] = 'pink'
        mic_normal_list = get_channels_rms('mic_test_normal.pcm')
        mic_test_result += "正常  "
        for item in mic_normal_list:
            mic_test_result += item + "  "
        mic_test_result += "\n"
        test_result['text'] = mic_test_result
        cos_res = get_consistency_result(mic_normal_list)
        if cos_res:
            test_button['state'] = 'normal'
            test_info['text'] = '请堵塞MIC孔后，点击开始测试按钮进行气密性测试'
            test_info['bg'] = 'pink'
            mic_test_state = 'Blocking'
        else:
            test_info['text'] = '麦克一致性测试失败'
            test_info["bg"] = 'red'
            mic_test_clean()
    elif mic_test_state == 'Blocking':
        os.popen("adb shell tinycap sdcard/mic_test_block.pcm -D 0 -d 2 -r 16000 -b 16 -c 8 -T 3")
        time.sleep(4)
        os.popen("adb pull sdcard/mic_test_block.pcm .")
        time.sleep(1)
        test_info['text'] = '正在进行气密性分析请稍等...'
        test_info['bg'] = 'pink'
        mic_blocking_list = get_channels_rms('mic_test_block.pcm')
        mic_test_result += "堵塞  "
        for item in mic_blocking_list:
            mic_test_result += item + "  "
        mic_test_result += "\n"
        mic_test_result += "下降  "
        for i in range(0, len(mic_normal_list)):
            diff = '%5.2f' % abs(float(mic_normal_list[i]) - float(mic_blocking_list[i]))
            mic_test_result += str(diff) + "  "
        test_result['text'] = mic_test_result
        test_info['text'] = '录制已经完成正在给出最终结果。'
        test_info['bg'] = 'pink'
        at_res = get_airtightness_result(mic_normal_list, mic_blocking_list)
        print(at_res)
        if at_res:
            test_info['text'] = '麦克一致性和气密性测试成功'
            test_info["bg"] = 'green'
        else:
            test_info['text'] = '麦克气密性测试失败'
            test_info["bg"] = 'red'
        mic_test_clean()


def mic_test_clean():
    global mic_test_state
    global mic_normal_list
    global mic_blocking_list
    global mic_test_result
    mic_test_state = 'Normal'
    mic_normal_list = []
    mic_blocking_list = []
    test_button['state'] = 'normal'


def mic_test():
    global mic_test_result
    test_button['state'] = 'disabled'
    test_info['text'] = '正在录音请稍等...'
    test_info['bg'] = 'pink'
    if mic_test_state == 'Normal':
        mic_test_result = ""
        test_result['text'] = ''
    mic_thread = threading.Thread(target=mic_record_thread)
    mic_thread.start()


mic_test_state = 'Normal'
mic_normal_list = []
mic_blocking_list = []
mic_test_result = "      声道1   声道2   声道3   声道4 \n"

adb_thread_run = True
adb_connect_success = False
write_window_show = False

main_window = Tk()
main_window.title('工厂测试')
center_window(main_window, 800, 600)
main_window.resizable(False, False)
main_window.protocol('WM_DELETE_WINDOW', window_close_fun)
main_window.update()

wifi_v = StringVar()
bt_v = StringVar()
barcode_v = StringVar()
check_v = StringVar()

menu_bar = Menu(main_window)
option_menu = Menu(menu_bar, tearoff=False)
option_menu.add_command(label="重启设备", command=reboot_device)
menu_bar.add_cascade(label="选项", menu=option_menu)
main_window.config(menu=menu_bar)

adb_label = Label(main_window, text='正在连接adb...', background='pink', fg='white', font=('宋体', 14), width=25)
adb_label.pack()
adb_thread = threading.Thread(target=adb_connect_fun)
adb_thread.start()

write_test_frame = Frame(main_window, width=800)
write_test_frame.pack(anchor=W, padx=15)

item_choose_frame = LabelFrame(write_test_frame, text="Write Option", font=('宋体', 16))
items = ["Wifi Address", "BT Address", "Barcode"]
item_values = []
for item in items:
    item_values.append(IntVar())
    b = Checkbutton(item_choose_frame, text=item, variable=item_values[-1], font=('宋体', 14))
    b.pack(anchor=W, pady=5)
button_start = Button(item_choose_frame, text="Start", font=('宋体', 14), width=10, command=start_input_info)
button_start.pack(pady=5)
button_start["state"] = "disabled"
item_choose_frame.pack(anchor=W, padx=15, pady=15, side=LEFT)

item_test_frame = LabelFrame(write_test_frame, text="Test Option", font=('宋体', 16), width=25)
test_items = {'mic': '麦克'}
test_items_key = test_items.keys()
test_items_value = test_items.values()
for test_item_key in test_items_key:
    b = Button(item_test_frame, text=test_items[test_item_key], font=('宋体', 14), width=10,
               command=lambda: start_test_item(test_item_key))
    b.pack(pady=15)
item_test_frame.pack(anchor=NE, padx=200, pady=5, side=LEFT)

main_window.mainloop()
