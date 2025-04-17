class EmotionDetector {
    constructor() {
        this.detectionInterval = null;
        this.isDetectionActive = false;
        this.pythonServiceUrl = 'http://localhost:5000/detect';
    }

    async startDetection(videoElement, callback) {
        if (this.isDetectionActive) {
            console.log('Detection already active');
            return;
        }

        this.isDetectionActive = true;
        console.log('Starting emotion detection...');

        this.detectionInterval = setInterval(async () => {
            try {
                if (!videoElement || videoElement.paused || videoElement.ended) {
                    this.stopDetection();
                    return;
                }

                // Capture frame from video
                const frame = await this.captureFrame(videoElement);
                
                // Send frame to Python service
                const emotion = await this.detectEmotion(frame);
                
                // Call the callback with results
                if (callback && emotion) {
                    callback(emotion);
                }
            } catch (error) {
                console.error('Error during emotion detection:', error);
            }
        }, 1000); // Adjust interval as needed
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

    async detectEmotion(frameData) {
        try {
            const response = await fetch(this.pythonServiceUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: frameData
                })
            });

            if (!response.ok) {
                throw new Error('Failed to detect emotion');
            }

            const result = await response.json();
            
            if (result.success) {
                return {
                    emotion: result.emotion,
                    confidence: result.confidence
                };
            } else {
                console.error('Emotion detection failed:', result.error);
                return null;
            }
        } catch (error) {
            console.error('Error in emotion detection:', error);
            return null;
        }
    }
}

// Export the class
window.EmotionDetector = EmotionDetector; 