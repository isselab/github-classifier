import torch

if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name()}')
else:
    print('not possible')

print(torch.cuda.is_available())

id = torch.cuda.current_device()
print(id)