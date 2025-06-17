import numpy as np
import torch
import torch.nn as nn
from .celery_app import app


class MLPClassifier(nn.Module):
    def __init__(self, input_dim=1792):
        super(MLPClassifier, self).__init__()
        self.dropout1 = nn.Dropout(0.5)
        self.dropout2 = nn.Dropout(0.3)
        self.dropout3 = nn.Dropout(0.1)

        self.model = nn.Sequential(
            nn.Linear(input_dim, 1024),
            nn.ReLU(),
            nn.BatchNorm1d(1024),
            self.dropout1,
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            self.dropout2,
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            self.dropout3,
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.model(x)


def load_model(model_path: str):
    model = MLPClassifier()
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model


@app.task
def predict(model_path: str, features: list):
    with torch.no_grad():
        features = np.array(features)
        if features.ndim != 2 or features.shape[1] != 1792:
            raise ValueError("Invalid feature shape. Expected [N, 1792]")

        mean_feature = torch.tensor(features.mean(axis=0), dtype=torch.float32).unsqueeze(0)
        model = load_model(model_path)
        output = model(mean_feature)
        prob = torch.sigmoid(output).item()

        verdict = "FAKE" if prob > 0.5 else "REAL"
        confidence = round((prob if verdict == "FAKE" else 1 - prob) * 100, 2)

        if 0.4 < prob < 0.6:
            comment = "⚠️ The model is uncertain about the result. We recommend further verification for greater confidence."
        elif verdict == "REAL":
            comment = "✅ Based on the analysis, the model considers this video to be authentic with high confidence."
        else:
            comment = "🚩 Based on the analysis, the model considers this video to be manipulated with high confidence."

        return {
            "verdict": verdict,
            "confidence": confidence,
            "model_output_prob": f"{prob:.4f}",
            "comment": comment
        }
