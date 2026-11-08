import torch
from torch import nn
from torch.nn import functional as F


class Classifier(nn.Module):
    def __init__(self, classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv3d(3, 12, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(12, 24, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool3d(1),
        )
        self.head = nn.Linear(24, classes)

    def forward(self, x):
        return self.head(self.features(x).flatten(1))


class Purifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 16, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 3, 3, padding=1),
        )
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, x):
        b, c, t, h, w = x.shape
        frames = x.permute(0, 2, 1, 3, 4).reshape(b * t, c, h, w)
        clean = (frames - self.net(frames)).clamp(0, 1)
        return clean.reshape(b, t, c, h, w).permute(0, 2, 1, 3, 4)


def fgsm(model, x, y, epsilon):
    pixels = x.detach().requires_grad_(True)
    loss = F.cross_entropy(model(pixels), y)
    (gradient,) = torch.autograd.grad(loss, pixels)
    return (pixels + epsilon * gradient.sign()).clamp(0, 1).detach()
