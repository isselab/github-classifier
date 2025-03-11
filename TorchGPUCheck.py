import torch
"""
This code is a simple Python script that checks if CUDA is available on the system and provides instructions on how to enable it if it's not available.
"""

if __name__ == "__main__":
    print(torch.torch_version)
    # Check if CUDA is available
    if torch.cuda.is_available():
        print("CUDA is available!")
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        print(f"Current GPU: {torch.cuda.get_device_name(torch.cuda.current_device())}")
    else:
        print("CUDA is not available.")
        print("To enable CUDA, follow these steps:")
        print("1. **Install NVIDIA Drivers**: Ensure you have the latest NVIDIA drivers installed on your system.")
        print("2. **Install CUDA Toolkit**: Download and install the CUDA Toolkit from the official NVIDIA website: https://developer.nvidia.com/cuda-downloads")
        print("3. **Verify CUDA Installation**: After installation, verify that CUDA is working correctly by running the `nvidia-smi` command in your terminal/command prompt.")
        print("4. **Update PyTorch**: Make sure you're using the latest version of PyTorch. You can update PyTorch using pip: `pip install --upgrade torch`")
        print("5. **Restart Your System**: Restart your system to ensure that the changes take effect.")