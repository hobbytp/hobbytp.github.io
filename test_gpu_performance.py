import torch
import time

def test_matrix_operations(sizes=[1000, 2000, 4000, 8000]):
    print("=== 矩阵运算性能测试 ===")
    print(f"{'矩阵大小':^15} {'CPU时间(秒)':^15} {'GPU时间(秒)':^15} {'加速比':^10}")
    print("-" * 60)
    
    for size in sizes:
        # 创建随机矩阵
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)
        a_gpu = a_cpu.cuda()
        b_gpu = b_cpu.cuda()
        
        # CPU测试
        start_time = time.time()
        c_cpu = torch.matmul(a_cpu, b_cpu)
        cpu_time = time.time() - start_time
        
        # GPU测试
        start_time = time.time()
        c_gpu = torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start_time
        
        # 计算加速比
        speedup = cpu_time / gpu_time
        
        print(f"{size}x{size:^10} {cpu_time:^15.3f} {gpu_time:^15.3f} {speedup:^10.2f}x")

def main():
    print("=== GPU性能测试 ===")
    print(f"GPU设备: {torch.cuda.get_device_name(0)}")
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"PyTorch版本: {torch.__version__}")
    print("\n")
    
    # 运行矩阵运算测试
    test_matrix_operations()

if __name__ == "__main__":
    main() 