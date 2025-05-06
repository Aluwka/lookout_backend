# Lookout

Welcome to the **Lookout** project! This repository is designed to analyze video content and detect if a video is real or AI-generated using deep learning.

## Features

- Upload videos for analysis
- Asynchronous video processing via Celery
- Transformer-based AI model (PyTorch)
- Integration with AWS S3
- REST API built with FastAPI

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Aluwka/lookout_backend.git
    ```

2. Navigate to the project directory:
    ```bash
    cd lookout
    ```

3. Copy the example environment file and configure it:
    ```bash
    cp .env.example .env
    # Or just create .env with .env.example fields
    ```

4. Install dependencies:
    ```bash
    poetry install
    # Or
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```bash
uvicorn src.main:app --reload
```


## Architecture

- **FastAPI** — web framework for API  
- **Celery + Redis** — background task processing  
- **PyTorch** — TransformerClassifier model for prediction  
- **AWS S3** — video storage  
- **Docker (optional)** — containerized development & deployment  

## Workflow

1. User uploads a video  
2. Video is stored on AWS S3  
3. A Celery task is triggered to extract features and run prediction  
4. The AI model returns a label (`REAL` or `FAKE`) with probability  
5. Result can be fetched via `task_id`  

## Environment Variables

Configure the following variables in your `.env` file:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET=iloveaminamore


S3_REGION_NAME=region-name
S3_ACCESS_KEY=access-key
S3_SECRET_KEY=secret-key
S3_BUCKET_NAME=bucket-name
```



## Running Celery

In a separate terminal:

```bash
celery -A worker.celery_app worker --loglevel=info
```


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add feature-name"
    ```
4. Push to your branch:
    ```bash
    git push origin feature-name
    ```
5. Open a pull request.

