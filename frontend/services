const db = require('../config/database');
const { EmotionData, EmotionSession } = require('../models');

class EmotionService {
    static async createSession(userId) {
        try {
            const session = await EmotionSession.create({
                user_id: userId,
                start_time: new Date()
            });
            return session;
        } catch (error) {
            console.error('Error creating emotion session:', error);
            throw error;
        }
    }

    static async endSession(sessionId) {
        try {
            await EmotionSession.update(
                { end_time: new Date() },
                { where: { session_id: sessionId } }
            );
        } catch (error) {
            console.error('Error ending emotion session:', error);
            throw error;
        }
    }

    static async saveEmotionData(sessionId, emotionData, modelId) {
        try {
            const data = await EmotionData.create({
                session_id: sessionId,
                emotion_type: emotionData.emotion,
                confidence: emotionData.confidence,
                model_id: modelId
            });
            return data;
        } catch (error) {
            console.error('Error saving emotion data:', error);
            throw error;
        }
    }

    static async getEmotionStats(userId, startDate, endDate) {
        try {
            const stats = await EmotionData.findAll({
                where: {
                    '$EmotionSession.user_id$': userId,
                    timestamp: {
                        [Op.between]: [startDate, endDate]
                    }
                },
                include: [{
                    model: EmotionSession,
                    required: true
                }],
                attributes: [
                    'emotion_type',
                    [db.fn('COUNT', db.col('emotion_id')), 'count'],
                    [db.fn('AVG', db.col('confidence')), 'avg_confidence']
                ],
                group: ['emotion_type']
            });
            return stats;
        } catch (error) {
            console.error('Error getting emotion stats:', error);
            throw error;
        }
    }
}

module.exports = EmotionService; 