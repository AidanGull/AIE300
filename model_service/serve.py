from fastapi import FastAPI
from pydantic import BaseModel

import torch
import torch.nn as nn

app = FastAPI()


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

model.load_state_dict(
    torch.load(
        "model/model.pth",
        map_location=torch.device("cpu")
    )
)

model.eval()

labels = [
    "setosa",
    "versicolor",
    "virginica"
]


class PredictionRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True
    }


@app.post("/predict")
def predict(req: PredictionRequest):

    x = torch.tensor(
        [req.features],
        dtype=torch.float32
    )

    with torch.no_grad():

        outputs = model(x)

        probs = torch.softmax(outputs, dim=1)

        pred = torch.argmax(probs, dim=1).item()

        confidence = probs[0][pred].item()

    return {
        "prediction": labels[pred],
        "confidence": round(confidence, 3),
        "model": "iris-classifier-v1"
    }
