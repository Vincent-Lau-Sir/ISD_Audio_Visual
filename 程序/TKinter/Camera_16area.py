"""
# @file         Camera_16area.py
# @brief        A Tkinter GUI returns phase delay from fixed mic position
# @details      This programme will calculate the delay by time difference of arrival(TDOA)
                After calculation, it passes the delay to FPGA via socket. module
                venv: anaconda python 3.10

# @author       Vincent Liu
# @par Copyright (c):
# Copyright (c) 2024, Logistics and Supply Chain MultiTech R&D Centre (LSCM)
# All rights reserved.
# @par History:
               Ver1.1:
                     Wang Xin, 2023/08/01, original version\n
                        multiconn-clientM2308.py   发送SET0给server， server返回COPY
                        multiconn-serverM_2308.py   是对应的server端程序

                        multiconn-clientM2308_2.py   从三维x,y,z值转为delay值,发送第一个delay共四字节给server, server返回COPY
                        multiconn-clientM2308_3.py   在multiconn-clientM2308_2.py 基础上，发送全部32个delay给server,server返回COPY
                        multiconn-serverM_2308_2.py  是服务端程序，对应multiconn-clientM2308_2.py和multiconn-clientM2308_3.py

                     Vincent_Liu, 2024/01/08, some modifications, definition pending\n
 """

import sys
import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np  # wx said "require to install and adjust to certain edition 1.13.3"
import socket
import selectors
import types
import math
from datetime import datetime
import os 

# Get Date 
current_datetime = datetime.now()
# Format the date and time
formatted_datetime = current_datetime.strftime("%m-%d-%y")

# Define Directory Path
CURRENT_PATH = os.getcwd()
VIDEO_SAVE_DIRECTORY = "\Video"
VIDEO_DATE = "\\" + formatted_datetime

# Create class for Camera Flag ( Currently implemented recording and start flag)
class Camera_Viewer:
    def __init__(self):
        self.SELECTION_PIXEL = False
        self.RECORDING = False
        self.START = True

    # Print Current status 
    def Print_Status(self):
        print(f"Selecting Pixel : {self.SELECTION_PIXEL}\nRecording       : {self.RECORDING}\nStart Counter   : {self.START} ")


# Create neccessary Directory
def check_folder_existence(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' exists.")
    else:
        print(f"The folder '{folder_path}' does not exist.")
        os.makedirs(folder_path)

# Create Camera Flag class
Camera = Camera_Viewer()
# Create Directory
check_folder_existence(CURRENT_PATH+VIDEO_SAVE_DIRECTORY)
check_folder_existence(CURRENT_PATH+VIDEO_SAVE_DIRECTORY+VIDEO_DATE)


sel = selectors.DefaultSelector()
sendBuf = b'SET0'
RecvBuf = []
sendFlag = False
MIC_NUMBER = 4  # so far fixed as 4 mics for demo
INDEX = [x for x in range(MIC_NUMBER)]
def start_connections(host, port):
    server_addr = (host, port)
    print("starting connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(outb=b"")
    sel = selectors.DefaultSelector()  # Vincent added from main
    sel.register(sock, events, data=data)
    return sel


def service_connection(key, mask, sel, host, port):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # shd be ready to read
        if recv_data:
            print("received", repr(recv_data))
            print("closing connection")
            sel.unregister(sock)
            sock.close()
        elif not recv_data:
            print("closing connection")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        global sendFlag
        # TODO change to #if sendFlag == True?
        if sendFlag:
            data.outb = sendBuf
            print("sending", repr(data.outb), "to connection", host, port)
            sent = sock.send(data.outb)  # shd be ready to write
            sendFlag = False


def create_and_send_packet(host, port, message):
    while True:
        try:
            while (input("Please input 'start' to send:") != 'start'):
                pass
            sel = start_connections(host, port)
            global sendBuf, sendFlag
            sendBuf = message
            sendFlag = True
            while True:
                events = sel.select(timeout=None)
                if events:
                    for key, mask in events:
                        service_connection(key, mask, sel, host, port)
        # WX: Check for a socket being monitored to continue
                if not sel.get_map():
                    print("exit 2")
                break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
            sys.exit(1)
        finally:
            print("exit 3")
            sel.close()


def get_position():
    mic_position = (
        [0.0000, 0.2500, 0],    # 0
        [0.0000, 0, 0.2500],   # 1
        [0.0000, -0.2500, 0],   # 2
        [0.0000, 0, -0.2500]    # 3
    )

    mic_position = np.array(mic_position)
    return mic_position


'''
This Python function, delay_calculation, calculates the phase delay for a set of microphones (or sensors) based on their positions relative to a target position. Here’s a step-by-step breakdown:
The function takes in a parameter thisposition, which is converted into a numpy array and assigned to Targetposition.
The speed of sound is defined as 340.29 m/s.
The position of the microphones is obtained using the get_position() function.
The reference microphone is chosen as the one at the top of the inner circle (mic_position[2]).
The function calculates the vector from the reference microphone to the target position (soure_ref).
For each microphone, the function calculates the vector from the microphone to the target position (magnitude_s2p[x]), and the delay caused by the difference in distances (delay[x]).
The delays are then adjusted so that the maximum delay is zero, and the others are negative.
The delays are converted to phase delays at a sampling rate of 48kHz, and then scaled and rounded to fit within the range of an FFT window size of 512.
The minimum phase delay is added to all phase delays to ensure they are all positive.
Finally, the phase delays are reshaped to match the number of microphones and returned.'''
# generate 32 delays for each microphone in phase


def delay_calculation(thisposition):
    c_detail = thisposition  # this_location=[6, actual.x, acutal.y]
    c_detail = np.array(c_detail)
    Targetposition = c_detail
    SPEED_OF_SOUND = 340.29
    mic_position = get_position()  # getting mic position
    mic_ref_ori = mic_position[1]  # set as the top mic
    soure_ref = Targetposition - mic_ref_ori
    magnitude_s2p = [0] * MIC_NUMBER
    # np.linalg.norm(求范数)
  # linalg=linear（线性）+algebra（代数），norm则表示范数
  #  https://blog.csdn.net/hqh131360239/article/details/79061535
    magnitude_s2r = np.linalg.norm(soure_ref, axis=0, keepdims=True)
    for x in INDEX:
        magnitude_s2p[x] = Targetposition - mic_position[x]
        magnitude_s2p[x] = np.linalg.norm(
            magnitude_s2p[x], axis=0, keepdims=True)
    delay = [0] * MIC_NUMBER
    for x in INDEX:
        delay[x] = - (magnitude_s2r - magnitude_s2p[x]) / SPEED_OF_SOUND
    delay = abs(min(delay)) + delay
    delay = -1 * (delay - max(delay))  # big to small reverse
    delay_phase = delay * 48000  # 48KHz
    delay = (np.round(delay / 1e-6, 6))
   # mic_delay_extra = find_calibration_value(Vision.distance,Vision.x,Vision.y)
    for x in INDEX:
        delay[x] = (delay[x]) * 1e-6
        delay_phase[x] = delay[x] * 48000
        delay_phase[x] = int(
            delay_phase[x] *
            360 /
            512 *
            256)   # 512 FFT window
    minimum = abs(min(delay_phase))
    delay_phase = delay_phase + minimum
    delay_phase = np.reshape(delay_phase, MIC_NUMBER)
    return delay_phase

# return delay integer to binary.


def delay_to_binary(delay):
    delay_binary_output = [0] * len(delay)
    for x in INDEX:
        delay_binary_output[x] = np.asarray(
            list(map(int, bin(int(delay[x]))[2:].zfill(13))))  # pad the binary string with leading zeros until it is 13 characters long
    return delay_binary_output


'''If you call (3,5), the function will return [0,0,0,1,1]'''


def decToBin(this_value, bin_num):
    num = bin(this_value)[2:].zfill(bin_num)
    num = list(map(int, num))
    return num

# R/W_filed 2 bit
# reversed_val 2bit
# types_val 2bit
# mode 1bit
# Mic_num 5bit
# en_BM 1bit
# en_MC 1bit
# Mic delay 13bit
# Mic_en 1bit
# DAC output select 4bit
# total 32bit


def struct_packet(RW_field, reserved_val, type_val, mode, mic_num, en_bm,
                  en_mc, delay_binary_output_x, mic_en, dac_out_sel):
    # convert into binary form
    #     MIC_change = np.asarray(list(map(int,bin (int(MIC_change))[2:].zfill(4))))
    #     MIC_change = [0,1,1,1]
    # TODO Noted that decToBin eat integer not array
    this_mic_no = decToBin(mic_num, 5)
    # this_reserved = decToBin(reserved_val, 2)
    # this_dac_out_sel = decToBin(..)
#     MC_BM_packet = BM_MC_status(BM_MC_bit_received)
#     delay_time   = delay_binary_output
#     mic_ONOFF = mic_onoff_ID
    #    Channel = np.asarray(list(map(int,bin (int(choice))[2:].zfill(2)))) # register change ch num and turn into binary
    # putting them into array order
    return np.hstack((RW_field, reserved_val, type_val, mode, this_mic_no, en_bm,
                     en_mc, delay_binary_output_x, mic_en, dac_out_sel))


def BintoINT(Binary):
    integer = 0
    result_hex = 0
    for x in range(len(Binary)):
        integer = integer + Binary[x] * 2**(len(Binary) - x - 1)
    result_hex = hex(integer)
    return result_hex


def exitWindow():
    cap.release()
    cv.destroyAllWindows()
    root.destroy()
    root.quit()

# select pixel event


def handleMotion(event):
    global select_pixel_flag
    # print(label_video.winfo_height(),label_video.winfo_width())
    x = event.x
    y = event.y
    block_width = label_video.winfo_width() // 4
    block_height = label_video.winfo_height() // 4
    row = y // block_height
    col = x // block_width
    area = row * 4 + col + 1
    actual_x = (x - 960) / 1000.0
    actual_y = (y - 540) / 1000.0
    this_location[1] = actual_x
    this_location[2] = actual_y
    print(this_location)
    print(delay)
    print(delay_binary_output)
    position_string = "x: {}  y: {}  area:{}\n".format(event.x, event.y, area)
    # need to change host and port here once IP of the server is changed.
    host = "192.168.1.10"
    port = 5001
    # message = create_and_send_packet(
    #     host, port, area.to_bytes(
    #         2, byteorder='big'))
    text.insert(tk.INSERT, position_string)
    select_pixel_flag = 0
    text.see("end")
    label_video.unbind('<ButtonPress-1>')


def disable_event():
    pass

# Converted to use class instead of global 
def Recording_video(Camera):
    Camera.Print_Status()
    if Camera.RECORDING == False:
        Camera.RECORDING = True

    else:
        Camera.RECORDING = False
        Camera.START = True



def select_pixel():
    global select_pixel_flag
    if select_pixel_flag == 0:
        label_video.bind('<ButtonPress-1>', handleMotion)
        select_pixel_flag = 1
    # image=Image.fromarray(img1)
    #  time=str(datetime.datetime.now().today()).replace(':',"_")+'.jpg'
    #  image.save(time)

try: 
    cap = cv.VideoCapture(1)  # for selecting camera from 0 to 2. In surface Pro, usb camera is '2'
    if (cap.isOpened() == False):
        print("Unable to read camera feed")
    print("Pass 0 ")
    cap.set(3, 1920)
    cap.set(4, 1080)
    print("Pass 1 ")
    video_width = int(cap.get(3))
    video_height = int(cap.get(4))
    border_width = 40
    down_panel = 120
    print(cap.isOpened(), video_width, video_height)
    select_pixel_flag = 0
    root = tk.Tk()
    root.title('Acoustic Camera')
    # root.iconbitmap("lscm.ico")
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    # Get the resolution of the screen
    print("Resolution is %dx%d" % (screenwidth, screenheight))
    if screenwidth < video_width or screenheight <= video_height:
        print(screenwidth,video_width,screenheight,video_height)
        print("screen not enough")
        exit()
    else:
        windowsize_string = "{}x{}+{}+{}".format(video_width + border_width,
                                                video_height + down_panel,
                                                int((screenwidth - video_width) / 2),
                                                int((screenheight - video_height) / 2))
        # Set the windows size: length and height. Note a "*" must be used here
        # instead of x
        root.geometry(windowsize_string)
        root.update()          # Refresh the screen to get size of the window
        root.config(background="#6fb765")
        label_video = tk.Label(root, bg="#7CCD7C",
                            # Set tag geometry
                            width=video_width, height=video_height,
                            # Set content format
                            padx=1, pady=1, borderwidth=1, relief="sunken")
        label_video.pack(side="top")
        b1 = tk.Button(root, fg='white', bg='green', activebackground='white', activeforeground='green', text='Select pixel',
                    relief=tk.RIDGE, height=40, width=20, command=select_pixel)
        b1.pack(side=tk.LEFT, padx=10, pady=10)
        b2 = tk.Button(root, fg='white', bg='red', activebackground='white', activeforeground='red', text='EXIT',
                    height=40, width=20, command=exitWindow)
        b2.pack(side=tk.LEFT, padx=10, pady=10)

        # Using Lambda to pass parameters from button action
        record_button = tk.Button(root, fg='white', bg='blue', activebackground='white', activeforeground='red', text='Record',
                    height=40, width=20, command=lambda:Recording_video(Camera))
        
        record_button.pack(side=tk.LEFT,padx=10,pady=10)

        text = tk.Text(root, width=40, height=8, undo=False, autoseparators=False)
        text.pack(side="bottom", padx=10, pady=10)
        root.protocol("WM_DELETE_WINDOW", disable_event)
        root.resizable(1, 1)

        # TODO Need to displace this_location latter two x and y with corresponding value -->by estimation
        # TODO How to pass the selected pixel to this_location? --> Solved
        # Z=distance between camera and object, x is left+/right-, y is down+/up-
        # Vincent: suppose the distance between the object and the camera is 2m, x
        # and y is figured from the window
        this_location = [2, 0, 0]
        delay = delay_calculation(this_location)
        print(delay)
        delay_binary_output = delay_to_binary(delay)
        RW_field = [1, 1]
        reserved_val = [0, 0]
        type_val = [0, 0]
        mode = 0
        mic_num = 0
        en_bm = 1
        en_bc = 1
        mic_en = 1
        dac_out_sel = [1, 0]
        message = struct_packet(
            RW_field,  # 2b
            reserved_val,  # 2b
            type_val,  # 2b
            mode,  # 1b
            mic_num,  # 5b
            en_bm,  # 1b
            en_bc,  # 1b
            delay_binary_output[0],  # 13b
            mic_en,  # 1b
            dac_out_sel)  # 4b
        print(message)
        # convert the message in to integers and print out
        messagehex = BintoINT(message)
        print(messagehex)
        message1 = int(messagehex[2:4], 16)  # hex at  1 and 2
        message2 = int(messagehex[4:6], 16)  # hex at  3 and 4
        message3 = int(messagehex[6:8], 16)  # hex at  5 and 6
        message4 = int(messagehex[8:], 16)  # hex at  7 and onwards
        # print the concerted integers. Each 2-digit hexadecimal number represents
        # a bytes.
        print("m1:{},m2:{},m3:{},m4:{}\n".format(
            message1, message2, message3, message4))
        
        # fourcc = cv.VideoWriter_fourcc(*'XVID')  # Use 'XVID' for AVI format
        fps = int(cap.get(cv.CAP_PROP_FPS))
        # out = cv.VideoWriter('output.avi', fourcc, fps, (640, 480))  # Adjust resolution as needed
        fourcc = cv.VideoWriter_fourcc(*"mp4v")
        counter = 0 

        while True:
            retval, frame = cap.read()
            img = frame
            # Set the codec and create a VideoWriter object


        # in case of a user stand in front of or back of the camera
            # img=cv.flip(img,1)
            if retval == True:
                img1 = cv.cvtColor(img, cv.COLOR_BGR2RGB)

                img = ImageTk.PhotoImage(Image.fromarray(img1))
                label_video['image'] = img
                root.update()
                if Camera.RECORDING== True:
                    if Camera.START == True :
                        counter +=1
                        current_datetime = datetime.now()
                    # Format the date and time
                        formatted_datetime = current_datetime.strftime("[%m-%d-%y]%H_%M_%S")
                        print(formatted_datetime)
                        video_name = CURRENT_PATH+VIDEO_SAVE_DIRECTORY+VIDEO_DATE + "\\"+str(formatted_datetime)+'.avi'
                        FPS = 20 
                        out = cv.VideoWriter(video_name, cv.VideoWriter_fourcc('M','J','P','G'), FPS, (video_width,video_height))
                        Camera.START = False
                    else:
                        out.write(frame)
                else:
                    if Camera.START == False:
                        out.release()
                    
            else:
                print("exit program")
                out.release()
                cap.release()
                exit()
            
            cv.waitKey(1)
            
    # cap.release()

except KeyboardInterrupt:
    out.release()
    cap.release()
    exit()

# Will need work to convert all gloabl into class to use following setting

# if __name__ == "__main__":
#     # This block will only execute if the script is run directly, not if it's imported as a module
#     Run_Camera_View()
# else:
#     print("Incorrect Operation!!! Check your Path !")