from PIL import Image, ImageTk
import itertools
import glob
import os
import customtkinter

class LabelTool:
    def __init__(self, master):
        # private variables
        self.parent = master
        self.image_directory = ""
        self.image_paths = []
        self.label_directory = ""
        self.image_index = 0
        self.total_images = 0
        self.current_image = None

        # shortcuts
        self.parent.bind("a", self.prev_image)
        self.parent.bind("f", self.next_image)

        # Set up the main frame
        self.parent.title('HOI Labeling Tool')
        self.parent.geometry('1000x600')

        # Main Frame
        self.main_frame = customtkinter.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True)

        # Left frame for image display
        self.left_frame = customtkinter.CTkFrame(self.main_frame, width=600, height=500)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Scrollable canvas setup
        self.canvas = customtkinter.CTkCanvas(self.left_frame)
        self.scrollbar_y = customtkinter.CTkScrollbar(self.left_frame, command=self.canvas.yview, orientation="vertical")
        self.scrollbar_x = customtkinter.CTkScrollbar(self.left_frame, command=self.canvas.xview, orientation="horizontal")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the mouse wheel and Shift+Mouse Wheel
        self.canvas.bind("<MouseWheel>", self.on_vertical_scroll)  # For vertical scrolling
        self.canvas.bind("<Shift-MouseWheel>", self.on_horizontal_scroll)  # For horizontal scrolling

        # For macOS/Linux compatibility (mouse scroll up/down)
        self.canvas.bind("<Shift-Button-4>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.canvas.bind("<Shift-Button-5>", lambda e: self.canvas.xview_scroll(1, "units"))
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))


        self.placeholder_text = self.canvas.create_text(0, 0, text="Image Display Area", font=("TkDefaultFont", 24), anchor="center")
        self.canvas.bind("<Configure>", self.update_canvas)

        # Labeling Buttons
        self.right_frame = customtkinter.CTkScrollableFrame(self.main_frame, width=300)
        self.right_frame.pack(side="right", fill="y")

        self.button_load_dir = customtkinter.CTkButton(self.right_frame, text="Load Directory", height=50, width=160, command=self.load_directory)
        self.button_load_dir.pack(pady=(20, 10), padx=10)

        self.button_person = customtkinter.CTkButton(self.right_frame, text="Person  [ P ]", height=70)
        self.button_person.pack(pady=(20, 10), padx=10)

        self.button_object = customtkinter.CTkButton(self.right_frame, text="Object  [ O ]", fg_color="green", hover_color="dark green", height=70)
        self.button_object.pack(pady=10, padx=10)

        self.button_interaction = customtkinter.CTkButton(self.right_frame, text="Interaction  [ I ]", fg_color="orange", hover_color="dark orange", height=70)
        self.button_interaction.pack(pady=10, padx=10)

        self.button_reset = customtkinter.CTkButton(self.right_frame, text="Reset  [ R ]", fg_color="red", hover_color="dark red", height=70)
        self.button_reset.pack(pady=10, padx=10)

        # Checkbox
        self.checkbox_var = customtkinter.BooleanVar()
        self.checkbox = customtkinter.CTkCheckBox(self.right_frame, text="Keep annotations for next image.", variable=self.checkbox_var)
        self.checkbox.pack(pady=10, padx=10)

        # Navigation Buttons
        self.navigation_frame = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        self.navigation_frame.pack(pady=10, padx=10)

        self.back_button = customtkinter.CTkButton(self.navigation_frame, text="Back  [ A ]", height=50, width=100, command=self.prev_image)
        self.back_button.pack(side="left", padx=10)

        self.next_button = customtkinter.CTkButton(self.navigation_frame, text="Next  [ F ]", height=50, width=100, command=self.next_image) # todo: vlt sollte der sich immer automat. deaktivieren
        self.next_button.pack(side="right", padx=10)

        self.image_index_label = customtkinter.CTkLabel(self.right_frame, text=f"{self.image_index} / {self.total_images}")
        self.image_index_label.pack(pady=20, padx=10)

    def get_checkbox_state(self):
        print(self.checkbox_var.get())

    def update_canvas(self, event=None):
        self.canvas.coords(
            self.placeholder_text,
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2
        )
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_vertical_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def on_horizontal_scroll(self, event):
        self.canvas.xview_scroll(-1 * (event.delta // 120), "units")

    def load_directory(self):
        self.image_directory = customtkinter.filedialog.askdirectory(title="Select Directory")

        allowed_extensions = ['*.jpg', '*.jpeg', '*.png']
        self.image_paths = list(itertools.chain.from_iterable(
            glob.glob(os.path.join(self.image_directory, ext)) for ext in allowed_extensions
        ))
        self.image_paths.sort()
        if len(self.image_paths) == 0:
            print('No images found.')
            return

        directory_name = os.path.basename(self.image_directory)
        self.label_directory = os.path.join("Labels", directory_name)
        os.makedirs(self.label_directory, exist_ok=True)

        self.image_index = 1
        self.total_images = len(self.image_paths)

        self.load_image()

    def load_image(self):
        image_path = self.image_paths[self.image_index - 1]
        image = Image.open(image_path)
        self.current_image = ImageTk.PhotoImage(image)

        # Clear existing canvas items
        self.canvas.delete("all")

        # Add image to canvas
        self.canvas.update_idletasks()
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.update_image_index_label()

    def prev_image(self, event=None):
        # self.save_image()
        if self.image_index <= 1:
            return

        self.image_index -= 1
        self.load_image()

    def next_image(self, event=None):
        # self.save_image()
        if self.image_index >= self.total_images:
            return

        self.image_index += 1
        self.load_image()

    def update_image_index_label(self):
        self.image_index_label.configure(text=f"{self.image_index} / {self.total_images}")

if __name__ == '__main__':
    customtkinter.set_appearance_mode('light')
    customtkinter.set_default_color_theme('blue')

    root = customtkinter.CTk()
    tool = LabelTool(root)
    root.mainloop()
