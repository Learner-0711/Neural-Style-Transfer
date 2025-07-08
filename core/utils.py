from PIL import Image
import torch
import numpy as np

def prepare_image(img_path, transform_pipeline, device):
    img = Image.open(img_path).convert("RGB")
    img = transform_pipeline(img).unsqueeze(0).to(device)
    return img

def to_numpy_image(tensor_img):
    img = tensor_img.to("cpu").clone().detach().numpy().squeeze()
    img = img.transpose(1, 2, 0)
    img = img * 0.5 + 0.5
    return np.clip(img, 0, 1)
