// Monaco Editor Setup
require.config({
    paths: {
        'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs'
    }
});

let editor;
window.onload = function() {
    require(['vs/editor/editor.main'], function() {
        editor = monaco.editor.create(document.getElementById('editor'), {
            value: '// Write your solution here\n',
            language: 'javascript',
            theme: 'vs-dark',
            minimap: {
                enabled: false
            },
            fontSize: 14,
            automaticLayout: true
        });

        // Language selection handling
        document.getElementById('language-select').addEventListener('change', (e) => {
            monaco.editor.setModelLanguage(editor.getModel(), e.target.value);
        });
    });
};

// Run code button handling
document.getElementById('run-btn')?.addEventListener('click', async () => {
    const outputContent = document.getElementById('output-content');
    if (!outputContent) return;
    
    outputContent.innerHTML = '<div class="loading">Running code...</div>';
    
    try {
        const code = editor?.getValue() || '';
        // In a real implementation, you would send this to a backend
        // For now, we'll use a mock execution
        setTimeout(() => {
            outputContent.innerHTML = `<pre>Output: [0, 1]
Test cases passed: 1/1</pre>`;
        }, 1000);
    } catch (error) {
        outputContent.innerHTML = `<pre class="error">${error.message}</pre>`;
    }
});

// Custom Emotion Detection Setup
let customModel = null;
let isEmotionDetectionActive = false;
let emotionDetectionInterval = null;
let videoStream = null;

async function setupEmotionDetection() {
    try {
        // Check if browser supports getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('Browser does not support webcam access');
        }

        // Access webcam
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 320,
                height: 240,
                facingMode: 'user'
            } 
        });
        
        const video = document.getElementById('webcam');
        if (!video) return;

        video.srcObject = videoStream;
        video.onloadedmetadata = () => {
            video.play();
            isEmotionDetectionActive = true;
            startEmotionDetection();
        };

        // Handle camera being turned off
        videoStream.getVideoTracks()[0].addEventListener('ended', () => {
            stopEmotionDetection();
        });

        // Load your custom model
        console.log('Loading custom emotion detection model...');
        // TODO: Replace this with your model loading code
        // Example for TensorFlow.js:
        // customModel = await tf.loadGraphModel('path/to/your/model.json');
        
    } catch (error) {
        console.error('Error setting up emotion detection:', error);
        const emotionStatus = document.querySelector('.emotion-status');
        if (emotionStatus) {
            emotionStatus.innerHTML = `<p class="error">Failed to initialize emotion detection: ${error.message}</p>`;
        }
    }
}

function stopEmotionDetection() {
    isEmotionDetectionActive = false;
    
    // Clear the interval
    if (emotionDetectionInterval) {
        clearInterval(emotionDetectionInterval);
        emotionDetectionInterval = null;
    }

    // Stop all video tracks
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }

    // Update UI to show camera is off
    const currentEmotion = document.getElementById('current-emotion');
    const confidenceBar = document.getElementById('confidence-bar');
    if (currentEmotion) {
        currentEmotion.textContent = 'Camera Off';
    }
    if (confidenceBar) {
        confidenceBar.style.width = '0%';
    }
}

async function startEmotionDetection() {
    if (!isEmotionDetectionActive) return;

    const video = document.getElementById('webcam');
    const currentEmotion = document.getElementById('current-emotion');
    const confidenceBar = document.getElementById('confidence-bar');
    const emotionTimeline = document.getElementById('emotion-timeline');

    if (!video || !currentEmotion || !confidenceBar || !emotionTimeline) return;

    // Clear any existing interval
    if (emotionDetectionInterval) {
        clearInterval(emotionDetectionInterval);
    }

    const updateEmotions = async () => {
        if (!isEmotionDetectionActive || video.readyState !== 4) return;

        try {
            // TODO: Replace this with your model inference code
            // Example for TensorFlow.js:
            /*
            const tensor = tf.browser.fromPixels(video)
                .resizeNearestNeighbor([224, 224])
                .toFloat()
                .expandDims();
            
            const predictions = await customModel.predict(tensor);
            const emotion = processPredictions(predictions);
            */

            // For now, using mock data
            const emotions = ['focused', 'confused', 'frustrated', 'neutral'];
            const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
            const confidence = Math.random();

            // Update current emotion
            currentEmotion.textContent = randomEmotion;
            confidenceBar.style.width = `${confidence * 100}%`;

            // Add to timeline
            const entry = document.createElement('div');
            entry.className = 'emotion-entry';
            entry.innerHTML = `
                <span>${randomEmotion}</span>
                <span class="time">${new Date().toLocaleTimeString()}</span>
            `;
            emotionTimeline.insertBefore(entry, emotionTimeline.firstChild);

            // Keep only last 10 entries
            if (emotionTimeline.children.length > 10) {
                emotionTimeline.removeChild(emotionTimeline.lastChild);
            }
        } catch (error) {
            console.error('Error detecting emotion:', error);
        }
    };

    // Update emotions every 2 seconds
    emotionDetectionInterval = setInterval(updateEmotions, 2000);
}

// Initialize emotion detection when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupEmotionDetection);
} else {
    setupEmotionDetection();
}

// Clean up when the page is unloaded
window.addEventListener('beforeunload', () => {
    stopEmotionDetection();
}); 