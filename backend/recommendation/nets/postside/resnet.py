import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

def build_resnet50():
    # Load a pre-trained ResNet model
    model = models.resnet50(pretrained=True)
    weights=models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.eval()  # Set to evaluation mode

    # Remove the final classification layer to get feature embeddings
    model = torch.nn.Sequential(*list(model.children())[:-1])

    # Preprocess image (resize, normalize, etc.)
    preprocess = weights.transforms()
    '''
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    '''
    return model, preprocess


def get_image_embeddings(img_path):
    model, preprocess = build_resnet50()
    # Load and preprocess image

    img = Image.open(img_path)
    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension

    # Get image embeddings
    with torch.no_grad():
        img_embeddings = model(img_tensor)
    img_embeddings = img_embeddings.view(img_embeddings.size(0), -1)
    
    return img_embeddings

'''
# Load and preprocess image

current_directory = os.getcwd()
#parent_directory = os.path.dirname(current_directory)
data_path = os.path.join(current_directory, 'recommendation','datasets', 'celebA_50k')
img_path = os.path.join(data_path, '000001.jpg')
#print(img_path)
img_embeddings = get_image_embeddings(img_path)
print(img_embeddings.shape)  # Should be [1, 2048] for ResNet50
'''