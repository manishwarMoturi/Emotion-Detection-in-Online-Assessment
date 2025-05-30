// Immediate debugging message to verify script loading
console.log('🔍 SCRIPT LOADED: emotion-detection.js');

class EmotionDetector {
    constructor() {
        console.log('⚙️ EmotionDetector constructor called');
        this.detectionInterval = null;
        this.isDetectionActive = false;
        this.apiUrl = '/api/detect-emotion/';  // Django API endpoint
        this.attemptId = null;  // Will store exam attempt ID if in exam mode
        this.debugMode = true;  // Enable debug logging
        this.backendConnected = false; // Track connection status
        this.video = document.getElementById('webcam');
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.emotionLabel = document.getElementById('detected-emotion-label');
        this.detectionDetails = document.getElementById('detection-details');
        this.emotionHistory = [];
        this.maxHistoryLength = 10;
        this.apiEndpoint = 'http://localhost:5000/detect_emotion';
        this.isDetecting = false;
    }

    setAttemptId(attemptId) {
        this.attemptId = attemptId;
    }

    async startDetection(videoElement, callback) {
        if (this.isDetectionActive) {
            console.log('Detection already active');
            return;
        }

        this.isDetectionActive = true;
        console.log('Starting emotion detection...');

        // Try to make one API call to check if backend is working
        if (!this.backendConnected) {
            try {
                // Capture a frame just to test connection
                const testFrame = await this.captureFrame(videoElement);
                const testResult = await this.detectEmotion(testFrame, true);
                
                if (testResult && !testResult.isMock) {
                    this.backendConnected = true;
                    console.log('%c✅ CONNECTED TO BACKEND EMOTION DETECTION ENGINE', 'color: green; font-weight: bold');
                    console.log('Using Python backend emotions: angry, disgusted, fearful, happy, sad, surprised, neutral');
                } else {
                    console.warn('⚠️ Using mock emotion data - backend connection failed');
                    console.log('Using mock data emotions: happy, sad, neutral, surprised');
                }
            } catch (err) {
                console.error('Error during initial connection test:', err);
            }
        }

        this.detectionInterval = setInterval(async () => {
            try {
                if (!videoElement || videoElement.paused || videoElement.ended) {
                    this.stopDetection();
                    return;
                }

                // Capture frame from video
                const frame = await this.captureFrame(videoElement);
                if (this.debugMode) console.log('Frame captured, size:', frame.length);
                
                // Send frame to Python service
                const emotion = await this.detectEmotion(frame);
                if (this.debugMode) console.log('Emotion detected:', emotion);
                
                // Log emotion if in exam mode and we have a valid emotion
                if (this.attemptId && emotion && emotion.emotion !== 'unknown' && emotion.emotion !== 'error') {
                    this.logEmotion(emotion);
                }
                
                // Call the callback with results
                if (callback && emotion) {
                    callback(emotion);
                }
            } catch (error) {
                console.error('Error during emotion detection:', error);
            }
        }, 2000); // Detect every 2 seconds
    }

    stopDetection() {
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
        this.isDetectionActive = false;
        console.log('Emotion detection stopped');
    }

    async captureFrame(videoElement) {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        
        return canvas.toDataURL('image/jpeg').split(',')[1]; // Get base64 without prefix
    }

    async detectEmotion(frameData, isTest = false) {
        try {
            if (this.debugMode && !isTest) console.log('Sending request to:', this.apiUrl);
            
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken() // Include CSRF token for Django
                },
                body: JSON.stringify({
                    image: frameData
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                if (!isTest) console.error('API error:', response.status, errorText);
                throw new Error(`Failed to detect emotion: ${response.status} ${errorText}`);
            }

            const result = await response.json();
            if (this.debugMode && !isTest) {
                console.log('API response:', result);
                console.log('%c🎯 REAL EMOTION DATA RECEIVED: ' + result.emotion, 'color: green');
            }
            
            // The Django API returns emotion, confidence, and metrics
            return {
                emotion: result.emotion,
                confidence: result.confidence,
                metrics: result.metrics || {}  // Include metrics for debugging
            };
        } catch (error) {
            if (!isTest) {
                console.error('Error in emotion detection:', error);
                console.error('%c❌ FORCING ERROR DISPLAY - NO FALLBACK TO MOCK DATA', 'color: red; font-weight: bold');
            }
            
            // Return error object instead of mock data
            return {
                emotion: "Error: " + error.message,
                confidence: 0,
                isError: true,
                metrics: {}
            };
        }
    }
    
    async logEmotion(emotionData) {
        if (!this.attemptId) return;
        
        try {
            const response = await fetch(`/api/exam-attempts/${this.attemptId}/log-emotion/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    emotion: emotionData.emotion,
                    confidence: emotionData.confidence
                })
            });
            
            if (!response.ok) {
                console.error('Failed to log emotion');
            }
        } catch (error) {
            console.error('Error logging emotion:', error);
        }
    }
    
    // Helper to get Django CSRF token from cookies
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async start() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            this.video.srcObject = stream;
            await this.video.play();
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            
            // Start periodic detection
            this.startPeriodicDetection();
        } catch (error) {
            console.error('Error accessing webcam:', error);
            this.emotionLabel.textContent = 'Error accessing webcam';
        }
    }

    startPeriodicDetection() {
        if (!this.isDetecting) {
            this.isDetecting = true;
            this.detectLoop();
        }
    }

    stopPeriodicDetection() {
        this.isDetecting = false;
    }

    async detectLoop() {
        if (!this.isDetecting) return;

        try {
            await this.detectEmotion();
            setTimeout(() => this.detectLoop(), 2000); // Detect every 2 seconds
        } catch (error) {
            console.error('Error in detection loop:', error);
            setTimeout(() => this.detectLoop(), 2000);
        }
    }

    async detectEmotion() {
        try {
            // Draw current frame to canvas
            this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            // Convert canvas to base64
            const imageData = this.canvas.toDataURL('image/jpeg');
            
            // Send directly to Flask API
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // No CSRF token needed when calling Flask directly from frontend
                },
                body: JSON.stringify({ image: imageData })
            });

            const data = await response.json();
            
            // Check if the Flask service returned an error in its JSON
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Check for basic HTTP errors
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Update UI with results
            if (data.results && data.results.length > 0) {
                const result = data.results[0]; // Get the first face detected
                const emotion = result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1);
                this.emotionLabel.textContent = emotion;
                this.detectionDetails.textContent = `Confidence: ${(result.confidence * 100).toFixed(1)}%`;
                
                // Add to history
                this.addToHistory(emotion, result.confidence);
            } else {
                this.emotionLabel.textContent = 'No face detected';
                this.detectionDetails.textContent = '';
            }
        } catch (error) {
            console.error('Error detecting emotion:', error);
            this.emotionLabel.textContent = 'Error'; 
            this.detectionDetails.textContent = error.message;
        }
    }

    addToHistory(emotion, confidence) {
        const timestamp = new Date().toLocaleTimeString();
        this.emotionHistory.unshift({
            emotion,
            confidence,
            timestamp
        });

        // Keep only the last N entries
        if (this.emotionHistory.length > this.maxHistoryLength) {
            this.emotionHistory.pop();
        }

        // Update history display
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        const timeline = document.getElementById('emotion-timeline');
        timeline.innerHTML = this.emotionHistory.map(entry => `
            <div class="emotion-entry">
                <span class="emotion">${entry.emotion}</span>
                <span class="confidence">${(entry.confidence * 100).toFixed(1)}%</span>
                <span class="timestamp">${entry.timestamp}</span>
            </div>
        `).join('');
    }
}

// Export the class
window.EmotionDetector = EmotionDetector;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const detector = new EmotionDetector();
    detector.start();

    // Set up test button
    const testButton = document.getElementById('test-single-frame');
    testButton.addEventListener('click', () => {
        detector.detectEmotion();
    });
}); 