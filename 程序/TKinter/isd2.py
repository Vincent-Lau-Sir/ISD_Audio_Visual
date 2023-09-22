from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
import cv2 as cv
import numpy as np ###### require install and adjust to certain edition 1.13.3

def select_pixel():
   global select_pixel_flag
   if select_pixel_flag==0:
      label_video.bind('<ButtonPress-1>',handleMotion)
      select_pixel_flag=1
  # image=Image.fromarray(img1)  
  # time=str(datetime.now().today()).replace(':',"_")+'.jpg'
  # image.save(time)
  
def exitWindow():
   cap.release()
   cv.destroyAllWindows()
   root.destroy()
   root.quit()  


def estimate_distance(w):
   if w>105:
    return_str= "less than 1m\n"
   elif w>60 and w<=105:
    return_str= "1-2m\n"
   elif w>40 and w<=60:
    return_str= "2-3m\n"
   elif w>31 and w<=40:
    return_str= "3-4m\n"
   elif w>26 and w<=31:
    return_str= "4-5m\n"
   elif w>24 and w<=26:
    return_str= "5-6m\n"
   else:
    return_str= "more than 6m\n"
   return return_str

def handleMotion(event):
  global select_pixel_flag
  position_string="x: {},y: {}\n".format(event.x, event.y)
  text.insert(tk.INSERT, position_string)
  select_pixel_flag=0
  if event.x-150 <=0:
     x_left=0
  else:
     x_left=event.x-150

  if event.y-150 <=0:
     y_up=0
  else:
     y_up=event.y-150

  if event.x+150 >=video_width:
     x_right=video_width-1
  else:
     x_right=event.x+150

  if event.y+150 >=video_height:
     y_down=video_height-1
  else:
     y_down=event.y+150
  print("x_left:{},x_right:{},y_up:{},y_down:{}".format(x_left,x_right,y_up,y_down) )
  start_time =datetime.now()
  gray = cv.cvtColor(img1[y_up:y_down,x_left:x_right], cv.COLOR_BGR2GRAY)
  # Detect faces
  faces= face_cascade.detectMultiScale(gray, 1.1, 3,minSize=(10,10))
  faces=np.array(faces)
  if faces.size>0:
    print("have face,detect time is ", (datetime.now()-start_time).microseconds)
    print("faces are ", faces)
    num_faces=faces.size/4
    if num_faces>1:
      min_dis=0
      min_index=0
      this_click=np.array([event.x,event.y])
      for row in range(faces.shape[0]):
        this_face=np.array(faces[row][0]+faces[row][2]/2,faces[row][1]+ faces[row][3]/2)+ np.array([x_left, y_up])
        print("this face is ", this_face)
        this_delta=np.linalg.norm(this_face-this_click, axis=0, keepdims=False) 
        if min_dis==0:
            min_dis=this_delta
            min_index=row
        elif this_delta<min_dis:
            min_index=row
      print("near face is ", min_index)
      text.insert(tk.INSERT,   estimate_distance(faces[min_index][2]) )
    else:    # only one face
      text.insert(tk.INSERT,   estimate_distance(faces[0][2]) )  #w
       
  text.see("end")
  label_video.unbind('<ButtonPress-1>')

def disable_event():
    pass



face_cascade = cv.CascadeClassifier('D:\\myProjects\\pythonProjects\\AI_projects\\ISD_project\\detect_face_demo\\haarcascade_frontalface_default.xml')
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
   b1=tk.Button(root,bg='green',fg='white',activebackground='white',activeforeground='green',text='Select pixel',
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
