import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from core.style_transfer import run_transfer
import threading
import os

class ArtifyUI:
    def __init__(self, window):
        self.window = window
        self.window.title("Artify - Image Style Blending")
        self.window.geometry("1020x720")

        self.base_img_path = None
        self.style_img_path = None
        self.result_img_path = None

        tk.Label(window, text="Artify: Merge Art with Image", font=("Verdana", 22)).pack(pady=15)

        top_frame = tk.Frame(window)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Choose Base Image", command=self.load_base).grid(row=0, column=0, padx=12)
        tk.Button(top_frame, text="Choose Art Style", command=self.load_style).grid(row=0, column=1, padx=12)
        tk.Button(top_frame, text="Apply Style", command=self.apply_style).grid(row=0, column=2, padx=12)

        self.img_frame = tk.Frame(window)
        self.img_frame.pack(pady=25)

        self.lbl_base = tk.Label(self.img_frame, text="Base")
        self.lbl_base.grid(row=0, column=0)
        self.lbl_style = tk.Label(self.img_frame, text="Style")
        self.lbl_style.grid(row=0, column=1)
        self.lbl_result = tk.Label(self.img_frame, text="Result")
        self.lbl_result.grid(row=0, column=2)

        self.panel_base = tk.Label(self.img_frame)
        self.panel_base.grid(row=1, column=0, padx=15)
        self.panel_style = tk.Label(self.img_frame)
        self.panel_style.grid(row=1, column=1, padx=15)
        self.panel_result = tk.Label(self.img_frame)
        self.panel_result.grid(row=1, column=2, padx=15)

    def load_base(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            self.base_img_path = file_path
            self.show_img(file_path, self.panel_base)
            messagebox.showinfo("Image Selected", f"Base Image Loaded: {os.path.basename(file_path)}")

    def load_style(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if file_path:
            self.style_img_path = file_path
            self.show_img(file_path, self.panel_style)
            messagebox.showinfo("Image Selected", f"Style Image Loaded: {os.path.basename(file_path)}")

    def apply_style(self):
        if not self.base_img_path or not self.style_img_path:
            messagebox.showwarning("Missing Input", "Both base and style images are required.")
            return

        def processing_task():
            self.update_title("Blending... Please wait.")
            self.disable_buttons()

            try:
                output_file = run_transfer(self.base_img_path, self.style_img_path)
                self.result_img_path = output_file
                self.show_img(output_file, self.panel_result)
                messagebox.showinfo("Success", f"Stylized image saved at:\n{output_file}")
            except Exception as ex:
                messagebox.showerror("Failure", f"Error occurred:\n{ex}")
            finally:
                self.enable_buttons()
                self.update_title("Artify - Complete")

        threading.Thread(target=processing_task).start()

    def show_img(self, path, widget, dim=(300, 300)):
        try:
            img = Image.open(path).resize(dim)
            display_img = ImageTk.PhotoImage(img)
            widget.config(image=display_img)
            widget.image = display_img
        except Exception as e:
            print(f"[ERROR] Couldn't load image {path} - {e}")

    def disable_buttons(self):
        for child in self.window.winfo_children():
            for sub in child.winfo_children():
                if isinstance(sub, tk.Button):
                    sub.config(state="disabled")

    def enable_buttons(self):
        for child in self.window.winfo_children():
            for sub in child.winfo_children():
                if isinstance(sub, tk.Button):
                    sub.config(state="normal")

    def update_title(self, message):
        self.window.title(message)

if __name__ == "__main__":
    root = tk.Tk()
    gui = ArtifyUI(root)
    root.mainloop()
