# HOI Labeling Tool
This UI the easy creation for labeling Human-Object-Interactions was created while writing my Bachelor Thesis about "..." at ScaDS.AI Dresden/Leipzig.

![Gif of HOI Labeling Tool usage](/images/labeling_example.gif)


## Installtion
This is a simple python file written with the tkinter frame work.
```
pip install -r requirements.txt
```

## Usage
Load images from your specified directory. 

### Step 1: Label Person
Select Person Button on the right hand side.
Draw a tight box around each person involved in the interaction.
In case of labeling error select on of the four vertex of the box and adjust 
or select the middle boxen of a box and move it in its entirety around.
Repeat this until all people are labeled.

### Step 2: Label Object
Select Object Button below the Person Button the right hand side.
Draw a tight box around each object involved in the interaction.
In case of labeling error select on of the four vertex of the box and adjust 
or select the middle boxen of a box and move it in its entirety around.
repeat this until all object are labeled.

### Step 3: Label Interaction
Select the Interaction Button below the Object Button on the right hand side.
Select the bounding box of a human and then of the object participating the HOI.
After selecting two Bounding Boxes a pop up will appear for selecting the correct 
interaction.
Repeat this until all interactions are labeled.

### Step 4: Next Image
Now you can move on to the next image. In case you are labeling Date from a Video
sequence as i have. you can check the checkbox to copy the annotions from the current
frame to the next or previous frame and just drag and resize to fit the next frame.

## Additional Features
- All Labeling related Buttons can also be used via shortcut which is also displayed 
on the button itself
- in case of mistakes all labels can be removed from the image again with the reset button.

## Misc
- If one wants to change the predifined object and interactions you can use the `config.json`
file to adjust the list of objects and interactions 
- The Output Format is in the by ... proposed odgt format. but this repo also in cludes the `odgt_to_hico.py` 
which can convert the odgt format to the format provided by the authors of the hico-det dataset