import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn import init


class CNN_(nn.Module):
    def __init__(self, num_channel):
        super(CNN_, self).__init__()
        self.num_channel = num_channel
        self.bn1 = nn.BatchNorm1d(num_features=self.num_channel)
        self.conv1 = nn.Conv1d(in_channels=self.num_channel, out_channels=16, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.conv4 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.bn2 = nn.BatchNorm1d(128)
        self.maxpool = nn.MaxPool1d(kernel_size=2,stride=2)
        
    def forward(self, x):
        x = self.bn1(x)
        x = F.relu(self.conv1(x))
        x = self.maxpool(x)
        x = F.relu(self.conv2(x))
        x = self.maxpool(x)
        x = F.relu(self.conv3(x))
        x = self.maxpool(x)
        x = F.relu(self.conv4(x))
        x = self.maxpool(x)
        x = self.bn2(x)
        return x


class N_VCNN_(nn.Module):
    def __init__(self):
        super(N_VCNN_, self).__init__()
        self.num_channel = 64
        self.conv1 = nn.Conv1d(in_channels=self.num_channel, out_channels=self.num_channel * 16, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.bn1 = nn.BatchNorm1d(num_features=self.num_channel * 16)
        self.conv2 = nn.Conv1d(in_channels=self.num_channel * 16, out_channels=self.num_channel * 8, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.bn2 = nn.BatchNorm1d(num_features=self.num_channel * 8)
        self.conv3 = nn.Conv1d(in_channels=self.num_channel * 8, out_channels=self.num_channel * 4, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.bn3 = nn.BatchNorm1d(num_features=self.num_channel * 4)
        self.conv4 = nn.Conv1d(in_channels=self.num_channel * 4, out_channels=self.num_channel * 2, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)
        self.bn4 = nn.BatchNorm1d(num_features=self.num_channel * 2)
        self.conv5 = nn.Conv1d(in_channels=self.num_channel * 2, out_channels=self.num_channel, kernel_size=(3,),
                               stride=(1,),
                               padding_mode='replicate',
                               padding=1)

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        # x = F.max_pool1d(x, kernel_size=2)
        x = F.relu(self.bn2(self.conv2(x)))
        # x = F.max_pool1d(x, kernel_size=2)
        x = F.relu(self.bn3(self.conv3(x)))
        # x = F.max_pool1d(x, kernel_size=2)
        x = F.relu(self.bn4(self.conv4(x)))
        # x = F.max_pool1d(x, kernel_size=2)
        x = F.relu((self.conv5(x)))
        # print(x.shape)
        return x

class CNN_LSTM_with_Attention(nn.Module):
    def __init__(self, dropout=0.3, lstm_num=2):
        super(CNN_LSTM_with_Attention, self).__init__()
        self.num_channel = 64

        self.N_VCNN = N_VCNN_()
        self.dropout = nn.Dropout(p=dropout)

        self.lstm = nn.LSTM(input_size=self.num_channel, hidden_size=self.num_channel , dropout=dropout,
                            num_layers=lstm_num)
        self.linear = nn.Linear(in_features=self.num_channel* 160, out_features=512)
        self.attention_weight = nn.Parameter(torch.randn(self.num_channel * 160, self.num_channel  * 160))

    def forward(self, x, hidden=None):
        x = self.N_VCNN.forward(x)
        x = x.view(160, -1, self.num_channel)
        x, hidden = self.lstm(x, hidden)
        x = x.view(-1, self.num_channel * 160)  # N,20480
        attention = F.softmax(torch.mm(x,self.attention_weight), dim=1)
        # print(attention.shape)  # N，self.num_channel * 2 * 160  ## N, 20480
        x = torch.mul(x , attention)   # N,20480
        x = self.linear(x)
        return x, hidden

    def initialize(self):
        for m in self.modules():
            # 判断这一层是否为线性层，如果为线性层则初始化权值
            if isinstance(m, nn.Linear):
                init.normal_(m.weight.data)  # normal: mean=0, std=1
            # if isinstance(m, nn.Conv1d):
            #     init.normal_(m.weight.data)
            
class model1000(nn.Module):
    def __init__(self, dropout = 0.3):
        super(model1000, self).__init__()
        self.cnn = CNN_(64)
        self.linear1 = nn.Linear(in_features=128*62,out_features=128)
        self.at = nn.MultiheadAttention(embed_dim=128,num_heads=4)
        self.gru = nn.GRU(input_size=128,hidden_size=128,num_layers=2,dropout=dropout)
    def forward(self,x):
        x = self.cnn(x)
        # print(x.shape)    # 64, 128, 62
        x = x.permute(2,0,1)
        x,_ = self.gru(x)
        x,_ = self.at(x,x,x)
        x = x.permute(1,2,0)
        x = torch.flatten(x,start_dim=1)
        x = self.linear1(x)
        # print(x.shape)
        return x
        
if __name__ == "__main__":
    net = CNN_LSTM_with_Attention()
    # lstm_h = (torch.randn(2, 2, 64*3), torch.randn(2, 2, 64*3))
    inputs = torch.randn(1, 64, 160)
    # print(inputs.shape)
    results, h = net(inputs)
    print(results[0])
