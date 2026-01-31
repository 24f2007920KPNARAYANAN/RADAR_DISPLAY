import serial
import tkinter as tk
import math
import time
import random

# --- CONFIGURATION ---
PORT = 'COM3'  
BAUD = 115200
MAX_DISTANCE = 300 
MAX_TARGETS = 5    

class FinalProjectHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED_NAV_SYSTEM_v6.6")
        self.canvas = tk.Canvas(root, width=900, height=600, bg="#0a141a", highlightthickness=0)
        self.canvas.pack()
        
        self.center_x, self.center_y = 450, 310
        self.radius = 230 
        self.angle = 0
        self.targets = [] 
        self.current_dist = 0

        try:
            self.ser = serial.Serial(PORT, BAUD, timeout=0.01)
        except:
            print("Check COM Port Connection!")
            root.destroy()

        self.render()

    def draw_hud_elements(self):
        # 1. Background Decorative Rings
        for i in range(5):
            r = 50 + (i * 45)
            self.canvas.create_oval(self.center_x-r, self.center_y-r, 
                                    self.center_x+r, self.center_y+r, outline="#0b242b", width=1)

        # 2. Main Azimuth Ring
        self.canvas.create_oval(self.center_x-self.radius, self.center_y-self.radius, 
                                self.center_x+self.radius, self.center_y+self.radius, outline="#00ffff", width=2)
        
        for a in range(0, 360, 10):
            rad = math.radians(a)
            inner_r = self.radius - (10 if a % 30 == 0 else 5)
            x1, y1 = self.center_x + inner_r * math.cos(rad), self.center_y + inner_r * math.sin(rad)
            x2, y2 = self.center_x + self.radius * math.cos(rad), self.center_y + self.radius * math.sin(rad)
            self.canvas.create_line(x1, y1, x2, y2, fill="#00ffff")

        # 3. LEFT SIDEBAR: TECHNICAL SPECS
        self.canvas.create_text(20, 40, text="MICRO PROJECT", fill="#00ffff", font=("Courier", 14, "bold"), anchor="w")
        self.canvas.create_text(20, 65, text="LD1020 - STATUS ACTIVE", fill="#008080", font=("Courier", 9), anchor="w")
        self.canvas.create_text(20, 85, text="ESP32 WROOM MODULE:", fill="#00ffff", font=("Courier", 9, "bold"), anchor="w")
        self.canvas.create_text(20, 100, text="RX/TX SIGNAL LINK ACTIVE", fill="#008080", font=("Courier", 8), anchor="w")

        # 4. CREATOR TAG (Added here)
        self.canvas.create_text(20, 570, text="CREATED BY - YASH_NARAYANAN_ATHUL", fill="#004444", font=("Courier", 8, "italic"), anchor="w")

        # 5. RIGHT SIDEBAR: DETECTION LOG
        self.canvas.create_text(730, 40, text="[ DETECTION_LOG ]", fill="#00ffff", font=("Courier", 10, "bold"), anchor="w")
        self.canvas.create_text(730, 60, text="ID   RANGE   ANG", fill="#008080", font=("Courier", 9), anchor="w")
        self.canvas.create_line(730, 70, 880, 70, fill="#008080")

        for i, target in enumerate(reversed(self.targets)):
            dist, ang, ts = target
            deg = int(math.degrees(ang) % 360)
            y_pos = 85 + (i * 20)
            self.canvas.create_text(730, y_pos, text=f"0{5-i}  {dist:3}cm  {deg:3}°", fill="#ffff00", font=("Courier", 9), anchor="w")

    def render(self):
        if self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line.isdigit():
                    self.current_dist = int(line)
                    if self.current_dist > 0:
                        self.targets.append([self.current_dist, self.angle, time.time()])
                        if len(self.targets) > MAX_TARGETS: self.targets.pop(0)
            except: pass

        self.canvas.delete("all")
        self.draw_hud_elements()
        self.angle += 0.04 

        # 6. GRADIENT SWEEP
        steps = 50 
        for i in range(steps):
            alpha = int((1 - i/steps) * 100)
            glow_color = f'#00{alpha:02x}{alpha:02x}' 
            start_ang = math.degrees(-(self.angle - i*0.02))
            self.canvas.create_arc(self.center_x-self.radius, self.center_y-self.radius, 
                                   self.center_x+self.radius, self.center_y+self.radius, 
                                   start=start_ang, extent=3, outline="", fill=glow_color, style="pieslice")

        # 7. SCANNER LINE & TARGET BLIPS
        sx = self.center_x + self.radius * math.cos(self.angle)
        sy = self.center_y + self.radius * math.sin(self.angle)
        self.canvas.create_line(self.center_x, self.center_y, sx, sy, fill="#00ffff", width=2)

        curr_t = time.time()
        for i, (dist, ang, ts) in enumerate(self.targets):
            if curr_t - ts > 1.8: continue
            r_scale = (min(dist, MAX_DISTANCE) / MAX_DISTANCE) * self.radius
            tx, ty = self.center_x + r_scale*math.cos(ang), self.center_y + r_scale*math.sin(ang)
            self.canvas.create_oval(tx-4, ty-4, tx+4, ty+4, fill="#ffff00", outline="")

        # 8. RANGE READOUT
        self.canvas.create_text(self.center_x, 575, text=f"DETECTION_RANGE: {self.current_dist}CM", 
                                fill="#00ffff", font=("Courier", 14, "bold"))

        self.root.after(20, self.render)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinalProjectHUD(root)
    root.mainloop()