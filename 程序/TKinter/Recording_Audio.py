import sounddevice as sd  #pip3 install sounddevice 
import wave
from datetime import datetime 
import os 
import numpy as np 
from moviepy.editor import VideoFileClip, AudioFileClip
# from Camera_16area import Return_recording_time
# from moviepy.audio.fx.all import audio_fadei
import time 



def check_folder_existence(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' exists.")
    else:
        print(f"The folder '{folder_path}' does not exist.")
        os.makedirs(folder_path)

def combine_video_audio(video_path, audio_path, output_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)


    # Set the audio of the video to the loaded audio clip
    video_clip = video_clip.set_audio(audio_clip)

    # output_path = video_clip[:-4]+"Com.avi"

    # Write the combined clip to a new file
    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp.m4a', remove_temp=False)

def write_start_txt():
    CURRENT_PATH = os.getcwd()
    with open(CURRENT_PATH+"/ready_video.txt", 'w') as file:
        # Write some text to the file
        file.write("Start")


def Start_recording():
    print("Start Recording")
    current_datetime = datetime.now()
    CURRENT_PATH = os.getcwd()
    AUDIO_PATH = "\Audio"
    OUTPUT_PATH = "\Combined"
    Folder_data = current_datetime.strftime("%m-%d-%y")
    
    # Format the date and time
    formatted_datetime = current_datetime.strftime("[%m-%d-%y]%H_%M_%S")
    filename = CURRENT_PATH+AUDIO_PATH+"\\"+Folder_data+"\\"+formatted_datetime+".wav"
    Output_filename = CURRENT_PATH + OUTPUT_PATH +"\\"+Folder_data+"\\"+formatted_datetime+".avi"
    duration = 10
    samplerate=48000
    # write_start_txt()
    # time.sleep(0.5)
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype=np.int16)
    time.sleep(4)
    print("Recording...")
    
    sd.wait()  # Wait until recording is finished
    print("Recording done.")

    audio_data

    with wave.open(filename, 'w') as wf:
            wf.setnchannels(2)  # Stereo
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())
        
    time.sleep(5)

    with open(os.getcwd()+"/FileList.txt", 'r') as file:
        # Read and print each line
        Output=[0]*3
        line = file.readline()
        counter = 0
        while line:
            print(line.strip())  # Strip removes the newline character
            line = file.readline()
            Output[counter] = line.strip()
            counter+=1
    # os.makedirs(os.path.dirname(Output[2]), exist_ok=True)
    combine_video_audio(Output[0],filename,Output_filename)
    # combine_video_audio(Output[0],Output[1],Output[2])

def main():
    while True:
        time.sleep(0.5)
        with open(os.getcwd()+"/Command.txt", 'r') as file:
            line = file.readline()
            if line == "Recording":
                Start_recording()
            elif line == "Exit":
                exit()
        
        


if __name__ == "__main__":
    main()



