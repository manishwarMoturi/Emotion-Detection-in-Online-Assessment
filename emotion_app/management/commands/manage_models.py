from django.core.management.base import BaseCommand, CommandError
import os
import logging
from pathlib import Path
from emotion_app.model_storage import ModelStorage

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Manage emotion detection models in MongoDB'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')
        
        # Import model command
        import_parser = subparsers.add_parser('import', help='Import a model into MongoDB')
        import_parser.add_argument('model_path', help='Path to the model file')
        import_parser.add_argument('model_name', help='Name for the model')
        import_parser.add_argument('--version', default='latest', help='Version string for the model')
        import_parser.add_argument('--set-active', action='store_true', help='Set as the active model')
        
        # List models command
        list_parser = subparsers.add_parser('list', help='List all models in MongoDB')
        
        # Set active model command
        active_parser = subparsers.add_parser('set-active', help='Set the active model')
        active_parser.add_argument('model_name', help='Name of the model')
        active_parser.add_argument('--version', default='latest', help='Version string for the model')
        
        # Delete model command
        delete_parser = subparsers.add_parser('delete', help='Delete a model from MongoDB')
        delete_parser.add_argument('model_name', help='Name of the model')
        delete_parser.add_argument('--version', default='latest', help='Version string for the model')
        
        # Import MediaPipe model command
        mediapipe_parser = subparsers.add_parser('import-mediapipe', help='Import a MediaPipe model into MongoDB')
        mediapipe_parser.add_argument('model_path', help='Path to the MediaPipe model file')
        mediapipe_parser.add_argument('model_name', help='Name for the model')
        mediapipe_parser.add_argument('--version', default='latest', help='Version string for the model')

    def handle(self, *args, **options):
        operation = options.get('operation')
        storage = ModelStorage()
        
        if operation == 'import':
            self.import_model(storage, options)
        elif operation == 'list':
            self.list_models(storage)
        elif operation == 'set-active':
            self.set_active_model(storage, options)
        elif operation == 'delete':
            self.delete_model(storage, options)
        elif operation == 'import-mediapipe':
            self.import_mediapipe_model(storage, options)
        else:
            self.print_help('manage.py', 'manage_models')
    
    def import_model(self, storage, options):
        model_path = options.get('model_path')
        model_name = options.get('model_name')
        version = options.get('version')
        set_active = options.get('set_active', False)
        
        # Check if model file exists
        if not os.path.exists(model_path):
            self.stderr.write(self.style.ERROR(f'Model file not found: {model_path}'))
            return
        
        # Collect metadata
        model_path = Path(model_path)
        metadata = {
            'original_filename': model_path.name,
            'size_bytes': model_path.stat().st_size,
            'import_source': 'django_command'
        }
        
        # Import the model
        try:
            file_id = storage.save_model(
                str(model_path),
                model_name,
                version=version,
                metadata=metadata
            )
            
            if file_id:
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported model {model_name} (version: {version})'
                ))
                
                # Set as active if requested
                if set_active:
                    self.set_active_model(storage, {'model_name': model_name, 'version': version})
            else:
                self.stderr.write(self.style.ERROR(
                    f'Failed to import model {model_name}'
                ))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing model: {str(e)}'))
    
    def list_models(self, storage):
        models = storage.get_available_models()
        
        if not models:
            self.stdout.write('No models found in MongoDB')
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(models)} models:'))
        for model in models:
            active = ' (ACTIVE)' if model.get('is_active') else ''
            self.stdout.write(f"  - {model.get('model_name')} (version: {model.get('version')}){active}")
    
    def set_active_model(self, storage, options):
        model_name = options.get('model_name')
        version = options.get('version')
        
        # Set the active model
        try:
            if storage.db is not None:
                storage.db.model_registry.update_many(
                    {'model_name': model_name, 'is_active': True},
                    {'$set': {'is_active': False}}
                )
                
                result = storage.db.model_registry.update_one(
                    {'model_name': model_name, 'version': version},
                    {'$set': {'is_active': True}}
                )
                
                if result.matched_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully set {model_name} (version: {version}) as active'
                    ))
                else:
                    self.stderr.write(self.style.ERROR(
                        f'Model {model_name} (version: {version}) not found'
                    ))
            else:
                self.stderr.write(self.style.ERROR('MongoDB connection not available'))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error setting active model: {str(e)}'))
    
    def delete_model(self, storage, options):
        model_name = options.get('model_name')
        version = options.get('version')
        
        # Delete the model
        try:
            if storage.db is not None and storage.fs is not None:
                # Get the model from registry
                model = storage.db.model_registry.find_one(
                    {'model_name': model_name, 'version': version}
                )
                
                if not model:
                    self.stderr.write(self.style.ERROR(
                        f'Model {model_name} (version: {version}) not found'
                    ))
                    return
                
                # Delete the file from GridFS
                if 'file_id' in model:
                    storage.fs.delete(model['file_id'])
                
                # Delete from registry
                storage.db.model_registry.delete_one(
                    {'model_name': model_name, 'version': version}
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully deleted model {model_name} (version: {version})'
                ))
            else:
                self.stderr.write(self.style.ERROR('MongoDB connection not available'))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error deleting model: {str(e)}'))
    
    def import_mediapipe_model(self, storage, options):
        model_path = options.get('model_path')
        model_name = options.get('model_name')
        version = options.get('version')
        
        # Check if model file exists
        if not os.path.exists(model_path):
            self.stderr.write(self.style.ERROR(f'MediaPipe model file not found: {model_path}'))
            return
        
        # Read the model file
        try:
            with open(model_path, 'rb') as f:
                model_data = f.read()
            
            # Import the model
            file_id = storage.store_mediapipe_model(
                model_data,
                model_name,
                version=version
            )
            
            if file_id:
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported MediaPipe model {model_name} (version: {version})'
                ))
            else:
                self.stderr.write(self.style.ERROR(
                    f'Failed to import MediaPipe model {model_name}'
                ))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing MediaPipe model: {str(e)}')) 