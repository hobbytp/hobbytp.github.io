import torch

print("PyTorch版本:", torch.__version__)
print("CUDA是否可用:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA版本:", torch.version.cuda)
    print("当前GPU设备:", torch.cuda.get_device_name(0))
    print("GPU数量:", torch.cuda.device_count())
else:
    print("CUDA不可用，请检查以下可能的原因：")
    print("1. 是否安装了支持CUDA的PyTorch版本")
    print("2. 是否安装了NVIDIA驱动程序")
    print("3. 是否安装了CUDA工具包")
    print("4. 系统是否识别到NVIDIA GPU") 