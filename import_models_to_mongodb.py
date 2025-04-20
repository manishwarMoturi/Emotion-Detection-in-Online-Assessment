#!/usr/bin/env python
"""
Utility script to import ML models into MongoDB GridFS.
This allows models to be stored in the database and loaded at runtime.
"""

import os
import sys
import django
import argparse
import logging
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emotion_detection.settings')
django.setup()

# Import the ModelStorage class
from emotion_app.model_storage import ModelStorage

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def import_model(model_path, model_name, version, metadata=None):
    """Import a model file into MongoDB GridFS"""
    # Check if model path exists
    model_path = Path(model_path)
    if not model_path.exists():
        logger.error(f"Model file not found: {model_path}")
        return False
        
    # Initialize the model storage
    storage = ModelStorage()
    
    # If metadata is not provided, create empty metadata
    if metadata is None:
        metadata = {}
        
    # Add file information to metadata
    metadata.update({
        "original_filename": model_path.name,
        "size_bytes": model_path.stat().st_size,
        "import_source": "import_script"
    })
    
    # Import the model
    try:
        file_id = storage.save_model(
            str(model_path),
            model_name,
            version=version,
            metadata=metadata
        )
        
        if file_id:
            logger.info(f"Successfully imported model {model_name} version {version} to MongoDB")
            logger.info(f"File ID: {file_id}")
            return True
        else:
            logger.error(f"Failed to import model {model_name}")
            return False
            
    except Exception as e:
        logger.error(f"Error importing model: {str(e)}")
        return False

def import_mediapipe_model(model_bytes, model_name, version, metadata=None):
    """Import a MediaPipe model into MongoDB GridFS"""
    # Initialize the model storage
    storage = ModelStorage()
    
    # If metadata is not provided, create empty metadata
    if metadata is None:
        metadata = {}
        
    # Add information to metadata
    metadata.update({
        "import_source": "import_script",
        "model_type": "mediapipe"
    })
    
    # Import the model
    try:
        file_id = storage.store_mediapipe_model(
            model_bytes,
            model_name,
            version=version
        )
        
        if file_id:
            logger.info(f"Successfully imported MediaPipe model {model_name} version {version} to MongoDB")
            logger.info(f"File ID: {file_id}")
            return True
        else:
            logger.error(f"Failed to import MediaPipe model {model_name}")
            return False
            
    except Exception as e:
        logger.error(f"Error importing MediaPipe model: {str(e)}")
        return False

def list_models():
    """List all models in the MongoDB registry"""
    # Initialize the model storage
    storage = ModelStorage()
    
    # Get all models
    models = storage.get_available_models()
    
    if not models:
        logger.info("No models found in MongoDB registry")
        return
        
    # Display models
    logger.info(f"Found {len(models)} models in MongoDB registry:")
    for model in models:
        active = " (ACTIVE)" if model.get("is_active") else ""
        logger.info(f"  - {model.get('model_name')} (version: {model.get('version')}){active}")

def main():
    """Main function for the import script"""
    parser = argparse.ArgumentParser(description="Import ML models into MongoDB GridFS")
    
    # Define subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import a model file into MongoDB")
    import_parser.add_argument("model_path", help="Path to the model file")
    import_parser.add_argument("model_name", help="Name for the model in MongoDB")
    import_parser.add_argument("--version", default="latest", help="Version string for the model")
    import_parser.add_argument("--active", action="store_true", help="Set as the active model")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all models in the MongoDB registry")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "import":
        # If active flag is set, use "latest" as version
        version = "latest" if args.active else args.version
        
        # Import the model
        success = import_model(args.model_path, args.model_name, version)
        
        # Exit with appropriate status code
        sys.exit(0 if success else 1)
        
    elif args.command == "list":
        # List all models
        list_models()
        sys.exit(0)
        
    else:
        # Display help if no command is specified
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 