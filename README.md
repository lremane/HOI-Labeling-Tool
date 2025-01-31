# HOI Labeling Tool

The **HOI Labeling Tool** is a user-friendly interface designed for efficiently labeling **Human-Object Interactions (HOI)**. This tool was developed as part of my Bachelor Thesis at **ScaDS.AI Dresden/Leipzig**.

![HOI Labeling Tool in action](/images/labeling_example.gif)

---

## Installation
This tool is implemented in Python using the **Tkinter** framework. To install the required dependencies, simply run:

```sh
pip install -r requirements.txt
```

You also need the system package `Tk` library, if not already installed.

---

## Usage

The tool enables labeling of people, objects, and their interactions in images. Follow these steps to annotate your data:

### Step 1: Label People
1. Click the **Person** button on the right-hand side.
2. Draw a **tight bounding box** around each person involved in the interaction.
3. To adjust the bounding box:
   - Drag one of the four vertices to resize it.
   - Drag the middle of the box to reposition it.
4. Repeat until all people are labeled.

### Step 2: Label Objects
1. Click the **Object** button below the Person button.
2. Draw a **tight bounding box** around each object involved in the interaction.
3. Adjust the bounding box as needed using the same method as in Step 1.
4. Repeat until all objects are labeled.

### Step 3: Label Interactions
1. Click the **Interaction** button below the Object button.
2. Select the bounding box of a human, then the bounding box of the corresponding object.
3. A pop-up window will appear for selecting the appropriate interaction type.
4. Repeat until all interactions are labeled.

### Step 4: Move to the Next Image
- Click **Next Image** to proceed.
- If you are labeling frames from a **video sequence**, enable the checkbox to **copy annotations** from the current frame to the next. You can then adjust the bounding boxes accordingly.

### Step 5: Export Your Labels
- Click the **Export** button at the bottom of the interface.
- You will be prompted to choose a location to save the annotations.
- The annotations will be exported in the **ODGT format**.
- For details on format conversion, refer to the **Customization** section.

---

## Additional Features
- **Keyboard Shortcuts:** All labeling actions can be performed using shortcuts, which are displayed on the respective buttons.
- **Reset Option:** If you make a mistake, you can remove all labels from the current image using the **Reset** button.

---

## Customization
- The list of predefined **objects** and **interactions** can be modified in the `config.json` file.
- The annotations are saved in the **ODGT format** (proposed by [Zou et al.](https://arxiv.org/abs/2103.04503)). More information about the ODGT format can be found [here](https://github.com/bbepoch/HoiTransformer#Annotations).
- The repository also includes `misc/odgt_to_hico.py` to convert ODGT annotations to the format used by the **HICO-DET dataset**.

```
python odgt_to_hico.py --input [INPUT_ODGT] --output [OUTPUT_JSON]
```

---

## License & Acknowledgments
This tool was created as part of my **Bachelor Thesis** at **ScaDS.AI Dresden/Leipzig**. The design and parts of the codebase were heavily inspired by [hoi-det-ui](https://github.com/ywchao/hoi-det-ui) and [BBox-Label-Tool](https://github.com/puzzledqs/BBox-Label-Tool).  

Feel free to modify and extend it as needed.  

For any issues or suggestions, please open an **issue** on this repository.  

Happy labeling! 🎯  


