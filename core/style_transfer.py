import torch
from torchvision import models, transforms
from core.utils import prepare_image, to_numpy_image
import os
import matplotlib.pyplot as plt

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg_net = models.vgg19(pretrained=True).features.to(DEVICE).eval()

for p in vgg_net.parameters():
    p.requires_grad_(False)

def extract(img, net):
    layer_map = {
        '0': 'l1', '5': 'l2',
        '10': 'l3', '19': 'l4',
        '21': 'main', '28': 'l5'
    }
    out = {}
    for name, layer in net._modules.items():
        img = layer(img)
        if name in layer_map:
            out[layer_map[name]] = img
    return out

def gram(mat):
    _, ch, h, w = mat.shape
    features = mat.view(ch, h * w)
    return torch.mm(features, features.t())

def run_transfer(content_file, style_file, save_to='generated', iterations=500, log_freq=500):
    os.makedirs(save_to, exist_ok=True)

    transform_seq = transforms.Compose([
        transforms.Resize(300),
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3)
    ])

    content_tensor = prepare_image(content_file, transform_seq, DEVICE)
    style_tensor = prepare_image(style_file, transform_seq, DEVICE)
    output = content_tensor.clone().requires_grad_(True)

    style_layers = {
        'l1': 1.0, 'l2': 0.8, 'l3': 0.5, 'l4': 0.2, 'l5': 0.1
    }

    alpha = 100
    beta = 1e8

    content_feats = extract(content_tensor, vgg_net)
    style_feats = extract(style_tensor, vgg_net)
    style_grams = {k: gram(v) for k, v in style_feats.items()}

    opt = torch.optim.Adam([output], lr=0.006)

    for step in range(1, iterations + 1):
        output_feats = extract(output, vgg_net)
        loss_c = torch.mean((output_feats['main'] - content_feats['main']) ** 2)

        loss_s = 0
        for l in style_layers:
            g_out = gram(output_feats[l])
            g_style = style_grams[l]
            _, c, h, w = output_feats[l].shape
            loss_s += style_layers[l] * torch.mean((g_out - g_style) ** 2) / (c * h * w)

        total_loss = alpha * loss_c + beta * loss_s
        opt.zero_grad()
        total_loss.backward()
        opt.step()

        if step % log_freq == 0 or step == iterations:
            img_arr = to_numpy_image(output)
            result_path = os.path.join(save_to, f"styled_{step}.png")
            plt.imsave(result_path, img_arr)
            print(f"[Progress] Iteration {step} - Loss: {total_loss:.4f}")
    return result_path
