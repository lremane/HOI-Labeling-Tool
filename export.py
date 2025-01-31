import os
import glob

def export_annotations(label_dir_path, odgt_output_path):
    txt_files = glob.glob(os.path.join(label_dir_path, "*.txt"))
    txt_files.sort()

    annotations = []
    for txt_file in txt_files:
        with open(txt_file, 'r') as file:
            anno = file.read()
            annotations.append(anno)

    with open(odgt_output_path, 'w') as file:
        for annotation in annotations:
            file.write(annotation + '\n')
