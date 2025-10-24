# SPDX-FileCopyrightText: 2025 2025 lremane
#
# SPDX-License-Identifier: MIT

import argparse
import json
from hico_classes import hico_classes_originID, hico_name2id

def main():
    parser = argparse.ArgumentParser(description='Convert ODGT file to HICO JSON format.')
    parser.add_argument('--input', required=True, help='Path to the input ODGT file')
    parser.add_argument('--output', required=True, help='Path to the output JSON file')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    json_data = []
    for line in lines:
        hico_data = {}
        data = json.loads(line)

        hico_data['file_name'] = data['file_name']

        hoi_annotations = []
        for hoi in data['hoi']:
            hoi_annotation = {
                'subject_id': hoi['subject_id'],
                'object_id': hoi['object_id'],
                'category_id': hico_name2id[hoi['interaction']]
            }
            hoi_annotations.append(hoi_annotation)
        hico_data['hoi_annotation'] = hoi_annotations

        annotations = []
        for gtbox in data['gtboxes']:
            annotation = {}
            bbox = gtbox['box']
            annotation['bbox'] = [
                bbox[0] + 1, 
                bbox[1] + 1, 
                bbox[0] + bbox[2], 
                bbox[1] + bbox[3]
            ]
            annotation['category_id'] = hico_classes_originID[gtbox['tag']]
            annotations.append(annotation)
        hico_data['annotations'] = annotations

        json_data.append(hico_data)

    with open(args.output, "w") as file:
        json.dump(json_data, file)

if __name__ == "__main__":
    main()