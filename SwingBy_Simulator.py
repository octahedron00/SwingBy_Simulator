import math
from tkinter import *
import tkinter.messagebox as alert
import tkinter.ttk as ttk
import sys

w = 640
h = 320
one_pixel = 10000000
time_tick = 10000
go = True


root = Tk()
root.title("SwingBy Simulator")

#################################################

class Planet:

    def __init__(self, mass, radius, my_canvas, pos_x, pos_y, dt_dx, dt_dy):
        self.mass = mass
        self.radius = radius
        self.canvas = my_canvas
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dt_dx = dt_dx
        self.dt_dy = dt_dy
        self.oval_id = self.draw_initial_planet()

    def draw_initial_planet(self):
        oval_id = self.canvas.create_oval(
            self.pos_x / one_pixel - self.radius, self.pos_y / one_pixel - self.radius,
            self.pos_x / one_pixel + self.radius, self.pos_y / one_pixel + self.radius,
            fill="grey")
        return oval_id

    def pos(self):
        return self.pos_x, self.pos_y

    def update_location(self):
        self.pos_x += self.dt_dx * time_tick
        self.pos_y += self.dt_dy * time_tick
        self.canvas.coords(self.oval_id,
                           self.pos_x / one_pixel - self.radius, self.pos_y / one_pixel - self.radius,
                           self.pos_x / one_pixel + self.radius, self.pos_y / one_pixel + self.radius)


class Spacecraft(Planet):
    G = 6.67e-11

    def __init__(self, mass, radius, my_canvas, pos_x, pos_y, dt_dx, dt_dy, planet):
        super(Spacecraft, self).__init__(mass, radius, my_canvas, pos_x, pos_y, dt_dx, dt_dy)
        self.planet = planet

    def dist(self):
        dist_x = (self.planet.pos_x - self.pos_x)
        dist_y = (self.planet.pos_y - self.pos_y)
        d = math.sqrt((dist_x * dist_x) + (dist_y * dist_y))
        return d

    def accelerate(self):
        dist_x = (self.planet.pos_x - self.pos_x)
        dist_y = (self.planet.pos_y - self.pos_y)
        dist = self.dist()
        f = self.G * self.planet.mass / (dist * dist)
        acc_x = f * dist_x / dist
        acc_y = f * dist_y / dist
        self.dt_dx += acc_x * time_tick
        self.dt_dy += acc_y * time_tick

    def speed(self):
        return math.sqrt(self.dt_dx * self.dt_dx + self.dt_dy * self.dt_dy)


class Dot:
    def __init__(self, canvas, pos_x, pos_y, i, col):
        self.canvas = canvas
        self.x = pos_x
        self.y = pos_y
        self.i = i
        self.dot_id = self.canvas.create_oval(self.x + 1, self.y + 1, self.x - 1, self.y - 1, fill=col)

    def move(self, pos_y):
        self.y = pos_y
        self.canvas.coords(self.dot_id, self.x + 1, self.y + 1, self.x - 1, self.y - 1)


#################################################

def proj(x, y, deg):
    rad = deg*math.pi/180

    x_proj = x*math.sin(rad) - y*math.cos(rad)
    return x_proj


def start():
    global time_tick
    global go

    go = True
    time = 0

    planet_name = cmb_weight.get()
    time_tick = eval(cmb_tick.get()[0:-1])
    speed = eval(ent_speed.get())
    deg = eval(ent_deg.get())
    vec = eval(ent_vec.get())

    print(planet_name)
    print(time_tick)
    print(speed)
    print(deg)

    btn_start.pack_forget()
    btn_stop.pack(side="right", padx=5, pady=5)
    canvas_space.delete("all")
    canvas_plot.delete("all")

    lines()

    if speed < 0.1:
        alert.showerror("Speed error", "Speed too small")
        btn_stop.pack_forget()
        btn_start.pack(side="right", padx=5, pady=5)
        return
    if speed > 100:
        alert.showerror("Speed error", "Speed too big")
        btn_stop.pack_forget()
        btn_start.pack(side="right", padx=5, pady=5)
        return
    if deg < -80 or deg > 80:
        alert.showerror("Degree error", "Degree too large")
        btn_stop.pack_forget()
        btn_start.pack(side="right", padx=5, pady=5)
        return

    planet = None
    if planet_name == "Earth":
        planet = Planet(5.974e24, 5, canvas_space, (w - 100) * one_pixel, h * one_pixel / 2, -29783, 0)
    if planet_name == "Mars":
        planet = Planet(6.417e23, 5, canvas_space, (w - 100) * one_pixel, h * one_pixel / 2, -24077, 0)
    if planet_name == "Jupiter":
        planet = Planet(1.898e27, 10, canvas_space, (w - 100) * one_pixel, h * one_pixel / 2, -13056, 0)
    if planet_name == "10x Jupiter":
        planet = Planet(1.898e28, 10, canvas_space, (w - 100) * one_pixel, h * one_pixel / 2, -13056, 0)
    if planet_name == "HOLD":
        planet = Planet(1.900e26, 5, canvas_space, w * one_pixel / 2, h * one_pixel / 2, 0, 0)

    speed_x = speed * 1000 * math.sin(deg * math.pi / 180)
    speed_y = speed * 1000 * math.cos(deg * math.pi / 180)
    spacecraft = []
    for i in range(320):
        spacecraft.append(
            (
                Spacecraft(1, 2, canvas_space, i * 2 * one_pixel, (h - 100) * one_pixel, speed_x, -speed_y, planet),
                Dot(canvas_plot, i * 2, 120, i, "black"),
                Dot(canvas_plot, i * 2, 360, i, "brown")
            )
        )

    while (spacecraft[0][0].pos_y > 0 or planet.pos_x > 0) and go:
        planet.update_location()
        for craft in spacecraft:
            craft[0].accelerate()
            craft[0].update_location()
            craft[1].move(120 - (craft[0].speed() - (speed * 1000)) / (speed * 10))
            craft[2].move(360 -
                          (proj(craft[0].dt_dx, craft[0].dt_dy, vec) - (proj(speed_x, -speed_y, vec)))
                          * 100 / (proj(speed_x, -speed_y, vec))
                          )

            time += time_tick
            time_string = str(time)+"s("+str(round(time/24/60/60, 3))+"d)"
            lbl_time.config(text=time_string)

        i = 0
        while i < len(spacecraft):
            if spacecraft[i][0].dist() / one_pixel < planet.radius*planet.radius/25:
                canvas_space.delete(spacecraft[i][0].oval_id)
                canvas_plot.delete(spacecraft[i][1].dot_id)
                canvas_plot.delete(spacecraft[i][2].dot_id)
                spacecraft.remove(spacecraft[i])
                i -= 1
            i += 1

        root.update()

    btn_stop.pack_forget()
    btn_start.pack(side="right", padx=5, pady=5)


def stop():
    global go
    go = False


#################################################

left_frame = Frame(root)
left_frame.grid(row=0, column=0)

# 1st Layer
frame_option = LabelFrame(left_frame, text="Settings")
frame_option.pack(padx=5, pady=5, ipady=5)

# Weight Label
lbl_weight = Label(frame_option, text="Planet", width=12)
lbl_weight.pack(side="left", padx=5, pady=5)

# Weight Combobox
opt_weight = ["Earth", "Mars", "Jupiter", "10x Jupiter", "HOLD"]
cmb_weight = ttk.Combobox(frame_option, state="readonly", values=opt_weight, width=10)
cmb_weight.current(0)
cmb_weight.pack(side="left", padx=5, pady=5)

# Speed Label
lbl_speed = Label(frame_option, text="Speed(km/s)", width=12)
lbl_speed.pack(side="left", padx=5, pady=5)

# Speed Entry
ent_speed = Entry(frame_option, width=10)
ent_speed.pack(side="left", padx=5, pady=5)

# Degree Label
lbl_deg = Label(frame_option, text="Degree", width=12)
lbl_deg.pack(side="left", padx=5, pady=5)

# Degree Entry
ent_deg = Entry(frame_option, width=10)
ent_deg.pack(side="left", padx=5, pady=5)

# 2nd Layer
frame_option2 = LabelFrame(left_frame, text="Settings")
frame_option2.pack(padx=5, pady=5, ipady=5)

# Vector degree Label
lbl_vec = Label(frame_option2, text="Degree", width=12)
lbl_vec.pack(side="left", padx=5, pady=5)

# Vector degree Entry
ent_vec = Entry(frame_option2, width=10)
ent_vec.pack(side="left", padx=5, pady=5)

# Tick Label
lbl_tick = Label(frame_option2, text="Time Tick", width=12)
lbl_tick.pack(side="left", padx=5, pady=5)

# Tick Combobox
opt_tick = ["10s", "50s", "100s", "200s", "500s", "1000s", "5000s", "10000s"]
cmb_tick = ttk.Combobox(frame_option2, state="readonly", values=opt_tick, width=10)
cmb_tick.current(2)
cmb_tick.pack(side="left", padx=5, pady=5)

# Time Label
lbl_time = Label(frame_option2, text="0s(0d)", width=16)
lbl_time.pack(side="left", padx=5, pady=5)

# Start Button
btn_start = Button(frame_option2, padx=5, pady=5, text="Start", width=8, command=start)
btn_start.pack(side="right", padx=5, pady=5)

# Stop Button
btn_stop = Button(frame_option2, padx=5, pady=5, text="Stop", width=8, command=stop)
btn_stop.pack(side="right", padx=5, pady=5)
btn_stop.pack_forget()

# Space Canvas
canvas_space = Canvas(left_frame, height=h, width=w, bg='black')
canvas_space.pack()

# Plot Canvas, Right side
canvas_plot = Canvas(root, height=480, width=640, bg='white')
canvas_plot.grid(row=0, column=1)
root.update_idletasks()


def lines():
    # One line = 10%
    canvas_plot.create_line(0, 170, 640, 170, fill='blue')
    canvas_plot.create_line(0, 160, 640, 160, fill='blue')
    canvas_plot.create_line(0, 150, 640, 150, fill='blue')
    canvas_plot.create_line(0, 140, 640, 140, fill='blue')
    canvas_plot.create_line(0, 130, 640, 130, fill='blue')
    canvas_plot.create_line(0, 120, 640, 120, fill='black')
    canvas_plot.create_line(0, 110, 640, 110, fill='red')
    canvas_plot.create_line(0, 100, 640, 100, fill='red')
    canvas_plot.create_line(0, 90, 640, 90, fill='red')
    canvas_plot.create_line(0, 80, 640, 80, fill='red')
    canvas_plot.create_line(0, 70, 640, 70, fill='red')

    canvas_plot.create_line(0, 170+240, 640, 170+240, fill='blue')
    canvas_plot.create_line(0, 160+240, 640, 160+240, fill='blue')
    canvas_plot.create_line(0, 150+240, 640, 150+240, fill='blue')
    canvas_plot.create_line(0, 140+240, 640, 140+240, fill='blue')
    canvas_plot.create_line(0, 130+240, 640, 130+240, fill='blue')
    canvas_plot.create_line(0, 120+240, 640, 120+240, fill='black')
    canvas_plot.create_line(0, 110+240, 640, 110+240, fill='red')
    canvas_plot.create_line(0, 100+240, 640, 100+240, fill='red')
    canvas_plot.create_line(0, 90+240, 640, 90+240, fill='red')
    canvas_plot.create_line(0, 80+240, 640, 80+240, fill='red')
    canvas_plot.create_line(0, 70+240, 640, 70+240, fill='red')


lines()

#################################################


root.mainloop()
sys.exit()
