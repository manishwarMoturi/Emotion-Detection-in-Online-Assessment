import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Components
import Login from './components/auth/Login';
import StudentDashboard from './components/student/StudentDashboard';
import TestTakerDashboard from './components/testtaker/TestTakerDashboard';
import AdminDashboard from './components/admin/AdminDashboard';
import PracticeProblem from './components/practice/PracticeProblem';
import LiveExam from './components/exam/LiveExam';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#9c27b0',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#0a1929',
      paper: '#1a2027',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/student/*" element={<StudentDashboard />} />
          <Route path="/testtaker/*" element={<TestTakerDashboard />} />
          <Route path="/admin/*" element={<AdminDashboard />} />
          <Route path="/practice/:problemId" element={<PracticeProblem />} />
          <Route path="/exam/:examId" element={<LiveExam />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 