import getopt
from datetime import datetime
import json
import time
import os
# https://onion.io/2bt-pid-control-python/
import PID
import queue
import threading
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from w1thermsensor import W1ThermSensor
import RPi.GPIO as gpio


BREWING_HEATER_BIT = 17
BOILING_HEATER_BIT = 18
PUMP1_BIT = 19
PUMP2_BIT = 20

heating_running = False
heating_thread = None

heating_power = 5.0
brewing_running = False
brewing_thread = None
brewing_elapsed_time = 0.0
brewing_heating_level = 0.0
boiling_running = False
boiling_thread = None
boiling_heating_level = 0.0
cooling_running = False
cooling_thread = None

pump1_speed = 0.0 # from 0.0 - 1.0
pump2_speed = 0.0


annotation_tags = ([])
xref = ([])

temp_q = queue.Queue()
setpoint_q = queue.Queue()
idx = 0
plot_temp = np.zeros(1)
plot_time = np.zeros(1)
plot_setp = np.zeros(1)
plot_powr = np.zeros(1)
clear_plot = False


def plotting(args):
    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = plt.axes(xlim=(0, int(np.sum(settings["brewing_time"]))), ylim=(20.0, max(settings["brewing_temp"])+10.0))
    plt.xlabel('Time [mimn]')
    plt.ylabel('Temp [C]')
    plotlays, plotcolors = [3], ["black","red", "green"]
    lines = []
    for index in range(3):
        lobj = ax.plot([], [], lw=1, color=plotcolors[index])[0]
        lines.append(lobj)

    # initialization function: plot the background of each frame
    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    # animation function.  This is called sequentially
    def animate(i):
        global idx
        global plot_temp, plot_time, plot_setp, plot_powr, clear_plot
        if clear_plot:
            clear_plot = False
            idx = 0
            plot_temp = []
            plot_time = []
            plot_setp = []
            plot_powr = []
        point = temp_q.get()
        plot_temp = np.append(plot_temp,point[1])
        plot_time = np.append(plot_time, point[0]/60.0)
        plot_setp = np.append(plot_setp, point[2])
        plot_powr = np.append(plot_powr, 20.0 + point[3]*(max(settings["brewing_temp"])+10.0-20.0))
        idx += 1
        xlist = [plot_time, plot_time, plot_time]
        ylist = [plot_temp, plot_setp, plot_powr]
        for lnum, line in enumerate(lines):
            line.set_data([xlist[lnum], ylist[lnum]])
        return lines

        #temp_line.set_data(plot_time, plot_temp)
        #setp_line.set_data(plot_time, plot_temp)
        #return setp_line,

    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   interval=20, blit=True)

    plt.show()


def temperature_thread( a ):
    while True:
        heating_temp.set(heating_sensor.get_temperature())
        heating_current['text'] = heating_sensor.get_temperature()
        brewing_temp.set(brewing_sensor.get_temperature())
        brewing_current['text'] = brewing_sensor.get_temperature()
        cooling_temp.set(cooling_sensor.get_temperature())
        cooling_current['text'] = cooling_sensor.get_temperature()
        time.sleep(0.5)

def brewing_heater_thread( port ):
    full_time = 1.0
    while True:
        power = min(brewing_heating_level, 1.0)
        info_brewing_heater["text"] = str(power)
        if power == 1.0:
            gpio.output(BREWING_HEATER_BIT, gpio.LOW)
            time.sleep(full_time)
        else:
            gpio.output(BREWING_HEATER_BIT, gpio.LOW)
            time.sleep(power*full_time)
            gpio.output(BREWING_HEATER_BIT, gpio.HIGH)
            time.sleep((1.0-power)*full_time)

def boiling_heater_thread( port ):
    full_time = 1.0
    while True:
        power = min(boiling_heating_level, 1.0)
        info_boiling_heater["text"] = str(power)
        if power == 1.0:
            gpio.output(BOILING_HEATER_BIT, gpio.LOW)
            time.sleep(full_time)
        else:
            gpio.output(BOILING_HEATER_BIT, gpio.LOW)
            time.sleep(power*full_time)
            gpio.output(BOILING_HEATER_BIT, gpio.HIGH)
            time.sleep((1.0-power)*full_time)

def pump1_thread( port ):
    full_time = 1.0
    while True:
        power = min(pump1_speed, 1.0)
        info_pump1["text"] = str(power)
        if power == 1.0:
            gpio.output(PUMP1_BIT, gpio.LOW)
            time.sleep(full_time)
        else:
            gpio.output(PUMP1_BIT, gpio.LOW)
            time.sleep(power*full_time)
            gpio.output(PUMP1_BIT, gpio.HIGH)
            time.sleep((1.0-power)*full_time)

def pump2_thread( port ):
    full_time = 1.0
    while True:
        power = min(pump2_speed, 1.0)
        info_pump2["text"] = str(power)
        if power == 1.0:
            gpio.output(PUMP2_BIT, gpio.LOW)
            time.sleep(full_time)
        else:
            gpio.output(PUMP2_BIT, gpio.LOW)
            time.sleep(power*full_time)
            gpio.output(PUMP2_BIT, gpio.HIGH)
            time.sleep((1.0-power)*full_time)

def speach_message(txt_msg):
    os.system('echo "{0}" | festival --tts'.format(txt_msg))


def update_settings(*args):
    heating_setpoint.set(str(settings["heating_setpoint"]))
    brewing_time1.set(str(settings["brewing_time"][0]))
    brewing_time2.set(str(settings["brewing_time"][1]))
    brewing_time3.set(str(settings["brewing_time"][2]))
    brewing_time4.set(str(settings["brewing_time"][3]))
    brewing_temp1.set(str(settings["brewing_temp"][0]))
    brewing_temp2.set(str(settings["brewing_temp"][1]))
    brewing_temp3.set(str(settings["brewing_temp"][2]))
    brewing_temp4.set(str(settings["brewing_temp"][3]))
    brewing_kp.set(str(settings["brewing_kp"]))
    brewing_ki.set(str(settings["brewing_ki"]))
    brewing_kd.set(str(settings["brewing_kd"]))
    brewing_use_pid.set(str(settings["brewing_pid"]))
    brewing_increase_lim.set(str(settings["brewing_increase_lim"]))
    brewing_decrease_lim.set(str(settings["brewing_decrease_lim"]))
    brewing_pump_speed.set(str(settings["brewing_pump_speed"]))
    boiling_heating_power.set(str(settings["boiling_heating_power"]))
    cooling_setpoint.set(str(settings["cooling_setpoint"]))
    cooling_kp.set(str(settings["cooling_kp"]))
    cooling_ki.set(str(settings["cooling_ki"]))

def set_settings(*args):
    settings["heating_setpoint"] = float(heating_setpoint.get())
    settings["brewing_time"][0] = int(brewing_time1.get())
    settings["brewing_time"][1] = int(brewing_time2.get())
    settings["brewing_time"][2] = int(brewing_time3.get())
    settings["brewing_time"][3] = int(brewing_time4.get())
    settings["brewing_temp"][0] = int(brewing_temp1.get())
    settings["brewing_temp"][1] = int(brewing_temp2.get())
    settings["brewing_temp"][2] = int(brewing_temp3.get())
    settings["brewing_temp"][3] = int(brewing_temp4.get())
    settings["brewing_pid"] = float(brewing_use_pid.get())
    settings["brewing_kp"] = float(brewing_kp.get())
    settings["brewing_ki"] = float(brewing_ki.get())
    settings["brewing_kd"] = float(brewing_kd.get())
    settings["brewing_increase_lim"] = float(brewing_increase_lim.get())
    settings["brewing_decrease_lim"] = float(brewing_decrease_lim.get())
    settings["brewing_pump_speed"] = float(brewing_pump_speed.get())
    settings["cooling_setpoint"] = float(cooling_setpoint.get())
    settings["cooling_kp"] = float(cooling_kp.get())
    settings["cooling_ki"] = float(cooling_ki.get())

def read_settings(*args):
    global settings
    global selected_settings

    filename = filedialog.askopenfilename(defaultextension='.json')
    if not filename: return
    try:
        with open(filename, 'r+') as infile:
            settings = json.load(infile)
            print(str.split(str.split(filename,".")[0], "/")[-1])
            selected_settings.set(str.split(str.split(filename,".")[0], "/")[-1])
            update_settings()
    except Exception as e:
        #raise
        messagebox.showerror('Error Loading settings file', 'Unable to open file: %r' % filename)


def save_settings(*args):
    #global resultsContents
    #global base_directory

    filename = filedialog.asksaveasfilename(defaultextension='.json')
    if not filename: return
    try:
        if filename.endswith('.json'):
            with open(filename, 'w') as outfile:
                set_settings()
                json.dump(settings, outfile)
                selected_settings.set(str.split(str.split(filename, ".")[0], "/")[-1])
        else:
            messagebox.showerror('Error Saving settings', "Not .lson extention")
    except Exception as e:
        messagebox.showerror('Error Saving settings', 'Unable to open file: %r' % filename)
def heating():
    global heating_running
    global heating_thread
    start_time = time.time()
    last_time = time.time()
    while heating_running:
        # Print elapsed time
        if time.time() - last_time > 1.:
            elapsed_time = time.time()-start_time
            heating_elapsed_time.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
            last_time = time.time()
        time.sleep(0.1)

def heating_start(*args):
    global heating_running
    global heating_thread
    speach_message("Heating started")
    heating_running_label.configure(text="Running", foreground="red")
    heating_stop_button.configure(state=NORMAL)
    heating_start_button.configure(state=DISABLED)
    brewing_start_button.configure(state=DISABLED)
    boiling_start_button.configure(state=DISABLED)
    cooling_start_button.configure(state=DISABLED)
    heating_running = True
    heating_thread = threading.Thread(target=heating)
    heating_thread.start()

def heating_stop(*args):
    global heating_running
    global heating_thread
    speach_message("Heating ended")
    heating_running_label.configure(text="")
    heating_stop_button.configure(state=DISABLED)
    heating_start_button.configure(state=NORMAL)
    brewing_start_button.configure(state=NORMAL)
    boiling_start_button.configure(state=NORMAL)
    cooling_start_button.configure(state=NORMAL)
    heating_running = False

def brewing():
    global brewing_running
    global brewing_thread
    global brewing_heating_level
    global pump1_speed
    global temp_q

    # Setup the PID regulator
    pid = PID.PID(settings["brewing_kp"], settings["brewing_ki"], settings["brewing_kd"])
    pid.setSampleTime(1)
    pid.SetPoint = settings["brewing_temp"][0]

    start_time = time.time()
    last_time = time.time()
    time_idx = 0
    time_extend = settings["brewing_time"][time_idx]*60
    temp_setpoint = settings["brewing_temp"][time_idx]
    next_change_of_temp = time_extend

    no_of_messages = len(settings["message_time"])
    print("Number of messages", no_of_messages)
    msg_idx = 0

    plot_interval = np.sum(settings["brewing_temp"])*60.0/1000.0
    last_plot = 0.0

    while brewing_running and time_idx < 4 and time_extend != 0 :
        # Update settings in case someting has changed
        set_settings()
        pump1_speed = float(brewing_pump_speed.get())/100.0
        elapsed_time = time.time() - start_time
        # Print elapsed time
        if time.time() - last_time > 1.:
            brewing_elapsed_time.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
            last_time = time.time()

        # Run temp regulator
        temp = float(brewing_temp.get())
        if settings["brewing_pid"]:
            pid.setKp(settings["brewing_kp"])
            pid.setKi(settings["brewing_ki"])
            pid.setKd(settings["brewing_kd"])

            temp = float(brewing_temp.get())
            pid.SetPoint = temp_setpoint
            pid.update(temp)
            brewing_heating_level = max(min( pid.output/100.0, 1.0 ),0.0)
        else:
            if temp - temp_setpoint > settings["brewing_decrease_lim"]:
                brewing_heating_level = 0.0
            if temp_setpoint - temp > settings["brewing_increase_lim"]:
                brewing_heating_level = 1.0

        # Check if change in temp
        if time.time() - start_time >= next_change_of_temp:
            time_idx += 1
            if time_idx < 4 :
                time_extend = settings["brewing_time"][time_idx] * 60
                next_change_of_temp += time_extend
                temp_setpoint = settings["brewing_temp"][time_idx]
                print("Temp setpoint: ", temp_setpoint)

        # Check for new voice message
        if msg_idx < no_of_messages:
            if time.time() - start_time > settings["message_time"][msg_idx]*60 :
                speach_message(settings["message_text"][msg_idx])
                msg_idx += 1

        # Check if plot data has to be updated
        while time.time() - last_plot > plot_interval:
            last_plot = time.time()
            plot = [elapsed_time, temp, temp_setpoint, brewing_heating_level]
            temp_q.put(plot)
        time.sleep(0.1)
    # Exit thread
    brewing_stop()


def brewing_start(*args):
    global brewing_running
    global brewing_thread
    speach_message("Brewing started")
    brewing_running_label.configure(text="Running", foreground="red")
    brewing_stop_button.configure(state=NORMAL)
    heating_start_button.configure(state=DISABLED)
    brewing_start_button.configure(state=DISABLED)
    boiling_start_button.configure(state=DISABLED)
    cooling_start_button.configure(state=DISABLED)
    brewing_running = True
    brewing_thread = threading.Thread(target=brewing)
    brewing_thread.start()

def brewing_stop(*args):
    global brewing_running
    global brewing_thread
    global brewing_heating_level
    global pump1_speed
    global clear_plot
    speach_message("Brewing ended")
    brewing_running_label.configure(text="")
    brewing_stop_button.configure(state=DISABLED)
    heating_start_button.configure(state=NORMAL)
    brewing_start_button.configure(state=NORMAL)
    boiling_start_button.configure(state=NORMAL)
    cooling_start_button.configure(state=NORMAL)
    brewing_running = False
    clear_plot = True
    brewing_heating_level = 0.0
    pump1_speed = 0.0


def boiling():
    global boiling_running
    global boiling_thread
    start_time = time.time()
    last_time = time.time()
    while boiling_running:
        # Print elapsed time
        if time.time() - last_time > 1.:
            elapsed_time = time.time()-start_time
            boiling_elapsed_time.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
            last_time = time.time()
        time.sleep(0.1)

def boiling_start(*args):
    global boiling_running
    global boiling_thread
    speach_message("Boiling started")
    boiling_running_label.configure(text="Running", foreground="red")
    boiling_stop_button.configure(state=NORMAL)
    heating_start_button.configure(state=DISABLED)
    brewing_start_button.configure(state=DISABLED)
    boiling_start_button.configure(state=DISABLED)
    cooling_start_button.configure(state=DISABLED)
    boiling_running = True
    boiling_thread = threading.Thread(target=boiling)
    boiling_thread.start()

def boiling_stop(*args):
    global boiling_running
    global boiling_thread
    global boiling_heating_level
    speach_message("Boiling ended")
    boiling_running_label.configure(text="")
    boiling_stop_button.configure(state=DISABLED)
    heating_start_button.configure(state=NORMAL)
    brewing_start_button.configure(state=NORMAL)
    boiling_start_button.configure(state=NORMAL)
    cooling_start_button.configure(state=NORMAL)
    boiling_running = False
    boiling_heating_power.set("0.0")
    boiling_heating_level = 0.0

def cooling():
    global cooling_running
    global cooling_thread
    start_time = time.time()
    last_time = time.time()
    while cooling_running:
        # Print elapsed time
        if time.time() - last_time > 1.:
            elapsed_time = time.time()-start_time
            cooling_elapsed_time.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))
            last_time = time.time()
        time.sleep(0.1)

def cooling_start(*args):
    global cooling_running
    global cooling_thread
    speach_message("Cooling started")
    cooling_running_label.configure(text="Running", foreground="red")
    cooling_stop_button.configure(state=NORMAL)
    heating_start_button.configure(state=DISABLED)
    brewing_start_button.configure(state=DISABLED)
    boiling_start_button.configure(state=DISABLED)
    cooling_start_button.configure(state=DISABLED)
    cooling_running = True
    cooling_thread = threading.Thread(target=cooling)
    cooling_thread.start()

def cooling_stop(*args):
    global cooling_running
    global cooling_thread
    speach_message("Cooling ended")
    cooling_running_label.configure(text="")
    cooling_stop_button.configure(state=DISABLED)
    heating_start_button.configure(state=NORMAL)
    brewing_start_button.configure(state=NORMAL)
    boiling_start_button.configure(state=NORMAL)
    cooling_start_button.configure(state=NORMAL)
    cooling_running = False

def start_pump(*args):
    i = 0


def stop_pump(*args):
    i = 0


def select_file(*args):
    global raw_sequence
    global annotation_tags
    global tag_lbox
    global xref
    filename = filedialog.askopenfilename(title="Select file to annotate",
                                          initialdir=base_directory+person.get()+"/raw",
                                          filetypes=[('Video files', '*.avi*')])
    if len(filename) > 1:
        reference = str.split(filename, ".")[0]
        reference = str.split(reference, "/")[-1]
        reference = str.split(reference, "X")[0]
        reference = reference[0:-1]

        print(reference)
        raw_sequence.set(reference)
        tag_lbox.configure(state=NORMAL)
        # Read the local annotation tags
        json_file = base_directory+person.get()+"/annotated/tags.json"
        with open(json_file) as jsonFile:
            annotation_tags = json.load(jsonFile)
            print("Annotation tags: ", annotation_tags)
            tags = StringVar(value=annotation_tags["tags"])
            tag_lbox.configure(listvariable=tags)
        # Read the cross reference file (connection between the saved sequence and the annotation tag)
        json_file = base_directory+person.get()+"/annotated/xref.json"
        with open(json_file, mode="r+") as jsonFile:
            xref = json.load(jsonFile)
            print("Xref: ", xref)

    print(filename)

def select_start_time(*args):
    print("Start time selected")

def select_tag(*args):
    selected_tag.set(tag_lbox.selection_get())
    save_button.configure(state=NORMAL)

def save_file(*args):
    global xref
    global raw_sequence
    print("Start time: ", start_time.get())
    print("End time : ", end_time.get())
    print("Sound significance: ", sound_scale.get())
    print("Face significance: ", face_scale.get())
    print("Gesture significance: ", gesture_scale.get())
    print("Annotation tag: ", selected_tag.get())
    filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    print(filename)
    # Update the cross reference file with the new file and tag
    x_reference = {filename: selected_tag.get()}
    xref.update(x_reference)
    json_file = base_directory + person.get() + "/annotated/xref.json"
    with open(json_file, mode="w") as jsonFile:
        json.dump(xref, jsonFile)
    # Save the sequence descriptor file
    json_file = base_directory + person.get() + "/annotated/" + filename + ".json"
    with open(json_file, mode="w") as jsonFile:
        descriptor = [{"raw_file": raw_sequence.get(), "tag": selected_tag.get()}]
        json.dump(descriptor, jsonFile)

# Read default settings
with open("default_settings.json", mode="r+") as jsonFile:
    settings = json.load(jsonFile)
    print("Default settings: ", settings)

root = Tk()
root.title("Garasjebryggeriet")

mainframe = ttk.Frame(root, padding="12 12 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Define all Widgets
read_settings_label = ttk.Label(mainframe, text="Read and save settings:")
read_settings_button = ttk.Button(mainframe, text="Read settings", command=read_settings)
selected_settings = StringVar()
selected_settings_label = ttk.Label(mainframe, text="No file selected")
selected_settings_label['textvariable'] = selected_settings
save_settings_button = ttk.Button(mainframe, text="Save settings", command=save_settings)

heating_label = ttk.Label(mainframe, text="Heating:")
heating_running_label = ttk.Label(mainframe, text="",foreground="red")
heating_setpoint_label = ttk.Label(mainframe, text="Temp setpoint")
heating_setpoint = StringVar()
heating_setpoint_entry = ttk.Entry(mainframe, textvariable=heating_setpoint)
heating_setpoint.set(str(settings["heating_setpoint"]))
heating_current_label = ttk.Label(mainframe, text="Current temp")
heating_current = ttk.Label(mainframe, text="20")
heating_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
heating_elapsed_time = ttk.Label(mainframe, text="00:00:00")
heating_start_button = ttk.Button(mainframe, text="Start", command=heating_start)
heating_stop_button = ttk.Button(mainframe, text="Stop", command=heating_stop, state=DISABLED)

brewing_label = ttk.Label(mainframe, text="Brewing:")
brewing_running_label = ttk.Label(mainframe, text="",foreground="red")
brewing_time_label = ttk.Label(mainframe, text="Number of minutes at each temperature")
brewing_time1 = StringVar()
brewing_time1_entry = ttk.Entry(mainframe, textvariable=brewing_time1)
brewing_time1.set(str(settings["brewing_time"][0]))
brewing_time2 = StringVar()
brewing_time2_entry = ttk.Entry(mainframe, textvariable=brewing_time2)
brewing_time2.set(str(settings["brewing_time"][1]))
brewing_time3 = StringVar()
brewing_time3_entry = ttk.Entry(mainframe, textvariable=brewing_time3)
brewing_time3.set(str(settings["brewing_time"][2]))
brewing_time4 = StringVar()
brewing_time4_entry = ttk.Entry(mainframe, textvariable=brewing_time4)
brewing_time4.set(str(settings["brewing_time"][3]))
brewing_temp_label = ttk.Label(mainframe, text="Temperature setpoints")
brewing_temp1 = StringVar()
brewing_temp1_entry = ttk.Entry(mainframe, textvariable=brewing_temp1)
brewing_temp1.set(str(settings["brewing_temp"][0]))
brewing_temp2 = StringVar()
brewing_temp2_entry = ttk.Entry(mainframe, textvariable=brewing_temp2)
brewing_temp2.set(str(settings["brewing_temp"][1]))
brewing_temp3 = StringVar()
brewing_temp3_entry = ttk.Entry(mainframe, textvariable=brewing_temp3)
brewing_temp3.set(str(settings["brewing_temp"][2]))
brewing_temp4 = StringVar()
brewing_temp4_entry = ttk.Entry(mainframe, textvariable=brewing_temp4)
brewing_temp4.set(str(settings["brewing_temp"][3]))
brewing_pid_label = ttk.Label(mainframe, text="Use PID")
brewing_kp_label = ttk.Label(mainframe, text="Kd")
brewing_ki_label = ttk.Label(mainframe, text="Ki")
brewing_kd_label = ttk.Label(mainframe, text="Kp")
brewing_use_pid = StringVar()
brewing_use_pid_button = ttk.Checkbutton(mainframe, text="Pid", variable=brewing_use_pid)
brewing_kp = StringVar()
brewing_kp_entry = ttk.Entry(mainframe, textvariable=brewing_kp)
brewing_ki = StringVar()
brewing_ki_entry = ttk.Entry(mainframe, textvariable=brewing_ki)
brewing_kd = StringVar()
brewing_kd_entry = ttk.Entry(mainframe, textvariable=brewing_kd)


brewing_increase_lim_label = ttk.Label(mainframe, text="Increase lim")
brewing_increase_lim = StringVar()
brewing_increase_lim_entry = ttk.Entry(mainframe, textvariable=brewing_increase_lim)
brewing_increase_lim.set(str(settings["brewing_increase_lim"]))
brewing_decrease_lim_label = ttk.Label(mainframe, text="Decrease lim")
brewing_decrease_lim = StringVar()
brewing_decrease_lim_entry = ttk.Entry(mainframe, textvariable=brewing_decrease_lim)
brewing_decrease_lim.set(str(settings["brewing_decrease_lim"]))
brewing_pump_speed_label = ttk.Label(mainframe, text="Pump speed [%]")
brewing_pump_speed = StringVar()
brewing_pump_speed_entry = ttk.Entry(mainframe, textvariable=brewing_pump_speed)
brewing_pump_speed.set(str(settings["brewing_pump_speed"]))
brewing_current_label = ttk.Label(mainframe, text="Current temp")
brewing_current = ttk.Label(mainframe, text="20")
brewing_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
brewing_elapsed_time = ttk.Label(mainframe, text="00:00:00")
brewing_stop_button = ttk.Button(mainframe, text="Stop", command=brewing_stop, state=DISABLED)
brewing_start_button = ttk.Button(mainframe, text="Start", command=brewing_start)

boiling_label = ttk.Label(mainframe, text="Boiling:")
boiling_running_label = ttk.Label(mainframe, text="",foreground="red")
boiling_start_pump_button = ttk.Button(mainframe, text="Start pump", command=start_pump)
boiling_stop_pump_button = ttk.Button(mainframe, text="Stop pump", command=stop_pump)
boiling_heating_power_label = ttk.Label(mainframe, text="Heating power [%]")
boiling_heating_power = StringVar()
boiling_heating_power_entry = ttk.Entry(mainframe, textvariable=boiling_heating_power)
boiling_heating_power.set(str(settings["boiling_heating_power"]))
boiling_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
boiling_elapsed_time = ttk.Label(mainframe, text="00:00:00")
boiling_start_button = ttk.Button(mainframe, text="Start", command=boiling_start)
boiling_stop_button = ttk.Button(mainframe, text="Stop", command=boiling_stop, state=DISABLED)

cooling_label = ttk.Label(mainframe, text="Cooling:")
cooling_running_label = ttk.Label(mainframe, text="",foreground="red")
cooling_setpoint_label = ttk.Label(mainframe, text="Temp setpoint")
cooling_setpoint = StringVar()
cooling_setpoint_entry = ttk.Entry(mainframe, textvariable=cooling_setpoint)
cooling_setpoint.set(str(settings["cooling_setpoint"]))
cooling_current_label = ttk.Label(mainframe, text="Current temp")
cooling_current = ttk.Label(mainframe, text="20")
cooling_kp_label = ttk.Label(mainframe, text="Kp")
cooling_kp = StringVar()
cooling_kp_entry = ttk.Entry(mainframe, textvariable=cooling_kp)
cooling_kp.set(str(settings["cooling_kp"]))
cooling_ki_label = ttk.Label(mainframe, text="Ki")
cooling_ki = StringVar()
cooling_ki_entry = ttk.Entry(mainframe, textvariable=cooling_ki)
cooling_ki.set(str(settings["cooling_ki"]))
cooling_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
cooling_elapsed_time = ttk.Label(mainframe, text="00:00:00")
cooling_start_button = ttk.Button(mainframe, text="Start", command=cooling_start)
cooling_stop_button = ttk.Button(mainframe, text="Stop", command=cooling_stop, state=DISABLED)

option_plot_curves_label = ttk.Label(mainframe, text="Plot curves")
option_temp1_label = ttk.Label(mainframe, text="Heating temp")
option_temp2_label = ttk.Label(mainframe, text="Brewing temp")
option_temp3_label = ttk.Label(mainframe, text="Cooling temp")

heating_temp = StringVar()
option_temp1 = ttk.Label(mainframe, text="0.0")
option_temp1['textvariable'] = heating_temp
brewing_temp = StringVar()
option_temp2 = ttk.Label(mainframe, text="0.0")
option_temp2['textvariable'] = brewing_temp
cooling_temp = StringVar()
option_temp3 = ttk.Label(mainframe, text="0.0")
option_temp3['textvariable'] = cooling_temp
plot_curves = StringVar()
option_plot_curves = ttk.Checkbutton(mainframe, text="Plot", variable=plot_curves)

info_pump1_label = ttk.Label(mainframe, text="Pump1 speed [%]")
info_pump2_label = ttk.Label(mainframe, text="Pump2 speed [%]")
info_brewing_heater_label = ttk.Label(mainframe, text="Brewing heater power [%]")
info_boiling_heater_label = ttk.Label(mainframe, text="Boiling heater power [%]")
info_pump1 = ttk.Label(mainframe, text="0.0")
info_pump2 = ttk.Label(mainframe, text="0.0")
info_brewing_heater = ttk.Label(mainframe, text="0.0")
info_boiling_heater = ttk.Label(mainframe, text="0.0")




# Position all Widgets
read_settings_label.grid(column=1, row=1, sticky=W, pady=5, padx=5)
read_settings_button.grid(column=1, row=2, sticky=W, pady=5, padx=5)
selected_settings_label.grid(column=2, row=2, columnspan=2, sticky=W, pady=5, padx=5)
save_settings_button.grid(column=4, row=2, sticky=E, pady=5, padx=5)


heating_label.grid(column=1, row=4, sticky=W, pady=5, padx=5)
heating_running_label.grid(column=2, row=4, sticky=W, pady=5, padx=5)
heating_setpoint_label.grid(column=1, row=5, sticky=W, pady=5, padx=5)
heating_setpoint_entry.grid(column=2, row=5, sticky=W, pady=5, padx=5)
heating_current_label.grid(column=3, row=5, sticky=W, pady=5, padx=5)
heating_current.grid(column=4, row=5, sticky=W, pady=5, padx=5)
heating_elapsed_time_label.grid(column=1, row=6, sticky=W, pady=5, padx=5)
heating_elapsed_time.grid(column=2, row=6, sticky=W, pady=5, padx=5)
heating_start_button.grid(column=3, row=7, sticky=E, pady=5, padx=5)
heating_stop_button.grid(column=4, row=7, sticky=E, pady=5, padx=5)

brewing_label.grid(column=1, row=9, sticky=W, pady=5, padx=5)
brewing_running_label.grid(column=2, row=9, sticky=W, pady=5, padx=5)
brewing_time_label.grid(column=1, row=10, columnspan=2, sticky=W, pady=5, padx=5)
brewing_time1_entry.grid(column=1, row=11, sticky=W, pady=5, padx=5)
brewing_time2_entry.grid(column=2, row=11, sticky=W, pady=5, padx=5)
brewing_time3_entry.grid(column=3, row=11, sticky=W, pady=5, padx=5)
brewing_time4_entry.grid(column=4, row=11, sticky=W, pady=5, padx=5)
brewing_temp_label.grid(column=1, row=12, columnspan=2, sticky=W, pady=5, padx=5)
brewing_temp1_entry.grid(column=1, row=13, sticky=W, pady=5, padx=5)
brewing_temp2_entry.grid(column=2, row=13, sticky=W, pady=5, padx=5)
brewing_temp3_entry.grid(column=3, row=13, sticky=W, pady=5, padx=5)
brewing_temp4_entry.grid(column=4, row=13, sticky=W, pady=5, padx=5)
brewing_increase_lim_label.grid(column=1, row=14, sticky=W, pady=5, padx=5)
brewing_increase_lim_entry.grid(column=2, row=14, sticky=W, pady=5, padx=5)
brewing_decrease_lim_label.grid(column=3, row=14, sticky=W, pady=5, padx=5)
brewing_decrease_lim_entry.grid(column=4, row=14, sticky=W, pady=5, padx=5)
brewing_pump_speed_label.grid(column=1, row=15, sticky=W, pady=5, padx=5)
brewing_pump_speed_entry.grid(column=2, row=15, sticky=W, pady=5, padx=5)
brewing_current_label.grid(column=3, row=15, sticky=W, pady=5, padx=5)
brewing_current.grid(column=4, row=15, sticky=W, pady=5, padx=5)
brewing_elapsed_time_label.grid(column=1, row=16, sticky=W, pady=5, padx=5)
brewing_elapsed_time.grid(column=2, row=16, sticky=W, pady=5, padx=5)
brewing_start_button.grid(column=3, row=17, sticky=E, pady=5, padx=5)
brewing_stop_button.grid(column=4, row=17, sticky=E, pady=5, padx=5)

boiling_label.grid(column=1, row=19, sticky=W, pady=5, padx=5)
boiling_running_label.grid(column=2, row=19, sticky=W, pady=5, padx=5)
boiling_start_pump_button.grid(column=1, row=20, sticky=W, pady=5, padx=5)
boiling_stop_pump_button.grid(column=2, row=20, sticky=W, pady=5, padx=5)
boiling_heating_power_label.grid(column=3, row=20, sticky=W, pady=5, padx=5)
boiling_heating_power_entry.grid(column=4, row=20, sticky=W, pady=5, padx=5)
boiling_elapsed_time_label.grid(column=1, row=21, sticky=W, pady=5, padx=5)
boiling_elapsed_time.grid(column=2, row=21, sticky=W, pady=5, padx=5)
boiling_start_button.grid(column=3, row=22, sticky=E, pady=5, padx=5)
boiling_stop_button.grid(column=4, row=22, sticky=E, pady=5, padx=5)

cooling_label.grid(column=1, row=24, sticky=W, pady=5, padx=5)
cooling_running_label.grid(column=2, row=24, sticky=W, pady=5, padx=5)
cooling_setpoint_label.grid(column=1, row=25, sticky=W, pady=5, padx=5)
cooling_setpoint_entry.grid(column=2, row=25, sticky=W, pady=5, padx=5)
cooling_current_label.grid(column=3, row=25, sticky=W, pady=5, padx=5)
cooling_current.grid(column=4, row=25, sticky=W, pady=5, padx=5)

cooling_kp_label.grid(column=1, row=26, sticky=W, pady=5, padx=5)
cooling_kp_entry.grid(column=2, row=26, sticky=W, pady=5, padx=5)
cooling_ki_label.grid(column=3, row=26, sticky=W, pady=5, padx=5)
cooling_ki_entry.grid(column=4, row=26, sticky=W, pady=5, padx=5)
cooling_elapsed_time_label.grid(column=1, row=27, sticky=W, pady=5, padx=5)
cooling_elapsed_time.grid(column=2, row=27, sticky=W, pady=5, padx=5)
cooling_start_button.grid(column=3, row=28, sticky=E, pady=5, padx=5)
cooling_stop_button.grid(column=4, row=28, sticky=E, pady=5, padx=5)

option_plot_curves_label.grid(column=1, row=30, sticky=W, pady=5, padx=5)
option_temp1_label.grid(column=2, row=30, sticky=W, pady=5, padx=5)
option_temp2_label.grid(column=3, row=30, sticky=W, pady=5, padx=5)
option_temp3_label.grid(column=4, row=30, sticky=W, pady=5, padx=5)
option_plot_curves.grid(column=1, row=31, sticky=W, pady=5, padx=5)
option_temp1.grid(column=2, row=31, sticky=W, pady=5, padx=5)
option_temp2.grid(column=3, row=31, sticky=W, pady=5, padx=5)
option_temp3.grid(column=4, row=31, sticky=W, pady=5, padx=5)

info_pump1_label.grid(column=1, row=32, sticky=W, pady=5, padx=5)
info_pump2_label.grid(column=2, row=32, sticky=W, pady=5, padx=5)
info_brewing_heater_label.grid(column=3, row=32, sticky=W, pady=5, padx=5)
info_boiling_heater_label.grid(column=4, row=32, sticky=W, pady=5, padx=5)
info_pump1.grid(column=1, row=33, sticky=W, pady=5, padx=5)
info_pump2.grid(column=2, row=33, sticky=W, pady=5, padx=5)
info_brewing_heater.grid(column=3, row=33, sticky=W, pady=5, padx=5)
info_boiling_heater.grid(column=4, row=33, sticky=W, pady=5, padx=5)

brewing_pid_label.grid(column=1, row=34, sticky=W, pady=5, padx=5)
brewing_kp_label.grid(column=2, row=34, sticky=W, pady=5, padx=5)
brewing_ki_label.grid(column=3, row=34, sticky=W, pady=5, padx=5)
brewing_kd_label.grid(column=4, row=34, sticky=W, pady=5, padx=5)
brewing_use_pid_button.grid(column=1, row=35, sticky=W, pady=5, padx=5)
brewing_kp_entry.grid(column=2, row=35, sticky=W, pady=5, padx=5)
brewing_ki_entry.grid(column=3, row=35, sticky=W, pady=5, padx=5)
brewing_kd_entry.grid(column=4, row=35, sticky=W, pady=5, padx=5)



speach_message("Welcome to garasjebryggeriet, the best brewery in Kongsberg")

# print sensor ID's
sensors = W1ThermSensor.get_available_sensors()
print("The following temperature sensors are connected:")
print(sensors[0].id)
print(sensors[1].id)
print(sensors[2].id)
print("Heating sensor id: ", settings["heating_sensor"])
print("Brewing sensor id: ", settings["brewing_sensor"])
print("Cooling sensor id: ", settings["cooling_sensor"])

heating_sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, settings["heating_sensor"])
brewing_sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, settings["brewing_sensor"])
cooling_sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, settings["cooling_sensor"])
heating_temp.set(heating_sensor.get_temperature())
brewing_temp.set(brewing_sensor.get_temperature())
cooling_temp.set(cooling_sensor.get_temperature())

threading.Thread(target=temperature_thread, args=(0,)).start()

# Setup GPIO bits
gpio.setmode(gpio.BCM)
gpio.setup(BREWING_HEATER_BIT, gpio.OUT)
gpio.output(BREWING_HEATER_BIT, gpio.HIGH)
gpio.setup(BOILING_HEATER_BIT, gpio.OUT)
gpio.output(BOILING_HEATER_BIT, gpio.HIGH)
gpio.setup(PUMP1_BIT, gpio.OUT)
gpio.output(PUMP1_BIT, gpio.HIGH)
gpio.setup(PUMP2_BIT, gpio.OUT)
gpio.output(PUMP2_BIT, gpio.HIGH)

threading.Thread(target=brewing_heater_thread, args=(BREWING_HEATER_BIT,)).start()
threading.Thread(target=boiling_heater_thread, args=(BOILING_HEATER_BIT,)).start()
threading.Thread(target=pump1_thread, args=(PUMP1_BIT,)).start()
threading.Thread(target=pump2_thread, args=(PUMP2_BIT,)).start()
threading.Thread(target=plotting, args=(0,)).start()

# get the path to the base directory
base_directory = "/home/vidar/projects/knowme/data/"
try:
    myOpts, args = getopt.getopt(sys.argv[1:], "i:")
except getopt.GetoptError as e:
    print(str(e))
    print("Usage: %s -i <path to base directory>" % sys.argv[0])
    sys.exit(2)

for o, a in myOpts:
    if o == '-d':
        base_directory = a

print("Base directory selected: ", base_directory)


root.mainloop()