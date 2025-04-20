import mediapipe as mp
import numpy as np
import cv2
import base64
import logging
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import shutil
from pathlib import Path
import urllib.request
import gdown
import requests
from io import BytesIO
import re
from .model_storage import ModelStorage
import traceback
import math

# Setup logging
logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self, test_mode=False):
        # Enable test mode for cartoon face testing
        self.test_mode = test_mode
        
        # Initialize model storage service for MongoDB integration
        self.model_storage = ModelStorage()
        
        # Initialize MediaPipe FaceMesh for reliable face detection and landmarks
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
            
        # Initialize MediaPipe Face Detection (more optimized than face mesh for detection only)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 for short-range, 1 for full-range detection
            min_detection_confidence=0.5)
            
        # MediaPipe face mesh landmark indices for various facial features
        self.LANDMARK_INDICES = {
            'left_eyebrow': [70, 63, 105, 66, 107],  # left eyebrow outline
            'right_eyebrow': [336, 296, 334, 293, 300],  # right eyebrow outline
            'left_eye': [362, 385, 387, 263, 373, 380],  # left eye outline
            'right_eye': [33, 160, 158, 133, 153, 144],  # right eye outline
            'mouth_outer': [61, 291, 0, 17, 14, 13, 16, 15, 92, 268],  # outer lips
            'mouth_inner': [78, 308, 13, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178],  # inner lips
            'nose': [168, 6, 195, 4, 19, 94, 2],  # nose outline
            'face_outline': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152]  # face outline
        }
        
        # Define emotion labels
        self.emotion_labels = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']
        
        # Skip ML model loading - use MediaPipe exclusively
        self.use_model = False
        self.model = None
        print("Using MediaPipe for emotion detection - model not needed")
    
    def detect_emotion(self, image_data):
        """
        Detect emotion from image data using MediaPipe face landmarks.
        
        Args:
            image_data: numpy array of image data
            
        Returns:
            dict: Dictionary containing emotion probabilities and dominant emotion
        """
        try:
            # Ensure image is in RGB format (MediaPipe requires RGB)
            if len(image_data.shape) == 2:  # Grayscale
                image_data = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)
            elif image_data.shape[2] == 4:  # RGBA
                image_data = cv2.cvtColor(image_data, cv2.COLOR_RGBA2RGB)
            elif image_data.shape[2] == 3 and image_data.dtype == np.uint8:
                # Check if the image is in BGR format (OpenCV default)
                if np.mean(image_data[:,:,0]) < np.mean(image_data[:,:,2]):
                    image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            
            h, w = image_data.shape[:2]
            
            # Process the image with MediaPipe face mesh
            results = self.face_mesh.process(image_data)
            
            # Default response if no face detected
            default_response = {
                'emotion': 'unknown',
                'emotions': {emotion: 0.0 for emotion in self.emotion_labels},
                'face_detected': False
            }
            
            # If no face mesh landmarks detected, try face detection first
            if not results.multi_face_landmarks:
                logger.info("No face mesh landmarks detected, trying face detection")
                # Perform face detection to get bounding box
                detection_results = self.face_detection.process(image_data)
                
                if not detection_results.detections:
                    logger.info("No face detected in the image")
                    return default_response
                
                # If face detected but no landmarks, return neutral with low confidence
                logger.info("Face detected but no landmarks, assuming neutral with low confidence")
                emotions = {emotion: 0.0 for emotion in self.emotion_labels}
                emotions['neutral'] = 0.55
                return {
                    'emotion': 'neutral',
                    'emotions': emotions,
                    'face_detected': True
                }
            
            # Face landmarks detected
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract landmark coordinates
            landmarks = []
            for landmark in face_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x * w,
                    'y': landmark.y * h,
                    'z': landmark.z
                })
            
            # Perform landmark-based emotion classification
            emotion_probs = self._heuristic_classification(landmarks, image_data)
            
            # Get the emotion with highest probability
            dominant_emotion = max(emotion_probs, key=emotion_probs.get)
            
            # Enhanced classification to adjust the probabilities
            emotion_probs = self._enhanced_classification(landmarks, image_data)
            
            # Re-determine dominant emotion after enhancements
            dominant_emotion = max(emotion_probs, key=emotion_probs.get)
            
            return {
                'emotion': dominant_emotion,
                'emotions': emotion_probs,
                'face_detected': True
            }
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            logger.error(traceback.format_exc())
            return {
                'emotion': 'error',
                'emotions': {emotion: 0.0 for emotion in self.emotion_labels},
                'error': str(e),
                'face_detected': False
            }
    
    def _simple_classification(self, face_roi):
        """Simple classification when landmarks are not available"""
        if face_roi is None or face_roi.size == 0:
            return {"emotion": "unknown", "confidence": 0.0, "error": "Invalid face ROI"}
            
        # Convert to grayscale
        face_gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
        
        # Calculate image statistics
        brightness = np.mean(face_gray)
        contrast = np.std(face_gray)
        
        # Edge detection
        edges = cv2.Canny(face_gray, 100, 200)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Simple heuristics for emotion
        if edge_density > 0.2:
            # High edge density could be surprise
            return {"emotion": "surprised", "confidence": 0.6, "method": "simple_heuristic"}
        elif brightness > 150 and contrast < 50:
            # Bright with low contrast might be happy
            return {"emotion": "happy", "confidence": 0.5, "method": "simple_heuristic"}
        elif brightness < 100 and contrast < 40:
            # Dark with low contrast might be sad
            return {"emotion": "sad", "confidence": 0.5, "method": "simple_heuristic"}
        else:
            # Default to neutral
            return {"emotion": "neutral", "confidence": 0.5, "method": "simple_heuristic"}
    
    def preprocess_image(self, image_data):
        """Convert base64 image to OpenCV format"""
        try:
            # Handle data URLs
            if isinstance(image_data, str) and 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
                
            # Decode base64 data
            image_bytes = base64.b64decode(image_data)
            np_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            
            # Convert to RGB (MediaPipe uses RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image_rgb, image.shape
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise ValueError(f"Invalid image data: {str(e)}")
    
    def _detect_face_landmarks(self, image):
        """
        Detect facial landmarks using MediaPipe Face Mesh.
        
        Args:
            image: RGB image 
            
        Returns:
            list: Facial landmarks if a face is detected, None otherwise
        """
        try:
            # Process the image with MediaPipe face mesh
            with self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5) as face_mesh:
                
                results = face_mesh.process(image)
                
                if not results.multi_face_landmarks:
                    return None
                
                # Get the first face detected
                face_landmarks = results.multi_face_landmarks[0]
                
                # Convert to a list of (x, y) tuples
                landmarks = []
                for landmark in face_landmarks.landmark:
                    landmarks.append((landmark.x, landmark.y))
                
                return landmarks
                
        except Exception as e:
            logger.error(f"Error detecting face landmarks: {str(e)}")
            return None
            
    def _calculate_movement_features(self, current_landmarks, previous_landmarks):
        """
        Calculate emotion indicators based on facial movement between frames.
        
        Args:
            current_landmarks: Current frame landmarks
            previous_landmarks: Previous frame landmarks
            
        Returns:
            dict: Movement-based emotion scores
        """
        try:
            movement_scores = {
                'surprise': 0.0,
                'happy': 0.0,
                'angry': 0.0
            }
            
            # Calculate overall movement (can indicate surprise)
            total_movement = 0
            for i in range(len(current_landmarks)):
                if i in current_landmarks and i in previous_landmarks:
                    dx = current_landmarks[i]['x'] - previous_landmarks[i]['x']
                    dy = current_landmarks[i]['y'] - previous_landmarks[i]['y']
                    total_movement += (dx**2 + dy**2)**0.5
            
            avg_movement = total_movement / len(current_landmarks)
            
            # Sudden movements can indicate surprise
            if avg_movement > 0.01:  # Threshold for significant movement
                movement_scores['surprise'] += min(1.0, avg_movement * 10)
            
            # Check for rapid eyebrow movement
            eyebrow_indices = self.LANDMARK_INDICES['left_eyebrow'] + self.LANDMARK_INDICES['right_eyebrow']
            eyebrow_movement = 0
            for i in eyebrow_indices:
                if i in current_landmarks and i in previous_landmarks:
                    dy = current_landmarks[i]['y'] - previous_landmarks[i]['y']
                    eyebrow_movement += abs(dy)
            
            avg_eyebrow_movement = eyebrow_movement / len(eyebrow_indices)
            
            # Eyebrow movement can indicate surprise or anger
            if avg_eyebrow_movement > 0.005:
                # Determine if moving up (surprise) or down (anger)
                up_movement = 0
                down_movement = 0
                for i in eyebrow_indices:
                    if i in current_landmarks and i in previous_landmarks:
                        dy = current_landmarks[i]['y'] - previous_landmarks[i]['y']
                        if dy < 0:  # Moving up
                            up_movement += abs(dy)
                        else:  # Moving down
                            down_movement += dy
                
                if up_movement > down_movement:
                    movement_scores['surprise'] += min(1.0, up_movement * 20)
                else:
                    movement_scores['angry'] += min(1.0, down_movement * 20)
            
            # Check for mouth movement (smiling)
            mouth_indices = self.LANDMARK_INDICES['mouth_outer']
            left_corner_idx = mouth_indices[0]
            right_corner_idx = mouth_indices[1]
            
            if left_corner_idx in current_landmarks and left_corner_idx in previous_landmarks and \
               right_corner_idx in current_landmarks and right_corner_idx in previous_landmarks:
                # Check if corners are moving up (smiling)
                left_dy = previous_landmarks[left_corner_idx]['y'] - current_landmarks[left_corner_idx]['y']
                right_dy = previous_landmarks[right_corner_idx]['y'] - current_landmarks[right_corner_idx]['y']
                
                if left_dy > 0 and right_dy > 0:  # Both corners moving up
                    smile_movement = (left_dy + right_dy) / 2
                    movement_scores['happy'] += min(1.0, smile_movement * 25)
            
            return movement_scores
            
        except Exception as e:
            logger.error(f"Error calculating movement features: {str(e)}")
            return {}
    
    def _apply_temporal_smoothing(self, current_scores):
        """Apply temporal smoothing to emotion scores based on history"""
        try:
            # Initialize with current scores
            smoothed_scores = current_scores.copy()
            
            # Weights for temporal smoothing (current frame has highest weight)
            weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # Older to newer
            
            # Ensure we have the right number of weights
            if len(self.emotion_history) < len(weights):
                weights = weights[-(len(self.emotion_history)):]
                weights.append(0.3)  # Current frame weight
                
                # Normalize weights to sum to 1
                total_weight = sum(weights)
                weights = [w/total_weight for w in weights]
            
            # Apply weighted average
            for emotion in smoothed_scores:
                weighted_score = weights[-1] * current_scores[emotion]  # Current frame
                
                # Add historical scores with weights
                for i, history_item in enumerate(self.emotion_history):
                    if i < len(weights) - 1:  # Use appropriate weight
                        if emotion in history_item:
                            weighted_score += weights[i] * history_item[emotion]
                
                smoothed_scores[emotion] = weighted_score
            
            return smoothed_scores
                
        except Exception as e:
            logger.error(f"Error applying temporal smoothing: {str(e)}")
            return current_scores
    
    def _heuristic_classification(self, landmarks, image=None):
        """
        Detect emotions using geometric heuristics from facial landmarks.
        
        Args:
            landmarks: List of (x, y) landmark coordinates
            image: Original image (optional)
            
        Returns:
            tuple: (emotion_scores, confidence, metrics)
        """
        if landmarks is None or len(landmarks) < 468:  # MediaPipe face mesh has 468 landmarks
            return {emotion: 0.0 for emotion in self.emotion_labels}, 0.0, {}
            
        try:
            # Initialize scores for each emotion
            scores = {emotion: 0.0 for emotion in self.emotion_labels}
            
            # Define landmark indices for facial features
            # Eyes
            left_eye = [33, 133, 157, 158, 159, 160, 161, 173, 246]  # Left eye landmarks
            right_eye = [362, 263, 386, 387, 388, 389, 390, 398, 466]  # Right eye landmarks
            
            # Eyebrows
            left_eyebrow = [65, 66, 67, 68, 69, 70, 71]
            right_eyebrow = [295, 296, 297, 298, 299, 300, 301]
            
            # Mouth
            mouth_outline = [0, 11, 12, 13, 14, 15, 16, 17, 37, 39, 40, 61, 
                            146, 146, 91, 181, 84, 270, 294, 295, 296, 307, 321, 375]
            lips = [78, 80, 81, 82, 84, 87, 88, 91, 95, 178, 191, 308, 310, 311, 312, 
                   314, 317, 318, 321, 324]
            
            # Calculate metrics
            metrics = {}
            
            # Eye opening (for surprise, fear)
            left_eye_top = sum(landmarks[i][1] for i in [159, 160, 161]) / 3
            left_eye_bottom = sum(landmarks[i][1] for i in [145, 144, 163]) / 3
            right_eye_top = sum(landmarks[i][1] for i in [386, 387, 388]) / 3
            right_eye_bottom = sum(landmarks[i][1] for i in [374, 373, 390]) / 3
            
            eye_height = ((left_eye_top - left_eye_bottom) + (right_eye_top - right_eye_bottom)) / 2
            metrics['eye_openness'] = eye_height
            
            # Eyebrow position (for anger, surprise)
            left_eyebrow_y = sum(landmarks[i][1] for i in left_eyebrow) / len(left_eyebrow)
            right_eyebrow_y = sum(landmarks[i][1] for i in right_eyebrow) / len(right_eyebrow)
            eyebrow_position = (left_eyebrow_y + right_eyebrow_y) / 2
            metrics['eyebrow_position'] = eyebrow_position
            
            # Mouth shape (for happiness, sadness)
            mouth_width = abs(landmarks[61][0] - landmarks[291][0])
            mouth_height = abs(landmarks[17][1] - landmarks[0][1])
            mouth_ratio = mouth_width / mouth_height if mouth_height > 0 else 0
            metrics['mouth_ratio'] = mouth_ratio
            
            # Mouth corners (for happiness vs sadness)
            left_corner = landmarks[61]
            right_corner = landmarks[291]
            center_lips_top = landmarks[13]
            
            left_corner_angle = math.atan2(left_corner[1] - center_lips_top[1], 
                                           left_corner[0] - center_lips_top[0])
            right_corner_angle = math.atan2(right_corner[1] - center_lips_top[1], 
                                            right_corner[0] - center_lips_top[0])
            
            # Convert to degrees
            left_corner_angle = math.degrees(left_corner_angle)
            right_corner_angle = math.degrees(right_corner_angle)
            
            metrics['left_corner_angle'] = left_corner_angle
            metrics['right_corner_angle'] = right_corner_angle
            
            # Detect emotions based on facial metrics
            
            # Happy: Wider mouth, corners up
            if mouth_ratio > 4.0 and left_corner_angle < -5 and right_corner_angle > 5:
                scores['happy'] = 0.8
            elif mouth_ratio > 3.0 and left_corner_angle < 0 and right_corner_angle > 0:
                scores['happy'] = 0.5
                
            # Sad: Downturned mouth corners
            if left_corner_angle > 0 and right_corner_angle < 0:
                scores['sad'] = 0.7
                
            # Angry: Lowered brows
            if eyebrow_position < 0.2:
                scores['angry'] = 0.7
                
            # Surprised: Raised eyebrows, wide eyes
            if eyebrow_position > 0.4 and eye_height > 0.15:
                scores['surprised'] = 0.8
                
            # Fear: Wide eyes, slightly open mouth
            if eye_height > 0.12 and mouth_ratio > 2.0 and mouth_ratio < 4.0:
                scores['fearful'] = 0.6
                
            # Disgust: Wrinkled nose, slightly raised upper lip
            nose_wrinkle = abs(landmarks[5][1] - landmarks[4][1])
            if nose_wrinkle > 0.05:
                scores['disgusted'] = 0.6
            
            # Default to neutral if no strong emotions detected
            if max(scores.values()) < 0.3:
                scores['neutral'] = 0.7
            else:
                # Add some neutral component
                scores['neutral'] = 0.2
                
            # Normalize scores
            total = sum(scores.values())
            if total > 0:
                for emotion in scores:
                    scores[emotion] /= total
                    
            dominant_emotion = max(scores, key=scores.get)
            confidence = scores[dominant_emotion]
            
            return scores, confidence, metrics
            
        except Exception as e:
            logger.error(f"Error in heuristic classification: {str(e)}")
            default_scores = {emotion: 0.0 for emotion in self.emotion_labels}
            default_scores['neutral'] = 1.0
            return default_scores, 0.5, {}
    
    def _distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return ((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)**0.5
        
    def _calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points in degrees"""
        import math
        
        # Create vectors
        vector1 = (p1['x'] - p2['x'], p1['y'] - p2['y'])
        vector2 = (p3['x'] - p2['x'], p3['y'] - p2['y'])
        
        # Calculate dot product
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        
        # Calculate magnitudes
        mag1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
        mag2 = math.sqrt(vector2[0]**2 + vector2[1]**2)
        
        # Calculate angle in radians and convert to degrees
        angle_rad = math.acos(max(-1.0, min(1.0, dot_product / (mag1 * mag2))))
        angle_deg = angle_rad * 180 / math.pi
        
        return angle_deg

    def process(self, frame):
        """
        Process a frame and detect emotions
        
        Args:
            frame: Frame to process
            
        Returns:
            dict: Results with emotions and metrics
        """
        try:
            if frame is None or frame.size == 0:
                raise ValueError("Invalid frame: empty or None")
            
            # Make a copy of the frame to avoid modifying the original
            image_data = frame.copy()
            
            # Convert to RGB (MediaPipe uses RGB)
            image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            
            # Detect face landmarks using MediaPipe
            face_landmarks = self._detect_face_landmarks(image_rgb)
            
            if not face_landmarks:
                logger.warning("No face detected in frame")
                return {
                    "success": False,
                    "error": "No face detected",
                    "emotions": {emotion: 0.0 for emotion in self.emotion_labels},
                    "dominant_emotion": "neutral",
                    "confidence": 0.0,
                    "metrics": {},
                    "debug_info": {"error": "No face detected"}
                }
            
            # Get emotion probabilities using heuristic approach with landmarks
            emotion_probs, dominant_emotion, confidence = self._heuristic_classification(face_landmarks, image_rgb)
            
            # Create metrics dictionary for debugging
            metrics = {}
            
            # Create response
            result = {
                "success": True,
                "emotions": emotion_probs,
                "dominant_emotion": dominant_emotion,
                "confidence": confidence,
                "metrics": metrics,
                "debug_info": {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "emotions": {emotion: 0.0 for emotion in self.emotion_labels},
                "dominant_emotion": "neutral",
                "confidence": 0.0,
                "metrics": {},
                "debug_info": {"error": str(e)}
            }

    def _enhanced_classification(self, landmarks, image=None):
        """
        Enhanced emotion classification using facial landmarks with advanced heuristics.
        This improves upon basic heuristic classification by adding temporal smoothing
        and confidence adjustments.
        
        Args:
            landmarks: List of facial landmarks
            image: Original image (optional)
            
        Returns:
            dict: Dictionary of emotion scores
        """
        try:
            # First get basic heuristic classification
            emotion_scores, confidence, metrics = self._heuristic_classification(landmarks, image)
            
            # Store history for temporal smoothing if not initialized
            if not hasattr(self, 'emotion_history'):
                self.emotion_history = []
            
            # Keep emotion history for temporal smoothing (max 5 frames)
            self.emotion_history.append(emotion_scores)
            if len(self.emotion_history) > 5:
                self.emotion_history.pop(0)
                
            # Apply temporal smoothing to prevent rapid emotion changes
            emotion_scores = self._apply_temporal_smoothing(emotion_scores)
            
            # Apply confidence adjustment - increase confidence of dominant emotion
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            max_score = emotion_scores[dominant_emotion]
            
            # If confidence is high, increase it further (winner takes more)
            if max_score > 0.4:
                boost_factor = 1.2
                for emotion in emotion_scores:
                    if emotion == dominant_emotion:
                        emotion_scores[emotion] = min(1.0, emotion_scores[emotion] * boost_factor)
            else:
                        emotion_scores[emotion] = emotion_scores[emotion] * 0.9
            
            # Normalize scores again after adjustments
            total = sum(emotion_scores.values())
            if total > 0:
                for emotion in emotion_scores:
                    emotion_scores[emotion] /= total
            
            return emotion_scores
            
        except Exception as e:
            logger.error(f"Error in enhanced classification: {str(e)}")
            default_scores = {emotion: 0.0 for emotion in self.emotion_labels}
            default_scores['neutral'] = 1.0
            return default_scores

# Create a singleton instance
emotion_detector = EmotionDetector(test_mode=False) 