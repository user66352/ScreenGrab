## What it is
  
ScreenGrab is a simple python tkinter GUI for ffmpeg and Linux.  
It's meant to simplify screen recordings with ffmpeg under X11.  
  
  
## Features
  
4 basic video settings are available.
  
1. Formate
 * selects the video output format (mp4, mkv, mpeg, avi)
 * mpeg and avi are meant to be used with the mpeg4 encoder
2. Encoder
 * select the video encoder to use for the output video
 * all encoder settings are aiming to be less CPU hungry and creating good/acceptable quality output but with a lower compression ratio
 * exception is 'libx264rgb', thats meant to act as a 'lossless' recorder
 * the 'default' encoder is using the ffmpeg defaults for x11grab, in case of doubt just use this (libx264 encoding)
3. Framerate
 * sets the capture framerate
4. Recording Area
 * either 'Fullscreen' or an selected area
  
### New in Ver. 0.4.0
  
4 additional functions under 'Recording Controls'
  
1. Hide Mouse
 * it prevents ffmpeg from recording the mouse pointer
2. Show Borders
 * shows the borders of the selected recording area while recording is running
3. Record Win ID
 * it will record an X11 window specified by its ID
 * the ID of a specific window can be found with `xwininfo`
 * the window itself can be in the background but should not be minimized or resized while recording
4. Recording Timer
 * set a time for how long ScreenGrab should keep recording
 * when the specified time has elapsed recording will stop
 * to record for 1hr 25min and 5sec enter '01:25:05'
  
A binary is now included that was created with 'PyInstaller'.
It should run on a 64bit X11 Linux Desktop.
  
### New in Ver. 0.5.1  
  
* added Sound Controls  
  - no Sound Device other than 'default' selectable with Alsa  
  - with Pulse Audio you have to choose a sound device manual, none is auto-selected  
  - select one of the '*.monitor' devices to record system sound from speakers/headphones  
* minor changes in GUI behavior  
  
### New in Ver. 0.5.2  
  
* selection window is now movable  
* selection window is reopened with the previously selected coordinates  
* minor tweaks to look and feel  
  
  
## Requirements

Since ffmpeg is used for the actual screen recording, ffmpeg must be installed.  

ScreenGrab should work out-of-the box on a standard Python3 installation.  
The following modules are used: tkinter, datetime, subprocess, sys, os  
If 'subprocess' for example is missing, you can install it via '`python3 -m pip install subprocess`'.  
  
To make use of the Nvidia hardware encoders (h264\_nvenc, hevc\_nvenc) a supported Nvidia card must be installed.  
Also ffmpeg must be compiled with those encoders enabled. That can be checked with '`ffmpeg -encoders | grep nvenc`'.  
I run that successfully on Debian 12 with the standard Nvidia drivers coming with Debian.  
  
  
## Notes
  
If the captured video did not record any sound, ffmpeg probably picked a different audio device.  
The solution could be to disable all sound devices except your headphone or standard speakers.  
Or open the audio controls with '`pavucontrol`'.  
Start screen recording with ScreenGrab. That will launch ffmpeg.  
Once ffmpeg is running switch to the 'pavucontrol' window and open the tab 'Recording'.  
You should see something like 'ALSA plug-in [ffmpeg]: ALSA Capture *from*'  
To the right you have a selection menu. Select the audio device you want ffmpeg to record from along with your video.  
  
If multiple monitors are connected, ffmpeg probably will record both monitors if 'Fullscreen' is selected.  
In this case you need to select the screen you want to capture manually with 'Select Area'.  