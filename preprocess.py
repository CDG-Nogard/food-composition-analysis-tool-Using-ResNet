import os
import random
import shutil
from PIL import Image

# Define folder paths
# folder_path = r'D:\code\CSCI6221\data\all'  # Replace with your folder path
folder_path = r'D:\code\CSCI6221\Dataset\images'  # Replace with your folder path

# Define target folder paths for train and validation sets
train_path = r'D:\code\CSCI6221\Dataset\train'  # Replace with your target folder path for train set
valid_path = r'D:\code\CSCI6221\Dataset\valid'  # Replace with your target folder path for validation set

# Define ratios for train and validation sets
train_ratio = 0.75  # Ratio of train set to the total dataset
valid_ratio = 0.25  # Ratio of validation set to the total dataset

# Get the list of subfolders in the main folder
dir_list = os.listdir(folder_path)

for dir in dir_list:
    file_list = os.listdir(os.path.join(folder_path, dir))

    # Shuffle the file list randomly
    random.shuffle(file_list)

    # Calculate the boundaries for train and validation sets
    train_border = int(len(file_list) * train_ratio)
    valid_border = int(len(file_list) * (train_ratio + valid_ratio))

    # Split the file list into train, validation, and test sets
    train_files = file_list[:train_border]
    valid_files = file_list[train_border:valid_border]

    dir1 = os.path.join(folder_path, dir)
    dir2 = os.path.join(train_path, dir)
    dir3 = os.path.join(valid_path, dir)

    os.makedirs(dir2)
    os.makedirs(dir3)

    # Copy files from the original folder to the target folder for train and validation sets
    for file in train_files:
        if file.endswith('.png'):
            output_filename = os.path.splitext(file)[0] + '.jpg'
            src = os.path.join(dir1, file)
            img = Image.open(src)
            # Convert to RGB mode
            img = img.convert('RGB')
            # Save as JPEG format
            dst = os.path.join(dir2, output_filename)
            img.save(dst)
        else:
            src = os.path.join(dir1, file)
            dst = os.path.join(dir2, file)
            shutil.copy(src, dst)  # Use shutil.copy() function for file copy

    for file in valid_files:
        if file.endswith('.png'):
            output_filename = os.path.splitext(file)[0] + '.jpg'
            src = os.path.join(dir1, file)
            img = Image.open(src)
            # Convert to RGB mode
            img = img.convert('RGB')
            # Save as JPEG format
            dst = os.path.join(dir2, output_filename)
            img.save(dst)
        else:
            src = os.path.join(dir1, file)
            dst = os.path.join(dir3, file)
            shutil.copy(src, dst)  # Use shutil.copy() function for file copy

    print(f"Successfully copied {len(train_files)} files to the train set folder: {train_path}")
    print(f"Successfully copied {len(valid_files)} files to the validation set folder: {valid_path}")
