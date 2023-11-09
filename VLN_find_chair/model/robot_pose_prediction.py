import torch
import torch.nn as nn
import clip
from torchvision import transforms

imgpreprocess = transforms.Compose([
    transforms.ToPILImage(),  # 将 NumPy 数组转换为 PIL 图像
    transforms.Resize((224, 224)),  # 调整大小为 (224, 224)
    transforms.ToTensor(),  # 转换为 Tensor
    ])

class RobotPosePrediction(nn.Module):
    def __init__(self, clip_model, robot_state_dim):
        super(RobotPosePrediction, self).__init__()

        # CLIP模型用于图像和文本处理
        self.clip_model = clip_model
        self.image_feature_dim = 512  # CLIP输出的图像特征维度
        self.text_feature_dim = 512  # CLIP输出的文本特征维度

        # 机器人状态特征提取MLP
        self.robot_state_fc = nn.Sequential(
            nn.Linear(robot_state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64)
        )

        # 输出层
        self.output_layer = nn.Sequential(
            nn.Linear(self.image_feature_dim + self.text_feature_dim + 64, 128),
            nn.ReLU(),
            nn.Linear(128, 2)  # 预测机器人的[x, y]
        )

    def forward(self, img, instruction, robot_state):
        # 图像特征提取
        img_features = self.clip_model.encode_image(img)
   

        # 文本特征提取
        text_features = self.clip_model.encode_text(instruction)  # 注意：将instruction放入列表中

        # 机器人状态特征提取
        robot_state_features = self.robot_state_fc(robot_state)

        # 合并图像、文本和机器人状态特征
        combined_features = torch.cat((img_features, text_features, robot_state_features), dim=1)

        # 预测机器人的[x, y, yaw]
        predicted_pose = self.output_layer(combined_features)

        # 将yaw范围限制在[-1, 1]之间
        # predicted_pose[:, 2] = torch.clamp(predicted_pose[:, 2], -1, 1)
        predicted_pose = predicted_pose / torch.norm(predicted_pose, dim=1, keepdim=True)

        return predicted_pose

def preprocess(image,instruction,state):
    image = imgpreprocess(image).unsqueeze(0)
    instruction=clip.tokenize([instruction])
    state=torch.tensor([state])
    return image,instruction,state
        
if __name__ == '__main__':

    # 加载CLIP模型
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ClipModel, transform = clip.load("ViT-B/32", device)
    # 创建模型实例
    robot_state_dim = 3  # 机器人状态维度
    model = RobotPosePrediction(ClipModel, robot_state_dim)
    # print(model)
    # 将输入数据转换为PyTorch张量
    img = torch.randn(1, 3, 224, 224).to(device)  # 示例图像输入
    instruction = "I need a bottle of ADMilk with a white cap and green lettering."  # 示例文本输入
    # text = clip.tokenize([instruction]).to(device)
    instr=clip.tokenize([instruction])
    # robot_state = torch.tensor([[1.6667, -3.5398, 2.2222, -6.8182, 0.2778, 0.0000, 0.0000, 1.6507, 5.8341, 10.9330, 0.0000]])
    robot_state = torch.tensor([[1.6667, -3.5398, 2.2222]])
    print("img:",img.shape,"instr:",instr.shape,"robot_state:",robot_state.shape)
    print("img:",type(img),"instr:",type(instr),"robot_state:",type(robot_state ))
    # 模型前向传播
    predicted_pose = model(img, instr, robot_state)
    # 打印预测的机器人位姿
    print("Predicted Robot Pose:", predicted_pose)
