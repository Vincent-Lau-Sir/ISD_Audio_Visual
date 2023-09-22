import os
import datetime
import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv

def select_pixel():
  # global select_pixel_flag
  # if select_pixel_flag==0:
  #    label_video.bind('<ButtonPress-1>',handleMotion)
  #    select_pixel_flag=1
   image=Image.fromarray(img1)  
   time=str(datetime.datetime.now().today()).replace(':',"_")+'.jpg'
   image.save(time)
  
def exitWindow():
   cap.release()
   cv.destroyAllWindows()
   root.destroy()
   root.quit()  

def handleMotion(event):
    global select_pixel_flag
    position_string="x: {},y: {}\n".format(event.x, event.y)
    text.insert(tk.INSERT, position_string)
    select_pixel_flag=0
    text.see("end")
    label_video.unbind('<ButtonPress-1>')

def disable_event():
    pass

cap= cv.VideoCapture(0)
if (cap.isOpened() == False):
  print("Unable to read camera feed")
video_width=int(cap.get(3))
video_height=int(cap.get(4))
border_width=40
down_panel=120
print(cap.isOpened(),video_width,video_height)
select_pixel_flag=0
root = tk.Tk()
root.title('wx Camera App')
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
print("电脑的分辨率是%dx%d" % (screenwidth,screenheight))  # 获取电脑屏幕的大小
if screenwidth<= video_width or screenheight<=video_height:
   print("screen not enough")
   exit()
else:
   windowsize_string="{}x{}+{}+{}".format(video_width+border_width, video_height+down_panel, int((screenwidth-video_width)/2), int((screenheight-video_height)/2) ) 
   root.geometry(windowsize_string)    #设置窗口大小:宽x高,注,此处不能为 "*",必须使用 "x"
   root.update()          # 要得到窗口的大小，必须先刷新一下屏幕
   root.config(background="#6fb765")
   label_video = tk.Label(root, bg="#7CCD7C",
                  # 设置标签内容区大小
                  width=video_width,height=video_height,
                  # 设置填充区距离、边框宽度和其样式（凹陷式）+
                  padx=1, pady=1, borderwidth=1, relief="sunken")
   label_video.pack(side="top")


   b1=tk.Button(root,bg='green',fg='white',activebackground='white',activeforeground='green',text='Capture photo',
                 relief=tk.RIDGE,height=40,width=20,command=select_pixel)
   b1.pack(side=tk.LEFT,padx=10,pady=10)
   b2=tk.Button(root,fg='white',bg='red',activebackground='white',activeforeground='red',text='EXIT',
                height=40,width=20,command=exitWindow)
   b2.pack(side=tk.LEFT,padx=10,pady=10)
   text = tk.Text(root, width=40, height=8, undo=False, autoseparators=False)
   text.pack(side="bottom",padx=10,pady=10)
   root.protocol("WM_DELETE_WINDOW", disable_event)
   root.resizable(0,0)

   while True:
    retval, img=cap.read()
  #  img=cv.flip(img,1)
    if retval== True:  
      img1=cv.cvtColor(img,cv.COLOR_BGR2RGB)
      img=ImageTk.PhotoImage(Image.fromarray(img1))
      label_video['image']=img
      root.update()
    else:
       print("exit program")
       exit()
#cap.release()    
