import getopt
from datetime import datetime
import json
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox


annotation_tags = ([])
xref = ([])

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
    settings["brewing_increase_lim"] = float(brewing_increase_lim.get())
    settings["brewing_decrease_lim"] = float(brewing_decrease_lim.get())
    settings["brewing_pump_speed"] = int(brewing_pump_speed.get())
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

def heating_start(*args):
    i = 0

def heating_stop(*args):
    i = 0

def brewing_start(*args):
    i = 0

def brewing_stop(*args):
    i = 0

def boiling_start(*args):
    i = 0

def boiling_stop(*args):
    i = 0

def cooling_start(*args):
    i = 0

def cooling_stop(*args):
    i = 0

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
    print("Default settings: ", xref)


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
heating_running_label = ttk.Label(mainframe, text="Running")
heating_setpoint_label = ttk.Label(mainframe, text="Temp setpoint")
heating_setpoint = StringVar()
heating_setpoint_entry = ttk.Entry(mainframe, textvariable=heating_setpoint)
heating_setpoint.set(str(settings["heating_setpoint"]))
heating_current_label = ttk.Label(mainframe, text="Current temp")
heating_current = ttk.Label(mainframe, text="20")
heating_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
heating_elapsed_time = ttk.Label(mainframe, text="00:00:00")
heating_start_button = ttk.Button(mainframe, text="Start", command=heating_start)
heating_stop_button = ttk.Button(mainframe, text="Stop", command=heating_stop)

brewing_label = ttk.Label(mainframe, text="Brewing:")
brewing_running_label = ttk.Label(mainframe, text="Running")
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
brewing_stop_button = ttk.Button(mainframe, text="Start", command=brewing_stop)
brewing_start_button = ttk.Button(mainframe, text="Stop", command=brewing_start)

boiling_label = ttk.Label(mainframe, text="Boiling:")
boiling_running_label = ttk.Label(mainframe, text="Running", background="yellow", foreground="red")
boiling_start_pump_button = ttk.Button(mainframe, text="Start pump", command=start_pump)
boiling_stop_pump_button = ttk.Button(mainframe, text="Stop pump", command=stop_pump)
boiling_heating_power_label = ttk.Label(mainframe, text="Heating power [%]")
boiling_heating_power = StringVar()
boiling_heating_power_entry = ttk.Entry(mainframe, textvariable=boiling_heating_power)
boiling_heating_power.set(str(settings["boiling_heating_power"]))
boiling_elapsed_time_label = ttk.Label(mainframe, text="Elapsed time")
boiling_elapsed_time = ttk.Label(mainframe, text="00:00:00")
boiling_start_button = ttk.Button(mainframe, text="Start", command=boiling_start)
boiling_stop_button = ttk.Button(mainframe, text="Stop", command=boiling_stop)

cooling_label = ttk.Label(mainframe, text="Cooling:")
cooling_running_label = ttk.Label(mainframe, text="Running")
cooling_setpoint_label = ttk.Label(mainframe, text="Temp setpoint")
cooling_setpoint = StringVar()
cooling_setpoint_entry = ttk.Entry(mainframe, textvariable=cooling_setpoint)
cooling_setpoint.set(str(settings["cooling_setpoint"]))
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
cooling_stop_button = ttk.Button(mainframe, text="Stop", command=cooling_stop)

option_plot_curves_label = ttk.Label(mainframe, text="Plot curves")
option_temp1_label = ttk.Label(mainframe, text="Temp 1")
option_temp2_label = ttk.Label(mainframe, text="Temp 2")
option_temp3_label = ttk.Label(mainframe, text="Temp 3")
option_temp1 = ttk.Label(mainframe, text="0.0")
option_temp2 = ttk.Label(mainframe, text="0.0")
option_temp3 = ttk.Label(mainframe, text="0.0")
plot_curves = StringVar()
option_plot_curves = ttk.Checkbutton(mainframe, text="Plot", variable=plot_curves)



file_label = ttk.Label(mainframe, text="File reference:")
select_button = ttk.Button(mainframe, text="Select", command=select_file)
selected_file_label = ttk.Label(mainframe, text="-")
start_time_label = ttk.Label(mainframe, text="Start time")
end_time_label = ttk.Label(mainframe, text="End time")
start_time = StringVar()
start_time_entry = ttk.Entry(mainframe, textvariable=start_time)
start_time.set("00:00:00:00")
end_time = StringVar()
end_time_entry = ttk.Entry(mainframe, textvariable=end_time)
end_time.set("00:00:00:00")
save_button = ttk.Button(mainframe, text="Save", command=save_file)
significance_label = ttk.Label(mainframe, text="Significance:")
sound_label = ttk.Label(mainframe, text="Sound")
sound_scale = ttk.Scale(mainframe, orient=HORIZONTAL, length=200, from_=0.0, to=1.0)
sound_scale.set(1.0)
face_label = ttk.Label(mainframe, text="Face")
face_scale = ttk.Scale(mainframe, orient=HORIZONTAL, length=200, from_=0.0, to=1.0)
face_scale.set(1.0)
gesture_label = ttk.Label(mainframe, text="Gesture")
gesture_scale = ttk.Scale(mainframe, orient=HORIZONTAL, length=200, from_=0.0, to=1.0)
gesture_scale.set(1.0)
annotation_tag_label = ttk.Label(mainframe, text="Select annotation tag:")
selected_tag_label = ttk.Label(mainframe, text="No annotation tag selected")
tags = StringVar(value=annotation_tags)
tag_lbox = Listbox(mainframe, listvariable=tags, height=5)
tag_lbox.selection_set(0)



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

"""
file_label.grid(column=1, row=3, sticky=W, pady=5, padx=5)
select_button.grid(column=1, row=4, sticky=W, pady=5, padx=5)
selected_file_label.grid(column=2, row=4, columnspan=2, sticky=W, pady=5, padx=5)
start_time_label.grid(column=1, row=5, sticky=W, pady=5, padx=5)
end_time_label.grid(column=2, row=5, sticky=W, pady=5, padx=5)
start_time_entry.grid(column=1, row=6, sticky=W, pady=5, padx=5)
end_time_entry.grid(column=2, row=6, sticky=W, pady=5, padx=5)
significance_label.grid(column=1, row=7, sticky=W, pady=5, padx=5)
sound_label.grid(column=1, row=8, sticky=W, pady=5, padx=5)
sound_scale.grid(column=2, row=8, sticky=W, pady=5, padx=5)

face_label.grid(column=1, row=9, sticky=W, pady=5, padx=5)
face_scale.grid(column=2, row=9, sticky=W, pady=5, padx=5)
gesture_label.grid(column=1, row=10, sticky=W, pady=5, padx=5)
gesture_scale.grid(column=2, row=10, sticky=W, pady=5, padx=5)
annotation_tag_label.grid(column=1, row=11, columnspan=2, sticky=W, pady=5, padx=5)
selected_tag_label.grid(column=2, row=12, sticky=W, pady=5, padx=5)
tag_lbox.grid(column=1, row=12, columnspan=2, sticky=W, pady=5, padx=5)

save_button.grid(column=2, row=13, sticky=E, pady=5, padx=5)
"""

# Disable the file button, a person must have been selected before it can turn active
select_button.configure(state=DISABLED)
# Disable the save button, a tag must have been selected before it can turn active
save_button.configure(state=DISABLED)
tag_lbox.configure(state=DISABLED)

selected_tag = StringVar()
selected_tag_label['textvariable'] = selected_tag
selected_tag.set("No tag selected")

raw_sequence = StringVar()
selected_file_label['textvariable'] = raw_sequence
raw_sequence.set('No file selected')

tag_lbox.bind('<Double-1>', select_tag)

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