import torch
import torch.nn as nn
import torch.nn.functional as F

class FirstOrderModel(nn.Module):
    def __init__(self):
        super(FirstOrderModel, self).__init__()
        # تعريف طبقات الشبكة العصبية
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(64, 3, kernel_size=4, stride=2, padding=1),
            nn.Tanh()
        )

    def forward(self, source, driving):
        # تشفير الصور
        source_encoded = self.encoder(source)
        driving_encoded = self.encoder(driving)
        
        # دمج المعلومات
        combined = source_encoded + driving_encoded
        
        # فك التشفير
        prediction = self.decoder(combined)
        
        return {'prediction': prediction}