import torchvision.models as models
from torchvision.models.resnet import ResNet50_Weights
import torch

import os

# print(os.getcwd())

# Set the current directory to the directory where the script is located
script_path = os.path.abspath(__file__)
parent_path = os.path.dirname(script_path)
os.chdir(parent_path)

# Load the pre-trained ResNet-50 model with ImageNet weights
model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
num_classes = 101
model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

# print(model.state_dict())

# Save the state dictionary of the modified model to a file
torch.save(model.state_dict(), "resnet50_food.pth")