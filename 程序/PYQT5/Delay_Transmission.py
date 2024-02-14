def handleMotion(event):
    global select_pixel_flag
    # print(label_video.winfo_height(),label_video.winfo_width())
    x = event.x
    y = event.y
    block_width = WINDOW_WIDTH // 4
    block_height = WINDOW_HEIGHT // 4
    row = y // block_height
    col = x // block_width
    area = row * 4 + col + 1
    actual_x = (x - 960) / 1000.0
    actual_y = (y - 540) / 1000.0
    Location = [actual_x,actual_y]
    print(Location)
    # print(delay)
    # print(delay_binary_output)
    position_string = "x: {}  y: {}  area:{}\n".format(event.x, event.y, area)
    # need to change host and port here once IP of the server is changed.
    host = "192.168.1.10"
    port = 5001
    # message = create_and_send_packet(
    #     host, port, area.to_bytes(
    #         2, byteorder='big'))
    select_pixel_flag = 0


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