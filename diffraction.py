import tkinter
import math
import sys

class Application(tkinter.Frame):

    pixel_size = 600
    grid_step = 15
    grid_size = int(pixel_size/grid_step)
    color_grid_size = 300
    color_grid_step = int(pixel_size/color_grid_size)

    def __init__(self, master, color):
        tkinter.Frame.__init__(self, master)
        self.color = color
        self.prev_x = -1
        self.prev_y = -1
        self.grid()
        self.flag = 0
        self.create_widgets()
        self.draw_finished = 0

        # Points of hole
        self.points = []

        # Hole matrix
        self.matrix = [[0 for x in range(Application.grid_size)]
                       for y in range(Application.grid_size)]

        # Diffraction pattern matrix
        self.color_matrix = [[0 for x in range(Application.color_grid_size)]
                             for y in range(Application.color_grid_size)]

        #======================= Physical parameters =======================
        # In micrometers:

        # Distance between hole and lens
        self.L = 2*10**5
        
        # Pixel length
        self.pixel_len = 10

        # Wave length
        self.Lambda = 500*10**(-2)


    def create_widgets(self):
        self.canvas = tkinter.Canvas(self, width=Application.pixel_size,
                                     height=Application.pixel_size)
        self.canvas.grid()
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.change_flag)


    # Summing field in direction (s_x, s_y, s_z=sqrt(1 - s_x^2 - s_y^2))
    def summing_tension(self, s_x, s_y, default_e, x_rel, y_rel):
        e = 0
        for i in range(Application.grid_size):
            for j in range(Application.grid_size):
                if self.matrix[i][j] != 0:
                    x_c = (i * Application.grid_step - x_rel) * self.pixel_len
                    y_c = (j * Application.grid_step - y_rel) * self.pixel_len
                    e += default_e * math.cos((x_c*s_x + y_c*s_y) * 2 * math.pi/self.Lambda)
        return abs(e)


    # Calculating whole diffraction pattern
    def calc_intensity(self):
        x_rel, y_rel = self.center_of_mass()
        progress = 0
        for i in range(Application.color_grid_size):
            for j in range(Application.color_grid_size):

                # (i, j)-th direction
                s_x = (Application.color_grid_step * i - Application.pixel_size/2) * self.pixel_len
                s_y = (Application.color_grid_step * j - Application.pixel_size/2) * self.pixel_len
                ro = math.sqrt(s_x**2 + s_y**2 + self.L**2)
                s_x /= ro
                s_y /= ro

                alpha = math.pi*self.pixel_len*s_x/self.Lambda
                beta = math.pi*self.pixel_len*s_y/self.Lambda

                if alpha == 0:
                    a_s = 1
                else:
                    a_s = math.sin(alpha)/alpha

                if beta == 0:
                    b_s = 1
                else:
                    b_s = math.sin(beta)/beta

                d = self.pixel_len*Application.grid_step
                default_e = d**2*a_s*b_s

                # Summing fields in direction (s_x, s_y, s_z)
                self.color_matrix[Application.color_grid_size - j - 1][i] = self.summing_tension(s_x, s_y, default_e, x_rel, y_rel)

                progress+=1
                percentage = 100*progress/(Application.color_grid_size**2)
                if percentage % 5 == 0:
                    print(str(int(percentage)) + "%")


    def change_flag(self, event):
        self.flag = (self.flag+1)%2


    def stop_drawing(self):
        self.canvas.bind("<B1-Motion>", lambda e: None)
        self.color_int()
        self.calc_intensity()
        self.display_diff_picture()


    # For 'fancy' mode
    def gauss(self, x, x0, rec, barrier=0.5):
        if x < barrier:
            return 0
        else:
            return int(254*math.e**(-((x/255 - x0)*rec)**2))


    def display_diff_picture(self):
        maximum = -999999
        minimum = 999999
        for i in range(Application.color_grid_size):
            for j in range(Application.color_grid_size):
                if maximum < self.color_matrix[i][j]:
                    maximum = self.color_matrix[i][j]
                if minimum > self.color_matrix[i][j]:
                    minimum = self.color_matrix[i][j]

        for i in range(Application.color_grid_size):
            for j in range(Application.color_grid_size):
                self.color_matrix[i][j] = int((self.color_matrix[i][j] - minimum)/(maximum - minimum) * 255)

        step = Application.color_grid_step
        fancy_mask = [0, 0, 0]
        mask = [0, 0, 0]
        if self.color == "fancy":
            fancy_mask = [1, 1, 1]
        elif self.color == "red":
            mask = [1, 0, 0]
        elif self.color == "green":
            mask = [0, 1, 0]
        elif self.color == "blue":
            mask = [0, 0, 1]
        elif self.color == "yellow":
            mask = [1, 1, 0]
        elif self.color == "magneta":
            mask = [1, 0, 1]
        elif self.color == "cyan":
            mask = [0, 1, 1]
        else:
            mask = [1, 1, 1]

        for i in range(Application.color_grid_size):
            for j in range(Application.color_grid_size):
                colorval = "#%02x%02x%02x" % (mask[0]*self.color_matrix[i][j] + fancy_mask[0]*self.gauss(self.color_matrix[i][j], 0.6, 1.5, 10),
                                              mask[1]*self.color_matrix[i][j] + fancy_mask[1]*self.gauss(self.color_matrix[i][j], 0.2, 5, 5),
                                              mask[2]*self.color_matrix[i][j] + fancy_mask[2]*self.gauss(self.color_matrix[i][j], 0.02, 60, 0))
                self.canvas.create_rectangle(i*step, j*step, (i + 1)*step, (j + 1)*step, fill=colorval,  outline="")


    # Filling with 1 all points between (x_p, y_p) and (x, y)
    def color_cells(self, x_p, y_p, x, y):
        if x - x_p != 0:
            k = (y - y_p)/(x - x_p)
            if abs(k) <= 1:
                x_start = min(x_p, x)
                x_end = max(x_p, x)
                it_x = math.sqrt(1/(math.sqrt(1+k**2))) * self.grid_step
                while x_start < x_end:
                    self.matrix[int(((x_start - x)*k + y)/self.grid_step)][int(x_start/self.grid_step)] = 1
                    x_start += it_x
        
        if y - y_p != 0:
            k = (x - x_p)/(y - y_p)
            y_start = min(y_p, y)
            y_end = max(y_p, y)
            it_y = math.sqrt(1/(math.sqrt(1+k**2))) * self.grid_step
            while y_start < y_end:
                self.matrix[int(y_start/self.grid_step)][int(((y_start - y)*k + x)/self.grid_step)] = 1
                y_start += it_y


    # Mouse capturing
    def draw(self, event):
        if self.prev_x != -1 and self.flag == 0:
            self.points.append([event.x, event.y])
            self.canvas.create_line(self.prev_x, self.prev_y, event.x, event.y, fill="#000", width=2)
            self.color_cells(self.prev_x, self.prev_y, event.x, event.y)
        self.prev_x = event.x
        self.prev_y = event.y

        if self.flag != 0:
            self.flag = 0


    # Filling interior with 1(yea its crazy, i know)
    def color_int(self):
        for i in range(Application.grid_size):
            state = 0
            first_zero = -1
            first_one = -1
            j = 0
            first_one_locked = 0
            while j < Application.grid_size:
                if self.matrix[i][j] == 1:
                    if self.matrix[i][j+1] == 1:
                        if first_one_locked == 0:
                            first_one = j
                            first_one_locked = 1
                        if self.matrix[i][j+2] == 0:
                            if (((self.matrix[i+1][first_one] == 1) or (self.matrix[i+1][first_one - 1] == 1)) and 
                            ((self.matrix[i-1][j+1] == 1) or (self.matrix[i-1][j+2] == 1))) or (((self.matrix[i-1][first_one] == 1) or (self.matrix[i-1][first_one - 1] == 1)) and
                            ((self.matrix[i+1][j+1] == 1) or (self.matrix[i+1][j+2] == 1))):
                                if state == 0:
                                    state = 1
                                    first_zero = j + 2
                                    j = j + 2
                                    first_one = -1
                                    first_one_locked = 0
                                    continue
                                else:
                                    for k in range(first_zero, first_one):
                                        self.matrix[i][k] = 2
                                    first_zero = -1
                                    state = 0
                                    j = j + 2
                                    first_one = -1
                                    first_one_locked = 0
                                    continue
                            elif state == 0:
                                j = j + 2
                                first_one = -1
                                first_one_locked = 0
                                continue
                            else:
                                for k in range(first_zero, first_one):
                                    self.matrix[i][k] = 2
                                first_zero = j + 2
                                j = j + 2
                                first_one = -1
                                first_one_locked = 0
                                continue
                        j += 1
                        continue
                    if (self.matrix[i][j + 1] == 0) and (state == 0):
                        first_zero = j + 1
                        state = 1

                    elif (first_zero >= 0) and (state == 1):
                        for k in range(first_zero, j):
                            self.matrix[i][k] = 2
                        first_zero = -1
                        state = 0
                j += 1


    # Calculating geometric center of hole(it will be the point with 0 initial phase of field)
    def center_of_mass(self):
        x_rel = 0
        y_rel = 0
        num_of_cells = 0
        for i in range(Application.grid_size):
            for j in range(Application.grid_size):
                if self.matrix[i][j] > 0:
                    x_rel += i * Application.grid_step
                    y_rel += j * Application.grid_step
                    num_of_cells += 1
        x_rel /= num_of_cells
        y_rel /= num_of_cells
        return (x_rel, y_rel)


if __name__ == "__main__":
    ROOT = tkinter.Tk()
    ROOT.title("diffraction meter")

    colors = ["red", "green", "blue", "yellow", "magneta", "cyan", "fancy"]
    if (len(sys.argv) > 1):
        if (sys.argv[1] in colors):
            color = sys.argv[1]
        else:
            raise NameError("Invalid color! Only 'red', 'green', 'blue', 'yellow', 'magneta', 'cyan' and 'fancy' are available.")
    else:
        color = "white"

    APP = Application(ROOT, color)

    BUTTON1 = tkinter.Button(ROOT, text="finish", command=APP.stop_drawing)
    BUTTON1.configure(width=10, activebackground="#33B5E5")
    BUTTON1_WINDOW = APP.canvas.create_window(300, 20, window=BUTTON1)
    
    ROOT.mainloop()