import torch
import time

def test_gpu():
    # 检查CUDA是否可用
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print("CUDA不可用，无法进行GPU测试")
        return

    # 获取GPU信息
    print(f"GPU设备: {torch.cuda.get_device_name(0)}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    
    # 创建两个大矩阵
    size = 5000
    print(f"\n创建两个 {size}x{size} 的矩阵...")
    
    # 在CPU上创建矩阵
    a_cpu = torch.randn(size, size)
    b_cpu = torch.randn(size, size)
    
    # 在GPU上创建矩阵
    a_gpu = a_cpu.cuda()
    b_gpu = b_cpu.cuda()
    
    # 测试CPU计算
    print("\n在CPU上进行矩阵乘法...")
    start_time = time.time()
    c_cpu = torch.matmul(a_cpu, b_cpu)
    cpu_time = time.time() - start_time
    print(f"CPU计算时间: {cpu_time:.2f} 秒")
    
    # 测试GPU计算
    print("\n在GPU上进行矩阵乘法...")
    start_time = time.time()
    c_gpu = torch.matmul(a_gpu, b_gpu)
    # 确保GPU计算完成
    torch.cuda.synchronize()
    gpu_time = time.time() - start_time
    print(f"GPU计算时间: {gpu_time:.2f} 秒")
    
    # 计算加速比
    speedup = cpu_time / gpu_time
    print(f"\nGPU加速比: {speedup:.2f}x")
    
    # 验证结果
    print("\n验证计算结果...")
    c_gpu_cpu = c_gpu.cpu()
    
    # 使用更严格的精度控制
    max_diff = torch.max(torch.abs(c_cpu - c_gpu_cpu))
    mean_diff = torch.mean(torch.abs(c_cpu - c_gpu_cpu))
    print(f"最大差异: {max_diff:.2e}")
    print(f"平均差异: {mean_diff:.2e}")
    
    # 使用更宽松的精度控制进行验证
    is_close = torch.allclose(c_cpu, c_gpu_cpu, rtol=1e-3, atol=1e-3)
    print(f"计算结果是否在可接受范围内: {is_close}")

if __name__ == "__main__":
    test_gpu() 