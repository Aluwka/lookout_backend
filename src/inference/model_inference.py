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
    """
    Abstract base class for model inference implementations.
    """

    @abstractmethod
    def analyze_video(self, video_url: str) -> ModelSchema:
        """
        Analyze the given video and return the result.
        """
        pass

    @abstractmethod
    def get_result(self, task_id: str) -> ModelSchema:
        """
        Get the analysis result for the given video ID.
        """
        pass



class ModelInferenceImpl(ModelInference):
    """
    Implementation of model inference.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.backbone = self.load_backbone()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
    

    def load_backbone(self):
        weights = EfficientNet_B4_Weights.IMAGENET1K_V1
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
            raise ValueError("⚠️ Не удалось извлечь кадры из видео")

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
            label, prob = result.result
            return ModelSchema(
                status="success",
                result=ModelResultSchema(prediction=label, confidence=prob),
                task_id=task_id
            )
        else:
            return ModelSchema(status="error", result=result.info, task_id=task_id)



model_inference = ModelInferenceImpl(model_path="models/best_model_2.pt")
