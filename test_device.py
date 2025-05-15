import torch

def check_device():
    print("=== PyTorch 环境信息 ===")
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 是否可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"当前 GPU: {torch.cuda.get_device_name(0)}")
    
    print("\n=== 设备分配测试 ===")
    # 测试方法1
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"方法1 - 字符串方式:")
    print(f"设备: {device}")
    
    # 测试方法2
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n方法2 - torch.device方式:")
    print(f"设备: {device}")
    
    # 创建测试张量
    print("\n=== 张量测试 ===")
    x = torch.randn(2, 3)
    print(f"初始张量设备: {x.device}")
    
    if torch.cuda.is_available():
        x = x.cuda()
        print(f"移动到CUDA后的设备: {x.device}")
        
        # 测试CUDA张量运算
        y = torch.randn(2, 3).cuda()
        z = x + y
        print(f"CUDA张量运算结果设备: {z.device}")

if __name__ == "__main__":
    check_device() 