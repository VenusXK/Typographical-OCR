from matplotlib import pyplot as plt
from torchvision.datasets import ImageFolder
import numpy as np
import alexnet

import torch
from torchvision import transforms, datasets
import torch.nn as nn
from torch.utils.data import DataLoader
 
device = torch.device("cuda")

transforms = transforms.Compose([
    transforms.ToTensor()          #把图片进行归一化，并把数据转换成Tensor类型
])

path_test = r'D:\Project\PythonPrj\MachineLearning\ocr\dataset\out_dir\test3755'
path_train = r'D:\Project\PythonPrj\MachineLearning\ocr\dataset\out_dir\train3755'

data_test = ImageFolder(path_test, transform=transforms)
data_train = ImageFolder(path_train, transform=transforms)
test_len = len(data_test)

batch_size = 32;

test_loader = DataLoader(data_test, batch_size = batch_size, shuffle=True)
train_loader = DataLoader(data_train, batch_size = batch_size, shuffle=True)

model = alexnet.Alexnet()
model.load_state_dict(torch.load('model_final_48000.pth'))
model = model.to(device)
learnstep = 0.0000001
# optim = torch.optim.SGD(model.parameters(),lr=learnstep)
opt_Adam = torch.optim.Adam(model.parameters(), lr=learnstep)
loss = torch.nn.CrossEntropyLoss()

epochs = 10


train_step = 0 #每轮训练的次数
model.train()


for epoch in range(epochs):
    print("epoch {}".format(epoch+1))
    for i, data in enumerate(train_loader):
        # 打印数据集中的图片
        # img = torchvision.utils.make_grid(images).numpy()
        # plt.imshow(np.transpose(img, (1, 2, 0)))
        # plt.show()
        images, labels = data

        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        result_loss = loss(outputs,labels)
        opt_Adam.zero_grad()
        result_loss.backward()
        opt_Adam.step()
        train_step = train_step+1

        if(train_step%300==0):
            print("Loss {} {}".format(train_step,result_loss.item()))
            loss_txt = open('./loss.txt','a')
            loss_txt.write(str(train_step)+' '+str(result_loss.item())+'\n')
            loss_txt.close()
            test_total_loss = 0
            right_number = 0
            test_step = 0
            with torch.no_grad(): # 验证的部分，不是训练所以不要带入梯度
                for test_data  in test_loader:
                    img_test,label_test = test_data

                    img_test = img_test.to(device)
                    label_test = label_test.to(device)

                    outputs_test = model(img_test)
                    test_result_loss=loss(outputs_test,label_test)
                    right_number += (outputs_test.argmax(1)==label_test).sum()
                    test_step = test_step + 1 
                    if(test_step == 30):
                        break;
                print("Accuracy {} {}".format((train_step),'%.16f'%((right_number/(batch_size*test_step)).float())))
                accuracy_txt = open('./accuracy.txt','a')
                accuracy_txt.write(str(train_step)+' '+str('%.16f'%((right_number/(batch_size*test_step)).float()))+'\n')
                accuracy_txt.close()
        if(train_step%1000 == 0):
            torch.save(model.state_dict(),"model_{}.pth".format(train_step))