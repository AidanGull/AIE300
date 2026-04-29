import torch

# Create tensors
a = torch.tensor([1.0, 2.0, 3.0])
b = torch.randn(3)

print("Tensor a:", a)
print("Tensor b:", b)

# Operations
print("Addition:", a + b)
print("Dot product:", torch.dot(a, b))

# Autograd
x = torch.tensor(3.0, requires_grad=True)
y = x**2 + 2*x + 1
y.backward()

print(f"x = {x.item()}, dy/dx = {x.grad.item()}")