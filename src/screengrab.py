#!/usr/bin/python3
# ver. 0.5.1
version = '0.5.1'

# ToDo:
# - disable audio selection when recording starts
# - integrate proper log file (?)

import tkinter as tk
from tkinter.constants import *
from tkinter import filedialog
from datetime import timedelta
import datetime, time
import subprocess, sys, os


class FloatingWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.center()
        self.wait_visibility(self)
        self.wm_attributes('-alpha',0.55)

        self.label = tk.Label(self, text="Drag corners over capture area\nClick 'Apply Area' or press 'ENTER' when ready")
        self.label.pack(side="top", fill="both", expand=True)

        self.grip_se = tk.Label(self, text="  ",bg='blue',fg='blue',cursor="cross")
        self.grip_se.place(relx=1.0, rely=1.0, anchor="se")
        self.grip_se.bind("<B1-Motion>",lambda e, mode='se':self.OnMotion(e,mode))

        self.grip_e = tk.Label(self,text="  ",bg='green',fg='green',cursor="cross")
        self.grip_e.place(relx=1.0, rely=0.5, anchor="e")
        self.grip_e.bind("<B1-Motion>",lambda e, mode='e':self.OnMotion(e,mode))
        
        self.grip_ne = tk.Label(self,text="  ",bg='blue',fg='blue',cursor="cross")
        self.grip_ne.place(relx=1.0, rely=0, anchor="ne")
        self.grip_ne.bind("<B1-Motion>",lambda e, mode='ne':self.OnMotion(e,mode))

        self.grip_n = tk.Label(self,text="  ",bg='green',fg='green',cursor="cross")
        self.grip_n.place(relx=0.5, rely=0, anchor="n")
        self.grip_n.bind("<B1-Motion>",lambda e, mode='n':self.OnMotion(e,mode))

        self.grip_nw = tk.Label(self,text="  ",bg='blue',fg='blue',cursor="cross")
        self.grip_nw.place(relx=0, rely=0, anchor="nw")
        self.grip_nw.bind("<B1-Motion>",lambda e, mode='nw':self.OnMotion(e,mode))

        self.grip_w = tk.Label(self,text="  ",bg='green',fg='green',cursor="cross")
        self.grip_w.place(relx=0, rely=0.5, anchor="w")
        self.grip_w.bind("<B1-Motion>",lambda e, mode='w':self.OnMotion(e,mode))

        self.grip_sw = tk.Label(self,text="  ",bg='blue',fg='blue',cursor="cross")
        self.grip_sw.place(relx=0, rely=1, anchor="sw")
        self.grip_sw.bind("<B1-Motion>",lambda e, mode='sw':self.OnMotion(e,mode))

        self.grip_s = tk.Label(self,text="  ",bg='green',fg='green',cursor="cross")
        self.grip_s.place(relx=0.5, rely=1, anchor="s")
        self.grip_s.bind("<B1-Motion>",lambda e, mode='s':self.OnMotion(e,mode))

    def OnMotion(self, event, mode):
        abs_x = self.winfo_pointerx() - self.winfo_rootx()
        abs_y = self.winfo_pointery() - self.winfo_rooty()
        width = self.winfo_width()
        height= self.winfo_height()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        
        if mode == 'se' and abs_x >0 and abs_y >0:
                self.geometry("%sx%s" % (abs_x,abs_y))
                
        if mode == 'e':
            if height >0 and abs_x >0:
                self.geometry("%sx%s" % (abs_x,height))

        if mode == 'ne' and abs_x >0:
                y = y+abs_y
                height = height-abs_y
                if height >0:
                    self.geometry("%dx%d+%d+%d" % (abs_x,height,x,y))

        if mode == 'n':
            height=height-abs_y
            y = y+abs_y
            if height >0 and width >0:
                self.geometry("%dx%d+%d+%d" % (width,height,x,y))
            
        if mode == 'nw':
            width = width-abs_x
            height=height-abs_y
            x = x+abs_x
            y = y+abs_y
            if height >0 and width >0:
                self.geometry("%dx%d+%d+%d" % (width,height,x,y))

        if mode == 'w':
            width = width-abs_x
            x = x+abs_x
            if height >0 and width >0:
                self.geometry("%dx%d+%d+%d" % (width,height,x,y))

        if mode == 'sw':
            width = width-abs_x
            height=height-(height-abs_y)
            x = x+abs_x
            if height >0 and width >0:
                self.geometry("%dx%d+%d+%d" % (width,height,x,y))

        if mode == 's':
            height=height-(height-abs_y)
            if height >0 and width >0:
                self.geometry("%dx%d+%d+%d" % (width,height,x,y))

    def center(self):
        width = 300
        height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width/2) - (width/2)
        y_coordinate = (screen_height/2) - (height/2)
        self.geometry("%dx%d+%d+%d" % (width, height, x_coordinate, y_coordinate))

    def coords(self):
        return (self.winfo_rootx(), self.winfo_rooty(), self.winfo_width(), self.winfo_height())

class Pulse_Audio_Devices:
    def __init__(self) -> None:
        self.sources = self.get_sources()

    def get_sources(self):
        shell_command = f"pactl list sources | grep 'Name: '"
        try:
            device_list = os.popen(shell_command).readlines()
        except BaseException as error:
            print('Exception using pactl to determine Pulse Audio sources!')
            print('To use Pulse Audio (if installed) pactl needs to be installed!')
            print(f'Error: {error}')
        paudio_devs = []
        for e in device_list:
            paudio_devs.append(e.split()[1])
        return paudio_devs

class gui:

    def __init__(self):
        self.root = tk.Tk()
        self.out_path = sys.path[0]
        self.format = "mp4"
        self.encoder = "default"
        self.sound_server = "Alsa"
        self.sound_device = "default"
        self.recorder = None
        self.recorder_options = {}
        self.selectionArea = (0, 0, 0, 0)
        self.timer = False
        self.pulseAudio = Pulse_Audio_Devices()
        self.gui_create()
        self.root.protocol("WM_DELETE_WINDOW", self.cleanUp)
        self.root.mainloop()

    def createSelectionWindow(self):
        self.floater = FloatingWindow()
        self.button1.config(state=DISABLED)
        self.button2.config(state=DISABLED)
        self.button_apply.config(state=NORMAL)
        self.fullscreen_toggle.config(state=DISABLED)
        self.root.bind('<Return>', self.applySelectionWindow)

    def applySelectionWindow(self, event=None):
        self.root.unbind('<Return>')
        self.selectionArea = self.floater.coords()
        self.floater.destroy()
        self.updateRecordingArea()
        self.button1.config(state=NORMAL)
        self.button_apply.config(state=DISABLED)
        self.button2.config(state=NORMAL)
        self.fullscreen_toggle.config(state=NORMAL)
        self.status_bar.configure(text="Ready")

    def updateRecordingArea(self):
        self.area_data.config(text=f"X: {self.selectionArea[0]}\nY: {self.selectionArea[1]}\nWidth: {self.selectionArea[2]}\nHight: {self.selectionArea[3]}")

    def startRecording(self):
        self.on_Record_Start()
        path = self.input_variable.get()
        rate = self.framerate_spinbox.get()
        self.recorder_options['time'] = self.timer_var.get()
        self.recorder_options['winid'] = self.winid_var.get()
        self.recorder = Actions(self.selectionArea, path, self.format, self.encoder, rate, self.recorder_options, self.sound_server, self.sound_device)
        self.root.after(1000, self.updateStatus)

    def stopRecording(self):
        self.recorder.stop_recording()
        del self.recorder
        self.recorder = None
        self.on_Record_Stop()
        self.status_bar.configure(text="Recording Stopped")

    def on_Record_Start(self):
        self.button3.config(state=NORMAL)
        self.button2.config(state=DISABLED)
        self.button1.config(state=DISABLED)
        self.fullscreen_toggle.config(state=DISABLED)
        self.timer_entry.config(state=DISABLED)
        self.timer_toggle.config(state=DISABLED)
        self.mouse_toggle.config(state=DISABLED)
        self.border_toggle.config(state=DISABLED)
        self.winid_entry.config(state=DISABLED)
        self.winid_toggle.config(state=DISABLED)
        self.path_entry.config(state=DISABLED)
        self.path_sel_btn.config(state=DISABLED)
        self.sound_server_menu.config(state=DISABLED)
        self.sound_device_menu.config(state=DISABLED)
        self.container_menu.config(state=DISABLED)
        self.encoder_select.config(state=DISABLED)
        self.framerate_spinbox.config(state=DISABLED)

    def on_Record_Stop(self):
        self.button2.config(state=NORMAL)
        self.fullscreen_toggle.config(state=NORMAL)
        self.button3.config(state=DISABLED)
        self.mouse_toggle.config(state=NORMAL)
        self.border_toggle.config(state=NORMAL)
        self.timer_toggle.config(state=NORMAL)
        self.winid_toggle.config(state=NORMAL)
        self.path_entry.config(state=NORMAL)
        self.path_sel_btn.config(state=NORMAL)
        self.sound_server_menu.config(state=NORMAL)
        self.sound_device_menu.config(state=NORMAL)
        self.container_menu.config(state=NORMAL)
        self.encoder_select.config(state=NORMAL)
        self.framerate_spinbox.config(state=NORMAL)
        if self.recorder_options['timer']:
            self.timer_entry.config(state=NORMAL)
        if self.recorder_options['record_window']:
            self.winid_entry.config(state=NORMAL)
        else:
            self.fullscreen_toggle.config(state=NORMAL)
            if self.toggle_var.get() == 0:
                self.button1.config(state=NORMAL)

    def outputPathSelection(self):
        self.out_path = filedialog.askdirectory()
        self.path_entry.delete(0,END)
        self.path_entry.insert(END, self.out_path)

    def formateSelect(self, e):
        self.format = e
        self.container_menu.config(text=f"{e}")

    def encoderSelect(self, e):
        self.encoder = e
        self.encoder_select.config(text=f"{e}")

    def soundServerSelect(self, e):
        gbc = '#0e345b'  # '#395f79'
        txc = '#e7e6e6'  # '#efefef'

        self.sound_server = e
        self.sound_server_menu.config(text=f"{e}")
        if e == 'Alsa':
            sound_dev_list = ['default']
        else:
            sound_dev_list = self.pulseAudio.sources

        # creating a new menu for audio device selection
        inside_menu = tk.Menu(self.sound_device_menu, background=gbc, foreground=txc)
        item_var = tk.StringVar()
        for e in sound_dev_list:
            inside_menu.add_radiobutton(label=e, variable=item_var, command=lambda e=e: self.soundDeviceSelect(e))
        self.sound_device_menu["menu"] = inside_menu

    def soundDeviceSelect(self, e):
        self.sound_device = e
        self.sound_device_menu.config(text=f'{e}')

    def toggleFullscreen(self):
        if self.toggle_var.get() == 1:
            self.selectionArea = (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            self.updateRecordingArea()
            self.button1.config(state=DISABLED)
            self.button2.config(state=NORMAL)
            self.status_bar.configure(text="Ready")
        else:
            self.button1.config(state=NORMAL)

    def toggleMouse(self):
        if self.mousetoggle_var.get() == 1:
            self.recorder_options['mouse'] = True
        else:
            self.recorder_options['mouse'] = False

    def toggleTimer(self):
        if self.timertoggle_var.get() == 1:
            self.timer_entry.config(state=NORMAL)
            self.recorder_options['timer'] = True
            self.timer = True
        else:
            self.timer_entry.config(state=DISABLED)
            self.recorder_options['timer'] = False
            self.timer = False

    def toggleBorders(self):
        if self.bordertoggle_var.get() == 1:
            self.recorder_options['borders'] = True
        else:
            self.recorder_options['borders'] = False

    def toggleWinID(self):
        if self.winidtoggle_var.get() == 1:
            self.winid_entry.config(state=NORMAL)
            self.button2.config(state=NORMAL)
            self.button1.config(state=DISABLED)
            self.fullscreen_toggle.config(state=DISABLED)
            self.recorder_options['record_window'] = True
        else:
            self.winid_entry.config(state=DISABLED)
            self.button1.config(state=NORMAL)
            self.fullscreen_toggle.config(state=NORMAL)
            self.recorder_options['record_window'] = False
            if self.selectionArea == (0, 0, 0, 0):
                self.button2.config(state=DISABLED)

    def recording(self):
        # test if recorder was already created, when recording is currently running
        if self.recorder != None:
            return True
        else:
            return False

    def cleanUp(self):
        if self.recording():
            self.stopRecording()
        self.root.destroy()

    def updateStatus(self):
        now = int(time.time())
        if self.recorder_options['timer'] and self.recording():
            if now > self.recorder.stop_time:
                self.stopRecording()
        if self.recording():
            time_now = int(str(now).split('.')[0])
            time_dif = time_now - self.recorder.recordingSince
            time_elapsed = "{:0>8}".format(str(timedelta(seconds=time_dif)))
            msg = "Recording since: " + time_elapsed
            self.status_bar.configure(text=msg)
            self.root.after(1000, self.updateStatus)

    def gui_create(self):

        # color definitions
        gbc = '#0e345b'  # '#395f79'
        abc = '#5d8ec1'  # '#a6cfe5'
        txc = '#e7e6e6'  # '#efefef'

        self.root.resizable(False, False)
        self.root.title(f"ScreenGrab v{version}")
        self.root.configure(background=gbc)


        # Path selection
        self.path_frame = tk.LabelFrame(self.root, text="Video Output Directory", background=gbc, foreground=txc)
        self.path_frame.grid(row=0, column=0, sticky=tk.EW, padx=5)

        self.input_variable = tk.StringVar()
        self.path_entry = tk.Entry(self.path_frame, textvariable=self.input_variable, width=45)
        self.path_entry.insert(END, self.out_path)
        self.path_entry.grid(row=0, column=0, padx=5, pady=5)

        self.path_sel_btn = tk.Button(self.path_frame, text="Select", width=5, relief='raised', background=gbc, foreground=txc, activebackground=abc, command=self.outputPathSelection)
        self.path_sel_btn.grid(row=0, column=1, sticky=tk.EW, padx=5)

        #Audio Device Selection
        self.audio_setting_frame = tk.LabelFrame(self.root, text="Audio Device Selection", background=gbc, foreground=txc)
        self.audio_setting_frame.grid(row=1, sticky=tk.EW, padx=5)

        self.sound_server_lable = tk.Label(self.audio_setting_frame, text="Sound Server:", background=gbc, foreground=txc)
        self.sound_server_lable.grid(row=0, column=0, padx=5, pady=(5,3))

        self.sound_device_lable = tk.Label(self.audio_setting_frame, text="Sound Device:", background=gbc, foreground=txc)
        self.sound_device_lable.grid(row=0, column=1, padx=5, pady=(5,3))

        self.sound_server_menu = tk.Menubutton(self.audio_setting_frame, text=f"{self.sound_server}", width=10, relief='raised', background=gbc, foreground=txc, activebackground=abc)
        sound_server_list = ['Alsa', 'Pulse']
        inside_menu = tk.Menu(self.sound_server_menu, background=gbc, foreground=txc)
        item_var = tk.StringVar()
        for e in sound_server_list:
            inside_menu.add_radiobutton(label=e, variable=item_var, command=lambda e=e: self.soundServerSelect(e))
        self.sound_server_menu["menu"] = inside_menu
        self.sound_server_menu.grid(row=1, column=0, padx=15, pady=(0,5))

        self.sound_device_menu = tk.Menubutton(self.audio_setting_frame, text=f"{self.sound_device}", width=10, relief='raised', background=gbc, foreground=txc, activebackground=abc)
        sound_device_list = ["default"]
        inside_menu = tk.Menu(self.sound_device_menu, background=gbc, foreground=txc)
        item_var = tk.StringVar()
        for e in sound_device_list:
            inside_menu.add_radiobutton(label=e, variable=item_var, command=lambda e=e: self.soundDeviceSelect(e))
        self.sound_device_menu["menu"] = inside_menu
        self.sound_device_menu.grid(row=1, column=1, padx=15, pady=(0,5))

        #Video Settings
        self.vsetting_frame = tk.LabelFrame(self.root, text="Video Settings", background=gbc, foreground=txc)
        self.vsetting_frame.grid(row=2, sticky=tk.EW, padx=5)

        self.container_label = tk.Label(self.vsetting_frame, text="Container Format:", background=gbc, foreground=txc)
        self.container_label.grid(row=0, column=0, padx=5, pady=(5,3))

        self.container_menu = tk.Menubutton(self.vsetting_frame, text=f"{self.format}", width=10, relief='raised', background=gbc, foreground=txc, activebackground=abc)
        formats_list = ["mp4", "mkv", "mpeg", "avi"]
        inside_menu = tk.Menu(self.container_menu, background=gbc, foreground=txc)
        item_var = tk.StringVar()
        for e in formats_list:
            inside_menu.add_radiobutton(label=e, variable=item_var, command=lambda e=e: self.formateSelect(e))
        self.container_menu["menu"] = inside_menu
        self.container_menu.grid(row=1, column=0, padx=5, pady=(0,5))

        self.encoder_label = tk.Label(self.vsetting_frame, text="Encoder:", background=gbc, foreground=txc)
        self.encoder_label.grid(row=0, column=1, padx=5, pady=(5,3))

        self.encoder_select = tk.Menubutton(self.vsetting_frame, text=f"{self.encoder}", width=10, relief='raised', background=gbc, foreground=txc, activebackground=abc)
        encoders_list = ["default", "libx264", "libx264rgb", "libx265", "h264_nvenc", "hevc_nvenc", "mpeg4"]
        inside_menu = tk.Menu(self.encoder_select, background=gbc, foreground=txc)
        item_var = tk.StringVar()
        for e in encoders_list:
            inside_menu.add_radiobutton(label=e, variable=item_var, command=lambda e=e: self.encoderSelect(e))
        self.encoder_select["menu"] = inside_menu
        self.encoder_select.grid(row=1, column=1, padx=5, pady=(0,5))

        self.framerate_label = tk.Label(self.vsetting_frame, text="Framerate:", background=gbc, foreground=txc)
        self.framerate_label.grid(row=0, column=3, padx=5, pady=(0,0))

        self.framerate_spinbox = tk.Spinbox(self.vsetting_frame, width=2, from_=10, to=60, background=gbc, foreground=txc, buttonbackground=gbc)
        self.framerate_spinbox.delete(0,"end")
        self.framerate_spinbox.insert(0,30)   # set initial framerate to 30
        self.framerate_spinbox.grid(row=1, column=3, padx=27, pady=(0,5))


        # Recording Area Selection
        self.selection_frame = tk.LabelFrame(self.root, text="Recording Area", background=gbc, foreground=txc)
        self.selection_frame.grid(row=3, sticky=tk.EW, padx=5)

        self.area_label = tk.Label(self.selection_frame, text="Selected Area:", background=gbc, foreground=txc)
        self.area_label.grid(row=0, column=0, padx=5, pady=5)

        self.area_data = tk.Label(self.selection_frame, text=f"X: {self.selectionArea[0]}\nY: {self.selectionArea[1]}\nWidth: {self.selectionArea[2]}\nHight: {self.selectionArea[3]}", background=gbc, foreground=txc)
        self.area_data.grid(row=0, column=1, padx=5, pady=5)

        self.button1 = tk.Button(self.selection_frame, text="Select Area", width=15, command=self.createSelectionWindow, background=gbc, foreground=txc, activebackground=abc)
        self.button1.grid(row=1, column=0, padx=5, pady=5)

        self.button_apply = tk.Button(self.selection_frame, text="Apply Area", width=15, state=DISABLED,command=self.applySelectionWindow, background=gbc, foreground=txc, activebackground=abc)
        self.button_apply.grid(row=1, column=1, padx=5, pady=5)

        self.toggle_var = tk.IntVar()
        self.fullscreen_toggle = tk.Checkbutton(self.selection_frame, text="Fullscreen", variable=self.toggle_var, onvalue=1, offvalue=0, command=self.toggleFullscreen, background=gbc, foreground=txc, activebackground=abc, selectcolor=gbc)
        self.fullscreen_toggle.grid(row=1, column=3, padx=(20,0))


        # Recording Controls
        self.button_frame = tk.LabelFrame(self.root, text="Recording Controls", background=gbc, foreground=txc)
        self.button_frame.grid(row=4, padx=5, sticky=tk.EW, pady=(0,5))

        #mouse
        self.mousetoggle_var = tk.IntVar()
        self.mouse_toggle = tk.Checkbutton(self.button_frame, text="Hide Mouse", variable=self.mousetoggle_var, onvalue=1, offvalue=0, command=self.toggleMouse, background=gbc, foreground=txc, activebackground=abc, selectcolor=gbc)
        self.mouse_toggle.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.recorder_options['mouse'] = False

        #borders
        self.bordertoggle_var = tk.IntVar()
        self.border_toggle = tk.Checkbutton(self.button_frame, text="Show Borders", variable=self.bordertoggle_var, onvalue=1, offvalue=0, command=self.toggleBorders, background=gbc, foreground=txc, activebackground=abc, selectcolor=gbc)
        self.border_toggle.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.recorder_options['borders'] = False

        #winid
        self.winidtoggle_var = tk.IntVar()
        self.winid_toggle = tk.Checkbutton(self.button_frame, text="Record Win ID", variable=self.winidtoggle_var, onvalue=1, offvalue=0, command=self.toggleWinID, background=gbc, foreground=txc, activebackground=abc, selectcolor=gbc)
        self.winid_toggle.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.recorder_options['record_window'] = False

        self.winid_var = tk.StringVar()
        self.winid_entry = tk.Entry(self.button_frame, textvariable=self.winid_var, justify=tk.CENTER,  insertofftime=0, width=9)
        self.winid_entry.config(state=DISABLED)
        self.winid_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)

        #timer
        self.timertoggle_var = tk.IntVar()
        self.timer_toggle = tk.Checkbutton(self.button_frame, text="Recording Timer", variable=self.timertoggle_var, onvalue=1, offvalue=0, command=self.toggleTimer, background=gbc, foreground=txc, activebackground=abc, selectcolor=gbc)
        self.timer_toggle.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.recorder_options['timer'] = False

        self.timer_var = tk.StringVar()
        self.timer_entry = tk.Entry(self.button_frame, textvariable=self.timer_var, justify=tk.CENTER,  insertofftime=0, width=9)
        self.timer_entry.insert(END, 'HH:MM:SS')
        self.timer_entry.config(state=DISABLED)
        self.timer_entry.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)

        #recording buttons
        self.button2 = tk.Button(self.button_frame, text="Start", width=15, state=DISABLED, command=self.startRecording, background=gbc, foreground='yellow', activebackground=abc)
        self.button2.grid(row=4, column=1, padx=5, pady=5)

        self.button3 = tk.Button(self.button_frame, text="Stop", width=15, state=DISABLED, command=self.stopRecording, background=gbc, foreground='red', activebackground='red')
        self.button3.grid(row=4, column=2, padx=5, pady=5)


        # Status Bar
        self.status_bar = tk.Label(self.root, text="Select Recording Area", relief=FLAT, anchor=W, foreground="black", border=1)
        self.status_bar.grid(row=5, column=0, sticky=EW, columnspan=3)

class Actions:
    def __init__(self, selectionArea, path, format, encoder, rate, recorder_options, sound_server, sound_device):
        self.x = selectionArea[0]
        self.y = selectionArea[1]
        self.width = selectionArea[2]
        self.height = selectionArea[3]
        self.recorder_options = recorder_options
        self.ffmpeg_bin = 'ffmpeg' # set path to prefered ffmpeg binary, leave it at 'ffmpeg' for default system-wide ffmpeg found via $PATH
        self.out_path = path
        self.format = format
        self.encoder = encoder
        self.sound_server = sound_server
        self.sound_device = sound_device
        self.framerate = rate
        self.recordingSince = int(str(time.time()).split('.')[0])   # get current time in seconds
        self.pid = 0
        self.stop_time = 0
        self.encoder_option = {"default":"", \
                                "libx264":"-c:v libx264 -preset faster -crf 17", \
                                "libx264rgb":"-c:v libx264rgb -crf 0 -preset ultrafast -color_range 2", \
                                "h264_nvenc":"-c:v h264_nvenc -preset fast", \
                                "hevc_nvenc":"-c:v hevc_nvenc -preset fast", \
                                "libx265":"-c:v libx265 -preset faster -crf 17", \
                                "mpeg4":"-c:v mpeg4 -vtag xvid -qscale:v 3"}
        self.start_recording()

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def timestr_to_seconds(self, timestr):
        return sum(x * int(t) for x, t in zip([3600, 60, 1], timestr.split(":")))

    def get_pid_array(self):
        ps_command = f"ps aux | grep ffmpeg | grep -v grep"
        proc_list = os.popen(ps_command).readlines()
        tmp_list = []
        self.pid_array = []
        #remove \n from line
        for line in proc_list:
            tmp_list.append(line.strip())
        #select only screengrab ffmpeg proccesses
        for line in tmp_list:
            if (self.shell_command in line):
                self.pid_array.append(int(line.split()[1]))

    def get_display(self):
        cmd = "echo $DISPLAY"
        display = os.popen(cmd).readline().strip()
        return display

    def stop_recording(self):
        pid = str(self.pid)
        os.system(f"kill -2 {pid}")  # kill actual ffmpeg process, send 'CTRL + C'
        self.p.terminate()
        self.p.wait()
        
    def formatPath(self, path):
        if path[-1] != "/":
            path = path + "/"
        return path
    
    def get_recording_options(self):
        show_mouse = '1'
        borders = '0'
        if self.recorder_options['mouse']:
            show_mouse = '0'
        if self.recorder_options['borders']:
            borders = '1'
        if self.recorder_options['record_window']:
            winid = self.recorder_options['winid']
            options = f'-draw_mouse {show_mouse} -window_id {winid}'
        else:
            options = f'-show_region {borders} -draw_mouse {show_mouse}'
        return options
    
    def set_timer(self):
        if self.recorder_options['timer']:
            now = time.time()
            ttl = self.timestr_to_seconds(self.recorder_options['time'])
            self.stop_time = int(now) + ttl

    def start_recording(self):
        self.set_timer()
        path = self.formatPath(self.out_path)
        tail = " >> ffmpeg_err.log 2>&1"
        filename = "screengrab_{timestamp}".format(timestamp=self.get_timestamp())
        encoder_option = self.encoder_option[self.encoder]
        recording_options = self.get_recording_options()   # show mouse pointer | show recording region
        display = self.get_display()
        output_info = f" '{path}{filename}.{self.format}'"
        if self.recorder_options['winid']:
            self.shell_command = f"{self.ffmpeg_bin} -loglevel error -nostats -f x11grab {recording_options} -framerate {self.framerate} -i {display} -f {self.sound_server} -i {self.sound_device} {encoder_option}"
        else:
            self.shell_command = f"{self.ffmpeg_bin} -loglevel error -nostats -f x11grab {recording_options} -framerate {self.framerate} -video_size {self.width}x{self.height} -i {display}+{self.x},{self.y} -f {self.sound_server} -i {self.sound_device} {encoder_option}"

        cmd = self.shell_command + output_info + tail
        self.p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        self.get_pid_array()
        self.pid = max(self.pid_array)

def main():
    gui()

if __name__ == "__main__":
    main()
