
from abc import ABC, abstractmethod
import cv2
import torch
from PIL import Image
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
from torchvision import transforms
from worker.celery_tasks import predict
from celery.result import AsyncResult
from worker.celery_app import app
from src.schemas.model_schema import ModelSchema, ModelResultSchema


class ModelInference(ABC):
    @abstractmethod
    def analyze_video(self, video_url: str) -> ModelSchema:
        pass

    @abstractmethod
    def get_result(self, task_id: str) -> ModelSchema:
        pass


class ModelInferenceImpl(ModelInference):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.backbone = self.load_backbone()
        self.transform = EfficientNet_B4_Weights.DEFAULT.transforms()

    def load_backbone(self):
        weights = EfficientNet_B4_Weights.DEFAULT
        model = efficientnet_b4(weights=weights)
        model.classifier = torch.nn.Identity()
        model.eval()
        return model

    def extract_features_from_video(self, video_url: str, max_frames=60):
        cap = cv2.VideoCapture(video_url)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval = int(fps) if fps > 0 else 1
        frames = []

        idx = 0
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % interval == 0:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img = self.transform(img)
                frames.append(img)
            idx += 1
        cap.release()

        if len(frames) == 0:
            raise ValueError("⚠️ Failed to extract frames from video")

        batch = torch.stack(frames)
        with torch.no_grad():
            features = self.backbone(batch)
        return features.numpy()

    def analyze_video(self, video_url: str) -> ModelSchema:
        features = self.extract_features_from_video(video_url)
        features_list = features.tolist()

        task = predict.delay(self.model_path, features_list)
        return ModelSchema(status="pending", task_id=str(task.id))

    def get_result(self, task_id: str) -> ModelSchema:
        result = AsyncResult(id=task_id, app=app)

        if result.state == 'PENDING':
            return ModelSchema(status="pending", task_id=task_id)
        elif result.state == 'FAILURE':
            return ModelSchema(status="failed", result=str(result.info), task_id=task_id)
        elif result.state == 'STARTED':
            return ModelSchema(status="processing", task_id=task_id)
        elif result.state == 'SUCCESS':
            data = result.result
            return ModelSchema(
                status="success",
                result=ModelResultSchema(
                    prediction=data["verdict"],
                    confidence=data["confidence"],
                    probability=data["model_output_prob"],
                    comment=data["comment"]
                ),
                task_id=task_id
            )
        else:
            return ModelSchema(status="error", result=result.info, task_id=task_id)


model_inference = ModelInferenceImpl(model_path="models/mlp_best_model_2_with_dropout_schedule.pt")
