import torch
import torchvision.transforms as transforms
import torchvision.models as models
import numpy as np
from PIL import Image
import os
# print(os.getcwd())

import torch
# print(torch.__version__)
# print(torch.version.cuda)

# Set the current directory to the directory where the script is located
script_path = os.path.abspath(__file__)
parent_path = os.path.dirname(script_path)
os.chdir(parent_path)


def load_labels(label_file):
    # Load labels from a label file
    with open(label_file, 'r') as f:
        labels = [line.strip() for line in f.readlines()]
    return labels

# Predict the food category from an image using the trained model
def predict_food(img, model, labels, transform):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)
    img = transform(img)
    img = img.unsqueeze(0)

    with torch.no_grad():
        output = model(img)
        _, preds = torch.max(output, 1)

    return labels[preds]

# Load the trained model and perform food recognition on the input image
def recognize(img):
    # model_path = './resnet50_food.pth'
    model_path = './model.pth'
    # model_path = './model1.pth'
    label_file = './food_labels.txt'

    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    labels = load_labels(label_file)

    model = models.resnet50()
    model.fc = torch.nn.Linear(model.fc.in_features, len(labels))
    model.load_state_dict(torch.load(model_path))
    model.eval()

    food = predict_food(img, model, labels, transform)
    # print(f'Predicted food: {food}')
    return food


if __name__ == '__main__':
    # Test: load an image and perform food recognition
    img = Image.open('test.jpg')
    print(recognize(img))