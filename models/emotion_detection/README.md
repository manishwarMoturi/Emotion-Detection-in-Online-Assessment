# Emotion Detection Model

This directory contains the emotion detection model files and configuration.

## Directory Structure
```
models/
└── emotion_detection/
    ├── model.json          # Model architecture
    ├── weights.bin         # Model weights
    ├── metadata.json       # Model metadata
    └── config.json         # Model configuration
```

## Model Files
1. `model.json`: Contains the model architecture
2. `weights.bin`: Contains the trained weights
3. `metadata.json`: Contains model metadata:
   ```json
   {
       "name": "emotion_detection_model",
       "version": "1.0.0",
       "input_shape": [224, 224, 3],
       "output_classes": ["happy", "sad", "angry", "focused", "confused", "frustrated", "neutral"],
       "accuracy": 0.85,
       "created_at": "2024-03-20"
   }
   ```
4. `config.json`: Contains model configuration:
   ```json
   {
       "preprocessing": {
           "resize": [224, 224],
           "normalization": {
               "mean": [0.485, 0.456, 0.406],
               "std": [0.229, 0.224, 0.225]
           }
       },
       "inference": {
           "batch_size": 1,
           "confidence_threshold": 0.5
       }
   }
   ```

## Usage
1. Place your model files in this directory
2. Update the metadata.json with your model's information
3. Update the config.json with your model's configuration
4. Register the model in the database using the following SQL:
   ```sql
   INSERT INTO emotion_models (name, version, model_path, input_shape, output_classes, accuracy)
   VALUES (
       'emotion_detection_model',
       '1.0.0',
       '/models/emotion_detection',
       '224,224,3',
       'happy,sad,angry,focused,confused,frustrated,neutral',
       0.85
   );
   ``` 