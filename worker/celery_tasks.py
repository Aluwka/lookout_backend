import os
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from .celery_app import app


class MLPClassifier(torch.nn.Module):
    def __init__(self, input_dim=1792):
        super().__init__()
        self.dropout1 = torch.nn.Dropout(0.5)
        self.dropout2 = torch.nn.Dropout(0.3)
        self.dropout3 = torch.nn.Dropout(0.1)

        self.model = torch.nn.Sequential(
            torch.nn.Linear(input_dim, 1024),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(1024),
            self.dropout1,
            torch.nn.Linear(1024, 512),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(512),
            self.dropout2,
            torch.nn.Linear(512, 128),
            torch.nn.ReLU(),
            torch.nn.BatchNorm1d(128),
            self.dropout3,
            torch.nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.model(x)


def load_model(model_path):
    model = MLPClassifier()
    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model


def save_frame_heatmap(probs, path):
    data = np.array(probs).reshape(1, -1)
    plt.figure(figsize=(12, 1.5))
    sns.heatmap(data, cmap="RdYlGn_r", cbar=True, xticklabels=False, yticklabels=False, vmin=0, vmax=1)
    plt.title("Frame-wise Real/Fake Heatmap")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def save_extreme(frames, probs, path):
    max_idx = int(np.argmax(probs))
    min_idx = int(np.argmin(probs))
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(frames[max_idx])
    axes[0].axis("off")
    axes[0].set_title(f"Most FAKE ({probs[max_idx]*100:.1f}%)")
    axes[1].imshow(frames[min_idx])
    axes[1].axis("off")
    axes[1].set_title(f"Most REAL ({(1 - probs[min_idx])*100:.1f}%)")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def save_gallery(frames, path):
    selected = frames[::10]
    fig, axes = plt.subplots(1, len(selected), figsize=(len(selected)*2, 3))
    if len(selected) == 1:
        axes = [axes]
    for i, ax in enumerate(axes):
        ax.imshow(selected[i])
        ax.axis("off")
        ax.set_title(f"F{i*10}", fontsize=6)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


@app.task
def predict(model_path: str, features: list, video_path: str, video_id: str):
    model = load_model(model_path)

    # Предсказание по среднему признаку
    features_np = np.array(features)
    mean_feature = torch.tensor(features_np.mean(axis=0), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        output = model(mean_feature)
        prob = torch.sigmoid(output).item()

    verdict = "FAKE" if prob > 0.5 else "REAL"
    confidence = round((prob if verdict == "FAKE" else 1 - prob) * 100, 2)

    if 0.4 < prob < 0.6:
        comment = "⚠️ The model is uncertain about the result. We recommend further verification."
    elif verdict == "REAL":
        comment = "✅ This video appears authentic with high confidence."
    else:
        comment = "🚩 This video appears manipulated with high confidence."

    # Загрузка кадров из видео (для визуализации)
    cap = cv2.VideoCapture(video_path)
    frames = []
    while len(frames) < len(features):
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)
    cap.release()

    # Получение по-кадровых вероятностей
    probs = []
    with torch.no_grad():
        for feat in features_np:
            f_tensor = torch.tensor(feat, dtype=torch.float32).unsqueeze(0)
            pred = model(f_tensor)
            probs.append(torch.sigmoid(pred).item())

  
    # Генерация PNG файлов (в папку src/static/images)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    images_dir = os.path.join(project_root, "src", "static", "images")
    os.makedirs(images_dir, exist_ok=True)

    heatmap_path = os.path.join(images_dir, f"heatmap_{video_id}.png")
    extreme_path = os.path.join(images_dir, f"extreme_{video_id}.png")
    gallery_path = os.path.join(images_dir, f"every10_{video_id}.png")


    save_frame_heatmap(probs, heatmap_path)
    save_extreme(frames, probs, extreme_path)
    save_gallery(frames, gallery_path)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "model_output_prob": f"{prob:.4f}",
        "comment": comment,
        "heatmap_path": f"/static/images/heatmap_{video_id}.png",
        "extreme_path": f"/static/images/extreme_{video_id}.png",
        "gallery_path": f"/static/images/every10_{video_id}.png"
    }
