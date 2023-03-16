import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
from PIL import Image, ImageTk, ImageCms, UnidentifiedImageError
import math


class Spraypaint(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Ash | Superior™ Spraypaint Program<3")

        self.colors = {
            (0, 0, 0): 1,
            (255, 255, 255): 2,
            (255, 0, 0): 3,
            (0, 255, 0): 4,
            (0, 0, 255): 5,
            (255, 255, 0): 6,
            (255, 0, 255): 7,
            (0, 255, 255): 8,
            (255, 201, 0): 9,
            (255, 151, 0): 10,
            (255, 79, 0): 11,
            (151, 0, 151): 12,
            (100, 0, 201): 13,
            (79, 0, 255): 14,
            (156, 255, 0): 15
        }

        self.yuv_colors = {
            (0, 0, 0): (0.0, 0.0, 0.0),
            (255, 255, 255): (255.0, 0.0025499999999851752, 1.4210854715202004e-14),
            (255, 0, 0): (76.24499999999999, -37.518150000000006, 156.825),
            (0, 255, 0): (149.685, -73.6593, -131.32244999999998),
            (0, 0, 255): (29.07, 111.17999999999999, -25.50255),
            (255, 255, 0): (225.93, -111.17745000000001, 25.502550000000014),
            (255, 0, 255): (105.315, 73.66184999999999, 131.32245),
            (0, 255, 255): (178.755, 37.52069999999999, -156.825),
            (255, 201, 0): (194.23199999999997, -95.57901000000001, 53.31201),
            (255, 151, 0): (164.882, -81.13601, 79.06151),
            (255, 79, 0): (122.618, -60.33809000000001, 116.14079),
            (151, 0, 151): (62.363, 43.619369999999996, 77.76348999999999),
            (100, 0, 201): (52.814, 72.923, 41.39799),
            (79, 0, 255): (52.691, 99.55672999999999, 23.08245),
            (156, 255, 0): (196.329, -96.61158, -35.38244999999998)
        }

        self.lab_colors = {
            (0, 0, 0): (0.0, 0.0, 0.0),
            (255, 255, 255): (100.0, 0.00526049995830391, -0.010408184525267927),
            (255, 0, 0): (53.23288178584245, 80.10930952982204, 67.22006831026425),
            (0, 255, 0): (87.73703347354422, -86.18463649762525, 83.18116474777854),
            (0, 0, 255): (32.302586667249486, 79.19666178930935, -107.86368104495168),
            (255, 255, 0): (97.13824698129729, -21.555908334832285, 94.48248544644461),
            (255, 0, 255): (60.319933664076004, 98.25421868616114, -60.84298422386232),
            (0, 255, 255): (91.11652110946342, -48.079618466228716, -14.138127754846131),
            (255, 201, 0): (83.45989067269004, 5.220399387155128, 84.7105016558785),
            (255, 151, 0): (71.82104619984888, 31.20197428846022, 76.9550389197525),
            (255, 79, 0): (58.83705295069808, 64.32147669714483, 69.56374584954908),
            (151, 0, 151): (35.62305062867866, 66.45947214842049, -41.15439183704076),
            (100, 0, 201): (31.638701076460855, 69.57205665248453, -77.87819101709967),
            (79, 0, 255): (35.756618152948725, 80.49356496010223, -102.00955449898356),
            (156, 255, 0): (91.0475141847166, -59.21479946946195, 87.2021193938955)
        }

        self.file_name = ""
        self.code = bytearray([0 for _ in range(65536)])
        self.dithering = tk.BooleanVar()
        self.distance_formula = tk.StringVar()
        self.closeness = self.euclidean_rgb
        self.red_k = tk.DoubleVar()
        self.green_k = tk.DoubleVar()
        self.blue_k = tk.DoubleVar()
        self.red_k.set(1)
        self.green_k.set(1)
        self.blue_k.set(1)

        self.container = tk.Frame(self)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.pack(side="top", fill="both", expand=True)

        self.real_image = Image.new("RGBA", (512, 512), color=(255, 255, 255, 0))
        self.image = ImageTk.PhotoImage(Image.new("RGBA", (512, 512), color=(180, 175, 151, 64)))
        self.image_display = ttk.Label(self.container, image=self.image, borderwidth=1, relief="solid")
        self.image_display.pack(padx=15, pady=15)

        self.color_distance = ttk.OptionMenu(self.container, self.distance_formula, "Euclidean (RGB)", "Euclidean (RGB)", "Euclidean (YUV)", "Euclidean (Lab)", "Delta E 1994 (Lab)", command=self.update_closeness)
        self.color_distance.pack(padx=30, pady=5)

        self.red_coefficient = ttk.Scale(self.container, from_=0, to=1, variable=self.red_k)
        self.green_coefficient = ttk.Scale(self.container, from_=0, to=1, variable=self.green_k)
        self.blue_coefficient = ttk.Scale(self.container, from_=0, to=1, variable=self.blue_k)
        self.red_coefficient.pack(padx=30, pady=5)
        self.green_coefficient.pack(padx=30, pady=5)
        self.blue_coefficient.pack(padx=30, pady=5)

        self.update_button = ttk.Button(text="Update image", command=lambda:self.update_image(self.file_name))
        self.update_button.pack(padx=30, pady=5)

        self.dithering_checkbox = ttk.Checkbutton(self.container, text="Dithering", variable=self.dithering, onvalue=True, offvalue=False, command=self.update_image)
        self.dithering_checkbox.pack(padx=30, pady=5)

        self.upload_button = ttk.Button(text="Upload an image", command=self.file_dialog)
        self.save_button = ttk.Button(text="Save spraypaint", command=self.save_code)
        self.upload_button.pack(padx=30, pady=5)
        self.save_button.pack(padx=30, pady=5)

    def file_dialog(self):
        previous_file_name = self.file_name
        self.file_name = tk.filedialog.askopenfilename(title="Select an Image", filetypes=[("All files", ".*")])
        self.update_image(previous_file_name)

    def update_image(self, previous_file_name=""):
        try:
            self.real_image = Image.open(self.file_name).resize((256, 256)).convert("RGBA")
            self.convert_image()

            self.code = self.set_code()

            self.image = ImageTk.PhotoImage(self.real_image.resize((512, 512)))
        except (UnidentifiedImageError, AttributeError):
            self.file_name = previous_file_name
        else:
            self.image_display.config(image=self.image)

    def update_closeness(self, distance_formula):
        if distance_formula == "Euclidean (RGB)":
            self.closeness = self.euclidean_rgb
        elif distance_formula == "Euclidean (YUV)":
            self.closeness = self.euclidean_yuv
        elif distance_formula == "Euclidean (Lab)":
            self.closeness = self.euclidean_lab
        elif distance_formula == "Delta E 1994 (Lab)":
            self.closeness = self.delta_e1994

        self.update_image()

    def save_code(self):
        self.directory = tk.filedialog.asksaveasfilename(title="Save as...", filetypes=[("DAT file", ".dat"), ("All files", ".*")], initialfile="spray.dat", defaultextension=".dat")
        try:
            with open(self.directory, "wb") as data:
                data.write(self.code)
        except FileNotFoundError:
            pass

    def convert_image(self):
        for y in range(self.real_image.height):
            for x in range(self.real_image.width):
                old_pixel = self.real_image.getpixel((x, y))
                if old_pixel[3] > 127:
                    old_pixel = old_pixel[:3]
                    new_pixel = min(self.colors.keys(), key=lambda color: self.closeness(color, old_pixel))
                    self.real_image.putpixel((x, y), (*new_pixel, 255))

                    if self.dithering.get():
                        quant_error = [x[0] - x[1] for x in zip(old_pixel, new_pixel)] + [0]
                        quant_error[0] = round(quant_error[0] * self.red_k.get())
                        quant_error[1] = round(quant_error[1] * self.green_k.get())
                        quant_error[2] = round(quant_error[2] * self.blue_k.get())

                        for n, a, b in ((7, 1, 0), (3, -1, 1), (5, 0, 1), (1, 1, 1)):
                            try:
                                self.real_image.putpixel((x + a, y + b), tuple(min(255, max(0, pixel + quant_error[i] * n // 16)) for i, pixel in enumerate(self.real_image.getpixel((x + a, y + b)))))
                            except IndexError:
                                pass
                else:
                    self.real_image.putpixel((x, y), (*old_pixel[:3], 0))

    def euclidean_rgb(self, pixel_1, pixel_2):
        return (pixel_1[0] - pixel_2[0])**2 + (pixel_1[1] - pixel_2[1])**2 + (pixel_1[2] - pixel_2[2])**2

    def euclidean_lab(self, pixel_1, pixel_2):
        #pixel_1 = self.rgb_to_lab(pixel_1)
        pixel_1 = self.lab_colors[pixel_1]
        pixel_2 = self.rgb_to_lab(pixel_2)

        return (pixel_1[0] - pixel_2[0])**2 + (pixel_1[1] - pixel_2[1])**2 + (pixel_1[2] - pixel_2[2])**2

    def euclidean_yuv(self, pixel_1, pixel_2):
        #pixel_1 = self.rgb_to_yuv(pixel_1)
        pixel_1 = self.yuv_colors[pixel_1]
        pixel_2 = self.rgb_to_yuv(pixel_2)

        return (pixel_1[0] - pixel_2[0])**2 + (pixel_1[1] - pixel_2[1])**2 + (pixel_1[2] - pixel_2[2])**2

    def delta_e1994(self, pixel_1, pixel_2, k_L=1, k_C=1, k_H=1, k_1=0.048, k_2=0.014):
        #pixel_1 = self.rgb_to_lab(pixel_1)
        pixel_1 = self.lab_colors[pixel_1]
        pixel_2 = self.rgb_to_lab(pixel_2)

        L_1, a_1, b_1 = pixel_1
        L_2, a_2, b_2 = pixel_2

        C_1 = math.hypot(a_1, b_1)
        C_2 = math.hypot(a_2, b_2)

        s_L = 1
        s_C = 1 + k_1 * C_1
        s_H = 1 + k_2 * C_1

        delta_L = L_1 - L_2
        delta_C = C_1 - C_2
        delta_a = a_1 - a_2
        delta_b = b_1 - b_2

        delta_H = math.sqrt(max(0, delta_a**2 + delta_b**2 - delta_C**2))

        L = (delta_L / (k_L * s_L)) ** 2
        C = (delta_C / (k_C * s_C)) ** 2
        H = (delta_H / (k_H * s_H)) ** 2

        return L + C + H

    def rgb_to_lab(self, pixel):
        RGB = [100 * ((color / 255 + 0.055) / 1.055)**2.4 if color > 0.04045 else 100 * color / 255 / 12.92 for color in pixel]

        XYZ = [None, None, None]

        for i, a, b, c, d in ((0, 0.4124, 0.3576, 0.1805, 95.047), (1, 0.2126, 0.7152, 0.0722, 100.0), (2, 0.0193, 0.1192, 0.9505, 108.883)):
            XYZ[i] = (a * RGB[0] + b * RGB[1] + c * RGB[2]) / d

        XYZ = [color**(1/3) if color > 0.008856 else 7.787 * color + 16 / 116 for color in XYZ]

        return 116 * XYZ[1] - 16, 500 * (XYZ[0] - XYZ[1]), 200 * (XYZ[1] - XYZ[2])

    def rgb_to_yuv(self, pixel):
        return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2], -0.14713 * pixel[0] - 0.28886 * pixel[1] + 0.436 * pixel[2], 0.615 * pixel[0] - 0.51499 * pixel[1] - 0.10001 * pixel[2]

    def set_code(self):
        code = bytearray()
        for x in range(self.real_image.width - 1, -1, -1):
            for y in range(self.real_image.height):
                pixel = self.real_image.getpixel((x, y))
                if pixel[3] > 127:
                    code.append(self.colors[tuple(pixel[:3])])
                else:
                    code.append(0)

        return code


app = Spraypaint()
app.mainloop()
