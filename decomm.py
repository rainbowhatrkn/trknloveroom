#!/usr/bin/env python3

import os
import argparse

def remove_python_comments(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if not line.strip().startswith("#"):
                file.write(line)

def remove_bash_comments(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if not line.strip().startswith("#"):
                file.write(line)

def remove_c_cpp_comments(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    inside_block_comment = False
    with open(file_path, 'w') as file:
        for line in lines:
            if '/*' in line:
                inside_block_comment = True
            if '*/' in line:
                inside_block_comment = False
                continue
            if inside_block_comment or line.strip().startswith("//"):
                continue
            file.write(line)

def remove_java_comments(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    inside_block_comment = False
    with open(file_path, 'w') as file:
        for line in lines:
            if '/*' in line:
                inside_block_comment = True
            if '*/' in line:
                inside_block_comment = False
                continue
            if inside_block_comment or line.strip().startswith("//"):
                continue
            file.write(line)

def process_file(file_path, lang):
    if lang == 'python' or lang == 'bash':
        remove_python_comments(file_path)
    elif lang in ['c', 'cpp', 'h']:
        remove_c_cpp_comments(file_path)
    elif lang == 'java':
        remove_java_comments(file_path)
    else:
        print(f"Unsupported language for file: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Remove comments from source code files.")
    parser.add_argument('-l', '--lang', required=True, choices=['python', 'bash', 'c', 'cpp', 'h', 'java'],
                        help="Specify the programming language.")
    parser.add_argument('files', nargs='+', help="Files to process.")

    args = parser.parse_args()

    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue

        process_file(file_path, args.lang)
        print(f"Processed file: {file_path}")

if __name__ == "__main__":
    main()