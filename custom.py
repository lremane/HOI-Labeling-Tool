import json
import math
from pathlib import Path

from PIL import Image, ImageTk
import itertools
import glob
import os
import customtkinter

COLORS = {'person': 'blue', 'object': 'green', 'interaction': 'red'}

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
        self.image_width = 0
        self.image_height = 0

        self.image_name = ""
        self.label_file_name = ""

        self.object_options = (
                ['cell phone'] +
                ['cup', 'bottle'] +
                ['couch'] +
                ['apple'] +
                ['book'] +
                ['laptop']
        )
        self.object_options.sort()

        self.interaction_options = (['no_interaction', 'hold'] +
                                  ['talk_on', 'text_on'] +
                                  ['drink_with'] +
                                  ['lie_on', 'sit_on'] +
                                  ['eat'] +
                                  ['read'] +
                                  ['type_on']
        )
        self.interaction_options.sort()

        # initialize mouse state
        self.STATE = {
            'click': 0,
            'x': 0,
            'y': 0,
            'label_type': 'person',
            'label_tag': 'person'
        }

        # reference to bbox
        self.bbox_ids = [] # (bbox_id, corner_ids, text_id)
        self.bbox_id = None
        self.bbox_coordinates = [] # (x1, y1, x2, y2) -> prio bboxList
        self.bbox_tag = []
        self.bbox_type = []
        self.temp_corner_ids = []

        # interaction management
        self.selected_objects = []
        self.interaction_lines = [] #(line_id, [text])
        self.interactions = []  # To store connections

        # mouse-cursor
        self.horizontal_line = None
        self.vertical_line = None

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
        self.canvas = customtkinter.CTkCanvas(self.left_frame, cursor="tcross")
        self.scrollbar_y = customtkinter.CTkScrollbar(self.left_frame, command=self.canvas.yview, orientation="vertical")
        self.scrollbar_x = customtkinter.CTkScrollbar(self.left_frame, command=self.canvas.xview, orientation="horizontal")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Display mouse cross
        self.canvas.bind("<Button-1>", self.mouse_click)
        self.canvas.bind("<Motion>", self.mouse_move)
        self.parent.bind("<Escape>", self.cancel_bbox)  # press <Escape> to cancel current bbox


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

        self.button_person = customtkinter.CTkButton(self.right_frame, text="Person  [ P ]", height=70, command=lambda: self.set_label_type("person"))
        self.button_person.pack(pady=(20, 10), padx=10)

        self.button_object = customtkinter.CTkButton(self.right_frame, text="Object  [ O ]", fg_color="green", hover_color="dark green", height=70, command=lambda: self.set_label_type("object"))
        self.button_object.pack(pady=10, padx=10)

        self.button_interaction = customtkinter.CTkButton(self.right_frame, text="Interaction  [ I ]", fg_color="orange", hover_color="dark orange", height=70, command=lambda: self.set_label_type("interaction"))
        self.button_interaction.pack(pady=10, padx=10)

        self.button_reset = customtkinter.CTkButton(self.right_frame, text="Reset  [ R ]", fg_color="red", hover_color="dark red", height=70, command=self.reset)
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

        self.next_button = customtkinter.CTkButton(self.navigation_frame, text="Next  [ F ]", height=50, width=100, command=self.next_image) # todo: maybe this should deactivate automatically
        self.next_button.pack(side="right", padx=10)

        self.image_index_label = customtkinter.CTkLabel(self.right_frame, text=f"{self.image_index} / {self.total_images}")
        self.image_index_label.pack(pady=20, padx=10)

    @staticmethod
    def get_label_file_name(image_name, label_directory):
        image_name_without_extension = os.path.splitext(image_name)[0]
        label_name = image_name_without_extension + '.txt'
        return os.path.join(label_directory, label_name)

    def get_checkbox_state(self):
        print(self.checkbox_var.get())

    def set_label_type(self, label_type):
        self.STATE['label_type'] = label_type
        if label_type == "object":
            return

        self.STATE['label_tag'] = label_type

    def mouse_click(self, event=None):
        x_offset = int(self.canvas.canvasx(event.x))
        y_offset = int(self.canvas.canvasy(event.y))

        if self.STATE['label_type'] == 'interaction':
            self.label_interaction(x_offset, y_offset)
            return

        if self.STATE['click'] == 0:
            # Start a new bounding box
            self.STATE['x'], self.STATE['y'] = x_offset, y_offset
            self.STATE['click'] = 1
        else:
            # Finalize the bounding box
            x1, x2 = min(self.STATE['x'], x_offset), max(self.STATE['x'], x_offset)
            y1, y2 = min(self.STATE['y'], y_offset), max(self.STATE['y'], y_offset)

            self.remove_temporary_bbox()

            if self.STATE['label_type'] == 'object':
                self.show_object_selection_popup()

            bbox_id, corner_ids, text_ids  = self.draw_bbox_with_label(x1, y1, x2, y2, self.STATE['label_type'], self.STATE['label_tag'])

            # Save the bounding box and its corner IDs
            self.bbox_coordinates.append((x1, y1, x2, y2))
            self.bbox_type.append(self.STATE['label_type'])
            self.bbox_tag.append(self.STATE['label_tag'])  # Save the label type
            self.bbox_ids.append((bbox_id, corner_ids, text_ids))  # Save both bbox and corners
            self.STATE['click'] = 0
            self.bbox_id = None  # Reset the temporary bbox
            self.temp_corner_ids = []


    def draw_label_name(self, x1, x2, y1, y2, label_tag):
        label_text = label_tag  # Use the current label_tag
        text_x = (x1 + x2) / 2  # Center of the box
        if self.STATE['label_type'] == 'interaction':
            text_y = (y1 + y2) // 2
        else:
            text_y = max(y1, y2) + 10  # Slightly below the bottom edge of the box
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Offsets for the black border

        text_ids = []
        for dx, dy in offsets:
            text_id = self.canvas.create_text(
                text_x + dx, text_y + dy,
                text=label_text,
                fill='black',
                font=("TkDefaultFont", 12, "bold")
            )
            text_ids.append(text_id)

        text_id = self.canvas.create_text(
            text_x, text_y,
            text=label_text,
            fill="white",
            font=("TkDefaultFont", 12, "bold")
        )
        text_ids.append(text_id)

        return text_ids

    def mouse_move(self, event=None):
        # Calculate the scroll offset
        x_offset = self.canvas.canvasx(event.x)
        y_offset = self.canvas.canvasy(event.y)

        if not self.current_image:
            return

        self.draw_cursor(x_offset, y_offset)

        # Update bounding box preview
        if self.STATE['click'] == 1:
            self.remove_temporary_bbox()

            # Use draw bbox to create the temporary bbox and corners
            self.bbox_id, self.temp_corner_ids = self.draw_bbox(
                self.STATE['x'], self.STATE['y'], x_offset, y_offset, self.STATE['label_type'])

    def remove_temporary_bbox(self):
        if self.bbox_id:
            self.canvas.delete(self.bbox_id)
        if self.temp_corner_ids:
            for corner_id in self.temp_corner_ids:
                self.canvas.delete(corner_id)

    def cancel_bbox(self, event=None): # noqa
        if self.STATE['click'] == 0:
            return

        if self.bbox_id:
            self.canvas.delete(self.bbox_id)
            self.bbox_id = None
            self.STATE['click'] = 0

    def get_closest_bbox_index_at_point(self, x, y):
        candidates = []
        for i, (x1, y1, x2, y2) in enumerate(self.bbox_coordinates):
            if x1 <= x <= x2 and y1 <= y <= y2:
                candidates.append(i)

        if not candidates:
            return None

        best_index = None
        best_distance = float('inf')

        for i in candidates:
            (x1, y1, x2, y2) = self.bbox_coordinates[i]
            corners = [
                (x1, y1),
                (x1, y2),
                (x2, y1),
                (x2, y2)
            ]
            min_corner_distance = min(
                math.dist((x, y), corner) for corner in corners
            )

            if min_corner_distance < best_distance:
                best_distance = min_corner_distance
                best_index = i

        return best_index

    def label_interaction(self, x, y):
        closest_bbox_id = self.get_closest_bbox_index_at_point(x, y)
        if closest_bbox_id is None:
            return

        bbox_id, _, _ = self.bbox_ids[closest_bbox_id]

        if bbox_id in self.selected_objects:
            self.selected_objects.remove(bbox_id)
            self.canvas.itemconfig(bbox_id, fill="",  stipple="")
            return

        self.selected_objects.append(bbox_id)
        label_type = self.bbox_type[closest_bbox_id]
        self.canvas.itemconfig(bbox_id, fill=COLORS[label_type], stipple="gray50")

        if len(self.selected_objects) != 2:
            return

        interaction_label = self.get_interaction_label()

        sub = next((index for index, triplet in enumerate(self.bbox_ids) if triplet[0] == self.selected_objects[0]), None)
        obj = next((index for index, triplet in enumerate(self.bbox_ids) if triplet[0] == self.selected_objects[1]), None)

        line_id, line_text_ids = self.draw_interaction(sub, obj, self.STATE['label_tag'])
        self.interaction_lines.append((line_id, line_text_ids))
        interaction = {
            "object_id": obj,
            "interaction": interaction_label,
            "subject_id": sub
        }

        self.interactions.append(interaction)

        self.reset_label_interaction()

    def draw_interaction(self, sub_id, obj_id, label_tag):
        center1 = self.get_bbox_center(self.bbox_coordinates[sub_id])
        center2 = self.get_bbox_center(self.bbox_coordinates[obj_id])
        line_id = self.canvas.create_line(
            center1[0], center1[1], center2[0], center2[1], fill="orange", width=4
        )

        line_text_ids = self.draw_label_name(center1[0], center2[0], center1[1], center2[1], label_tag)

        return line_id, line_text_ids

    @staticmethod
    def get_bbox_center(bbox):
        x1, y1, x2, y2 = bbox
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2
        return x_center, y_center

    def reset_label_interaction(self):
        for bbox_id, _, _ in self.bbox_ids:
            self.canvas.itemconfig(bbox_id, fill="", stipple="")

        self.selected_objects = []

    def update_canvas(self, event=None): # noqa
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
        self.image_width = image.width
        self.image_height = image.height

        # Clear existing canvas items
        self.canvas.delete("all")

        # Add image to canvas
        self.canvas.update_idletasks()
        self.canvas.create_image(0, 0, anchor="nw", image=self.current_image)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.update_image_index_label()

        self.image_name = Path(image_path).name
        self.label_file_name = self.get_label_file_name(self.image_name, self.label_directory)
        loading_label_file_name = str(self.label_file_name)
        if not Path(loading_label_file_name).exists():
            return

        with open(loading_label_file_name, "r") as file:
            data = json.load(file)

        for gtbox in data["gtboxes"]:
            x1, y1, width, height = map(int, gtbox["box"])
            x2, y2 = x1 + width - 1, y1 + height - 1

            label_type = "person" if gtbox["tag"] == "person" else "object"
            bbox_id, corner_ids, text_ids  = self.draw_bbox_with_label(x1, y1, x2, y2, label_type, gtbox['tag'])

            self.bbox_coordinates.append((x1, y1, x2, y2))
            self.bbox_type.append(label_type)
            self.bbox_tag.append(gtbox["tag"])
            self.bbox_ids.append((bbox_id, corner_ids, text_ids))

        for conn in data["hoi"]:
            sub = conn['subject_id']
            obj = conn['object_id']
            interaction = conn['interaction']

            line_id, line_text_ids = self.draw_interaction(sub, obj, interaction)
            self.interaction_lines.append((line_id, line_text_ids))
            interaction = {
                "object_id": obj,
                "interaction": interaction,
                "subject_id": sub
            }

            self.interactions.append(interaction)

    def save_image(self):
        data = {
            "file_name": self.image_name,
            "height": self.image_height,
            "width": self.image_width,
            "gtboxes": [
                {
                    "tag": self.bbox_tag[i],
                    "box": [int(x_min), int(y_min), int(width), int(height)]
                }
                for i, bbox in enumerate(self.bbox_coordinates)
                for x_min, y_min, x_max, y_max in [bbox]
                for width, height in [(x_max - x_min + 1, y_max - y_min + 1)]
            ],
            "hoi": self.interactions
        }

        with open(self.label_file_name, 'w', encoding="utf-8") as file:
            json.dump(data, file) # type: ignore

    def prev_image(self, event=None): # noqa
        self.save_image()
        if self.image_index <= 1:
            return
        self.image_index -= 1

        self.reset()
        self.load_image()

    def next_image(self, event=None): # noqa
        self.save_image()
        if self.image_index >= self.total_images:
            return
        self.image_index += 1

        self.reset()
        self.load_image()

    def reset(self, event=None): # noqa
        for bbox_id, corner_ids, text_ids in self.bbox_ids:
            self.canvas.delete(bbox_id)
            for corner_id in corner_ids:
                self.canvas.delete(corner_id)
            for text_id in text_ids:
                self.canvas.delete(text_id)

        self.bbox_ids = []
        self.bbox_id = None
        self.bbox_coordinates = []
        self.bbox_tag = []
        self.bbox_type = []

        # interaction management
        for line, text_ids in self.interaction_lines:
            self.canvas.delete(line)
            for text_id in text_ids:
                self.canvas.delete(text_id)

        self.selected_objects = []
        self.interaction_lines = []
        self.interactions = []

    def debug_canvas_items(self):
        print("Canvas items:")
        for item_id in self.canvas.find_all():
            item_type = self.canvas.type(item_id)  # Use `type` to get the type of the canvas item
            print(f"Item {item_id}: {item_type}")

    def update_image_index_label(self):
        self.image_index_label.configure(text=f"{self.image_index} / {self.total_images}")

    def show_object_selection_popup(self):
        def enable_ok_button():
            """Enable the OK button when a radio button is selected."""
            if label_var.get():
                ok_button.configure(state="normal")

        popup = customtkinter.CTkToplevel(self.parent)
        popup.title("Select Label")
        popup.geometry("200x300")

        popup.protocol("WM_DELETE_WINDOW", lambda: None)
        popup.update_idletasks()
        popup.grab_set()

        label_var = customtkinter.StringVar(value="")
        popup_frame = customtkinter.CTkScrollableFrame(popup, width=180, height=200)
        popup_frame.pack(fill="both", expand=True)
        customtkinter.CTkLabel(popup_frame, text="Choose a label:").pack(pady=10)

        for label in self.object_options:
            radio = customtkinter.CTkRadioButton(popup_frame, text=label, variable=label_var, value=label,
                                                 command=enable_ok_button)
            radio.pack(pady=2, padx=10, anchor="w")

        ok_button = customtkinter.CTkButton(popup_frame, text="OK", state="disabled", command=lambda: self.set_label_from_popup(popup, label_var))
        ok_button.pack(pady=(20, 10))

        popup.wait_window()

    def get_interaction_label(self):
        popup = customtkinter.CTkToplevel(self.parent)
        popup.title("Select Interaction")
        popup.geometry("200x300")

        popup.protocol("WM_DELETE_WINDOW", lambda: None)

        popup.update_idletasks()
        popup.grab_set()

        popup_frame = customtkinter.CTkScrollableFrame(popup, width=180, height=200)
        popup_frame.pack(fill="both", expand=True)
        customtkinter.CTkLabel(popup_frame, text="Choose a interaction:").pack(pady=10)

        interaction_var = customtkinter.StringVar()
        for label in self.interaction_options:
            customtkinter.CTkRadioButton(popup_frame, text=label, variable=interaction_var, value=label).pack(pady=2, padx=10, anchor="w")

        customtkinter.CTkButton(popup_frame, text="OK", command=lambda: self.set_label_from_popup(popup, interaction_var)).pack(pady=(20, 10))

        popup.wait_window()
        return interaction_var.get()

    def set_label_from_popup(self, popup, label_var):
        selected_tag = label_var.get()
        self.STATE['label_tag'] = selected_tag
        popup.destroy()

    def draw_cursor(self, x, y):
        if self.horizontal_line:
            self.canvas.delete(self.horizontal_line)
        self.horizontal_line = self.canvas.create_line(0, y, self.current_image.width(), y, width=2)

        # Update vertical line
        if self.vertical_line:
            self.canvas.delete(self.vertical_line)
        self.vertical_line = self.canvas.create_line(x, 0, x, self.current_image.height(), width=2)

    def draw_bbox_with_label(self, x1, y1, x2, y2, label_type, label_tag):
        bbox_id, corner_ids = self.draw_bbox(x1, y1, x2, y2, label_type)
        text_ids = self.draw_label_name(x1, x2, y1, y2, label_tag)

        return bbox_id, corner_ids, text_ids

    def draw_bbox(self, x1, y1, x2, y2, label_type):
        # Draw the main bounding box
        bbox_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            width=2,
            outline=COLORS[label_type]
        )

        # Add red rectangles at the corners
        corner_size = 5  # Size of the corner rectangles
        corner_ids = []
        for x, y in [
            (x1, y1),
            (x1, y2),
            (x2, y1),
            (x2, y2)
        ]:
            corner_id = self.canvas.create_rectangle(
                x - corner_size, y - corner_size, x + corner_size, y + corner_size,
                fill='red', outline='red'
            )
            corner_ids.append(corner_id)

        return bbox_id, corner_ids


if __name__ == '__main__':
    customtkinter.set_appearance_mode('light')
    customtkinter.set_default_color_theme('blue')

    root = customtkinter.CTk()
    tool = LabelTool(root)
    root.mainloop()
