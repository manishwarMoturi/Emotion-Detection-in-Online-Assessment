import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  CircularProgress,
} from '@mui/material';
import Editor from '@monaco-editor/react';
import Webcam from 'react-webcam';
import * as faceapi from '@tensorflow-models/face-landmarks-detection';

interface EmotionData {
  timestamp: number;
  emotion: string;
  confidence: number;
}

const PracticeProblem: React.FC = () => {
  const { problemId } = useParams<{ problemId: string }>();
  const [code, setCode] = useState<string>('// Write your solution here\n');
  const [output, setOutput] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [emotionData, setEmotionData] = useState<EmotionData[]>([]);
  const webcamRef = useRef<Webcam>(null);
  const [model, setModel] = useState<any>(null);

  // Mock problem data
  const problem = {
    title: 'Two Sum',
    difficulty: 'Easy',
    description:
      'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
    examples: [
      {
        input: 'nums = [2,7,11,15], target = 9',
        output: '[0,1]',
        explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].',
      },
    ],
  };

  useEffect(() => {
    // Load face detection model
    const loadModel = async () => {
      const model = await faceapi.load();
      setModel(model);
    };
    loadModel();

    // Start emotion detection
    const interval = setInterval(detectEmotion, 1000);
    return () => clearInterval(interval);
  }, []);

  const detectEmotion = async () => {
    if (
      webcamRef.current &&
      webcamRef.current.video &&
      model &&
      webcamRef.current.video.readyState === 4
    ) {
      const video = webcamRef.current.video;
      const face = await model.estimateFaces(video, {
        flipHorizontal: false,
      });

      if (face.length > 0) {
        // This is a mock emotion detection - in reality, you'd use a proper emotion detection model
        const mockEmotions = ['focused', 'confused', 'frustrated', 'neutral'];
        const randomEmotion =
          mockEmotions[Math.floor(Math.random() * mockEmotions.length)];
        
        setEmotionData((prev) => [
          ...prev,
          {
            timestamp: Date.now(),
            emotion: randomEmotion,
            confidence: Math.random(),
          },
        ]);
      }
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value) {
      setCode(value);
    }
  };

  const runCode = async () => {
    setIsRunning(true);
    // Mock code execution
    setTimeout(() => {
      setOutput('Output: [0, 1]');
      setIsRunning(false);
    }, 1000);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              {problem.title}
            </Typography>
            <Typography variant="body1" paragraph>
              {problem.description}
            </Typography>
            <Typography variant="h6" gutterBottom>
              Example:
            </Typography>
            <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
              <Typography variant="body2">
                Input: {problem.examples[0].input}
              </Typography>
              <Typography variant="body2">
                Output: {problem.examples[0].output}
              </Typography>
              <Typography variant="body2">
                Explanation: {problem.examples[0].explanation}
              </Typography>
            </Box>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Editor
              height="500px"
              defaultLanguage="javascript"
              value={code}
              onChange={handleEditorChange}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
              }}
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={runCode}
                disabled={isRunning}
              >
                {isRunning ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Run Code'
                )}
              </Button>
            </Box>
            {output && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100' }}>
                <Typography variant="body2" component="pre">
                  {output}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Emotion Detection
            </Typography>
            <Box sx={{ width: '100%', mb: 2 }}>
              <Webcam
                ref={webcamRef}
                audio={false}
                width="100%"
                screenshotFormat="image/jpeg"
                videoConstraints={{
                  width: 320,
                  height: 240,
                  facingMode: 'user',
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Current Emotion:{' '}
              {emotionData.length > 0
                ? emotionData[emotionData.length - 1].emotion
                : 'Detecting...'}
            </Typography>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Emotion History
            </Typography>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              {emotionData.slice(-10).map((data, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 1,
                    mb: 1,
                    bgcolor: 'grey.100',
                    borderRadius: 1,
                  }}
                >
                  <Typography variant="body2">
                    Emotion: {data.emotion}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {(data.confidence * 100).toFixed(2)}%
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default PracticeProblem; 