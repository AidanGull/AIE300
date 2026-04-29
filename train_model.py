import torch
import torch.nn as nn
import torch.optim as optim

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


# -----------------------
# Load dataset
# -----------------------
data = load_iris()
X = data.data
y = data.target

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Convert to tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)

X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.long)


# -----------------------
# DataLoader (batching)
# -----------------------
train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)


# -----------------------
# Model definition
# -----------------------
class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(4, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, 3)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)


model = SimpleClassifier()


# -----------------------
# Training setup
# -----------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)


# -----------------------
# Training loop
# -----------------------
epochs = 50

for epoch in range(epochs):
    for xb, yb in train_loader:
        optimizer.zero_grad()
        outputs = model(xb)
        loss = criterion(outputs, yb)
        loss.backward()
        optimizer.step()

    # Print every 10 epochs
    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")


# -----------------------
# Save model
# -----------------------
torch.save(model.state_dict(), "model.pth")
print("Model saved as model.pth")


# -----------------------
# Evaluate accuracy
# -----------------------
model.eval()

with torch.no_grad():
    outputs = model(X_test)
    predictions = torch.argmax(outputs, dim=1)
    accuracy = (predictions == y_test).float().mean()

print(f"Test Accuracy: {accuracy.item():.4f}")