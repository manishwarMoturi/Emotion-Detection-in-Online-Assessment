import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Tabs,
  Tab,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const StudentDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const practiceProblemsList = [
    {
      id: 1,
      title: 'Two Sum',
      difficulty: 'Easy',
      description: 'Find two numbers that add up to a target',
    },
    {
      id: 2,
      title: 'Valid Parentheses',
      difficulty: 'Medium',
      description: 'Check if parentheses are valid',
    },
  ];

  const upcomingExams = [
    {
      id: 1,
      title: 'Data Structures Exam',
      date: '2024-03-20',
      duration: '2 hours',
    },
    {
      id: 2,
      title: 'Algorithms Final',
      date: '2024-03-25',
      duration: '3 hours',
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Welcome to Your Dashboard
            </Typography>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange}>
                <Tab label="Practice Problems" />
                <Tab label="Upcoming Exams" />
              </Tabs>
            </Box>

            <TabPanel value={tabValue} index={0}>
              <Grid container spacing={3}>
                {practiceProblemsList.map((problem) => (
                  <Grid item xs={12} md={6} key={problem.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6">{problem.title}</Typography>
                        <Typography
                          sx={{ mb: 1.5 }}
                          color="text.secondary"
                        >
                          Difficulty: {problem.difficulty}
                        </Typography>
                        <Typography variant="body2">
                          {problem.description}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          onClick={() =>
                            navigate(`/practice/${problem.id}`)
                          }
                        >
                          Start Practice
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <Grid container spacing={3}>
                {upcomingExams.map((exam) => (
                  <Grid item xs={12} md={6} key={exam.id}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6">{exam.title}</Typography>
                        <Typography
                          sx={{ mb: 1.5 }}
                          color="text.secondary"
                        >
                          Date: {exam.date}
                        </Typography>
                        <Typography variant="body2">
                          Duration: {exam.duration}
                        </Typography>
                      </CardContent>
                      <CardActions>
                        <Button
                          size="small"
                          onClick={() => navigate(`/exam/${exam.id}`)}
                        >
                          View Details
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default StudentDashboard; 