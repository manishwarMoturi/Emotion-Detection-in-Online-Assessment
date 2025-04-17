const mongoose = require('mongoose');

// Users Schema
const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  role: {
    type: String,
    required: true,
    enum: ['Student', 'Instructor', 'Admin']
  },
  // Additional fields for emotion detection platform
  institution: String,
  department: String,
  lastActive: Date,
  emotionHistory: [{
    timestamp: Date,
    emotion: String,
    confidence: Number
  }]
}, {
  timestamps: true
});

// Assessments Schema
const assessmentSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  instructorId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // Additional fields for emotion detection platform
  duration: {
    type: Number,  // in minutes
    required: true
  },
  startTime: {
    type: Date,
    required: true
  },
  endTime: {
    type: Date,
    required: true
  },
  status: {
    type: String,
    enum: ['draft', 'scheduled', 'ongoing', 'completed'],
    default: 'draft'
  },
  participants: [{
    studentId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    status: {
      type: String,
      enum: ['registered', 'started', 'completed'],
      default: 'registered'
    },
    emotionData: [{
      timestamp: Date,
      emotion: String,
      confidence: Number
    }],
    score: Number,
    submittedAt: Date
  }],
  questions: [{
    questionText: String,
    points: Number,
    testCases: [{
      input: String,
      expectedOutput: String
    }]
  }]
}, {
  timestamps: true
});

// Create indexes
userSchema.index({ email: 1 });
userSchema.index({ role: 1 });
assessmentSchema.index({ instructorId: 1 });
assessmentSchema.index({ status: 1 });
assessmentSchema.index({ 'participants.studentId': 1 });

// Create models
const User = mongoose.model('User', userSchema);
const Assessment = mongoose.model('Assessment', assessmentSchema);

module.exports = {
  User,
  Assessment
}; 