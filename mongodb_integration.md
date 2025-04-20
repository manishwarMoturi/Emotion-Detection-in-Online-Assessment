# MongoDB Integration for Emotion Detection

This document explains how to set up and use the MongoDB integration for storing and loading emotion detection models.

## Setup

### 1. Install MongoDB

If you haven't already, install MongoDB on your system or use a cloud MongoDB service.

- [MongoDB Installation Instructions](https://docs.mongodb.com/manual/installation/)
- [MongoDB Atlas Cloud Service](https://www.mongodb.com/cloud/atlas)

### 2. Configure Connection

Update the MongoDB connection settings in `emotion_detection/settings.py`:

```python
# MongoDB connection for the application
MONGODB_URI = 'mongodb://username:password@hostname:port/database_name'

# MongoDB settings for emotion models
MONGODB_MODELS = {
    'URI': MONGODB_URI,
    'DB_NAME': 'emotion_detection_db',
    'COLLECTIONS': {
        'MODEL_REGISTRY': 'model_registry',
        'EMOTION_LOGS': 'emotion_logs'
    },
    'DEFAULT_MODEL': 'emotion_model',
    'DEFAULT_MODEL_VERSION': 'latest'
}
```

For local development without authentication, you can use:

```python
MONGODB_URI = 'mongodb://localhost:27017/emotion_detection_db'
```

## Importing Models

You can import models into MongoDB using the provided Django management command:

```bash
# Import a model and set it as active
python manage.py manage_models import /path/to/model.h5 emotion_model --set-active

# Import a model with a specific version
python manage.py manage_models import /path/to/model.h5 emotion_model --version v1

# List all models in MongoDB
python manage.py manage_models list

# Set an existing model as active
python manage.py manage_models set-active emotion_model --version v1

# Delete a model
python manage.py manage_models delete emotion_model --version v1

# Import a MediaPipe model
python manage.py manage_models import-mediapipe /path/to/mediapipe_model.blob mediapipe_face_detection
```

Alternatively, you can use the provided script:

```bash
# Import a model
python import_models_to_mongodb.py import /path/to/model.h5 emotion_model

# List all models
python import_models_to_mongodb.py list
```

## Usage in Code

The integration is automatically used by the `EmotionDetector` class. When initialized, it will:

1. Try to load models from MongoDB first
2. Fall back to local files if MongoDB is not available or models aren't found
3. Store local models to MongoDB for future use if they're found and valid

If you want to manually use the model storage, you can do so:

```python
from emotion_app.model_storage import ModelStorage

# Initialize the storage
storage = ModelStorage()

# Load a model by name
model = storage.load_model("emotion_model")

# Save a model
storage.save_model("/path/to/model.h5", "emotion_model", version="v2", metadata={"accuracy": 0.92})

# Get available models
models = storage.get_available_models()
```

## Advantages

Using MongoDB for model storage offers several advantages:

1. **Centralized storage**: Store models in a central location accessible by multiple instances
2. **Version control**: Keep multiple versions of models and track their performance
3. **Dynamic loading**: Update models without redeploying the application
4. **Metadata**: Store additional information about models (accuracy, training data, etc.)
5. **Model switching**: Easily switch between different models

## Implementation Details

The implementation consists of the following components:

1. **ModelStorage class** (`emotion_app/model_storage.py`): The core class for interacting with MongoDB GridFS
2. **EmotionDetector** (`emotion_app/emotion_detection.py`): Uses the ModelStorage to load models
3. **Django management command** (`emotion_app/management/commands/manage_models.py`): For managing models via CLI
4. **Import script** (`import_models_to_mongodb.py`): Standalone script for importing models

Models are stored using GridFS, which allows for storing files larger than 16MB in MongoDB. Each model is also registered in a metadata collection for easier retrieval and management.

## Troubleshooting

### Connection Issues

If you're having trouble connecting to MongoDB, check:

1. MongoDB is running and accessible
2. The connection string is correct
3. Authentication credentials are correct
4. Network/firewall settings allow the connection

### Model Loading Issues

If models aren't loading correctly:

1. Check the logs for detailed error messages
2. Try listing available models with the management command
3. Verify the model exists in MongoDB with the correct name and version
4. Ensure the model file is in a compatible format (H5 or SavedModel) 