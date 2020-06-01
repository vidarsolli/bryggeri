import matplotlib.pyplot as plt
import threading
import time
import numpy as np
from matplotlib import animation


data1 = np.random.randn(4, 100)
data2 = np.random.randn(4, 100)

def plt_thread():
    while True:
        fig.draw()
        print("drawin")
        time.sleep(0.1)

def data_thread1(a):
    global data1, data2
    while True:
        data1= np.random.randn(4, 100)
        data2= np.random.randn(4, 100)
        time.sleep(0.5)

def data_thread2():
    while True:
        data1= np.random.randn(4, 100)
        data2= np.random.randn(4, 100)
        axs[1].plot(data1, data2)
        time.sleep(0.3)




#fig, axs = plt.subplots(1,2)
#threading.Thread(target=plt_thread, args=(1,))
threading.Thread(target=data_thread1, args=(1,)).start()
#threading.Thread(target=data_thread2, args=(1,))

fig, axs = plt.subplots(1,2)
fig.set_size_inches(12,4)
line_label = ["Temp","Setpoint", "Power","Temp","Setpoint", "Power" ]
N = 6
lines = [axs[int(i/3)].plot([], [], label=line_label[i])[0] for i in range(N)] #lines to animate
patches = lines

axs[0].set_xlim(0,4)
axs[0].set_ylim(-1, 2)
axs[0].set_title("Brewing temperature")
axs[0].legend()
axs[0].grid()
axs[0].set_position([0.05, 0.1, 0.42, 0.8])
axs[1].set_xlim(-2,2)
axs[1].set_ylim(0, 2)
axs[1].set_title("Cooling temperature")
axs[1].legend()
axs[1].grid()
axs[1].set_position([0.55, 0.1, 0.42, 0.8])

# initialization function: plot the background of each frame
def init():
    for line in lines:
        line.set_data([], [])
    return lines

# animation function.  This is called sequentially
def animate(i):
    x = np.linspace(0, 2, 1000)
    y1 = np.sin(2 * np.pi * (x - 0.01 * i))
    y2 = np.sin(2 * np.pi * (x - 0.03 * i))
    y3 = np.sin(2 * np.pi * (x - 0.05 * i))
    lines[0].set_data(data1, data2)
    lines[3].set_data(y1, x)
    lines[4].set_data(y2, x)
    lines[5].set_data(y3, x)
    #lines[0].set_data(x, y)
    #lines[1].set.data(x, y)
    return lines

# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=200, interval=20, blit=True)

plt.show()