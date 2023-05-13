import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from torchvision.models.resnet import ResNet50_Weights
import matplotlib.pyplot as plt
import os


# Set the working directory to the parent directory of the script
script_path = os.path.abspath(__file__)
parent_path = os.path.dirname(script_path)
os.chdir(parent_path)

num_classes = 20

# Define data transforms for image preprocessing
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load train and validation datasets using ImageFolder

# train_dataset = ImageFolder('D:\\code\\CSCI6221\\Food-101\\train', transform=transform)
# valid_dataset = ImageFolder('D:\\code\\CSCI6221\\Food-101\\valid', transform=transform)
train_dataset = ImageFolder('D:\\code\\CSCI6221\\Data\\train', transform=transform)
valid_dataset = ImageFolder('D:\\code\\CSCI6221\\Data\\valid', transform=transform)
# train_dataset = ImageFolder('D:\\code\\CSCI6221\\Dataset\\train', transform=transform)
# valid_dataset = ImageFolder('D:\\code\\CSCI6221\\Dataset\\valid', transform=transform)

# Load pre-trained ResNet-50 model and replace the last fully connected layer with a new one for our task
model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)  
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, num_classes)  

criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(model.parameters(), lr=0.0001)

num_epochs = 30  
batch_size = 32  
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
valid_loader = DataLoader(valid_dataset, batch_size=batch_size, shuffle=True)

train_losses = []  
valid_losses = []  

valid_accs = []  

# Training loop
for epoch in range(num_epochs):

    model.train()   # Set the model to training mode
    num=0
    train_loss=0
    for inputs, labels in train_loader:
        num+=1
        print("Epoch:%d|%d/%d   " % ((epoch+1),num, len(train_loader)))

        outputs = model(inputs)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    avg_train_loss = train_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    model.eval()   # Set the model to evaluation mode
    valid_loss = 0.0
    correct = 0
    total = 0
    num=0
    with torch.no_grad():
        for inputs, labels in valid_loader:
            num+=1
            print("Epoch:%d|%d/%d   " % ((epoch+1),num, len(valid_loader)))

            outputs = model(inputs)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            loss = criterion(outputs, labels)
            valid_loss += loss.item()
        valid_losses.append(valid_loss / len(valid_loader))
        accuracy = correct / total 
        valid_accs.append(accuracy)

    print(f'Epoch [{epoch+1}/{num_epochs}], '
          f'Train Loss: {train_losses[-1]:.4f}, '
          f'Valid Loss: {valid_losses[-1]:.4f}, '
          f'Valid Accuracy: {accuracy:.4f}')
        
# Plot the training and validation losses over epochs    
plt.plot(train_losses, label='Train Loss')
plt.plot(valid_losses, label='Valid Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
        
# Plot the valid accuracy over epochs
plt.plot(valid_accs, label='Valid Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# save the model in a .pth file
torch.save(model.state_dict(), 'finalmodel.pth')
