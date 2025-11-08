// MongoDB initialization script for hate speech moderation system

// Switch to the application database
db = db.getSiblingDB('hate_speech_mitigation');

// Create collections with validation schemas
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'username', 'email'],
      properties: {
        user_id: {
          bsonType: 'string',
          pattern: '^user_[a-zA-Z0-9]+$'
        },
        username: {
          bsonType: 'string',
          minLength: 3,
          maxLength: 50
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        },
        'behavior_profile.risk_level': {
          enum: ['low', 'medium', 'high']
        },
        'behavior_profile.trust_score': {
          bsonType: 'double',
          minimum: 0,
          maximum: 1
        }
      }
    }
  }
});

db.createCollection('conversations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['conversation_id', 'participants', 'metadata'],
      properties: {
        conversation_id: {
          bsonType: 'string',
          pattern: '^conv_[a-zA-Z0-9]+$'
        },
        participants: {
          bsonType: 'array',
          minItems: 1
        },
        'metadata.moderation_level': {
          enum: ['none', 'basic', 'strict']
        },
        status: {
          enum: ['active', 'archived', 'moderated']
        }
      }
    }
  }
});

db.createCollection('messages', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['message_id', 'conversation_id', 'user_id', 'content', 'timestamp'],
      properties: {
        message_id: {
          bsonType: 'string',
          pattern: '^msg_[a-zA-Z0-9]+$'
        },
        content: {
          bsonType: 'string',
          minLength: 1,
          maxLength: 10000
        },
        'toxicity_analysis.overall_score': {
          bsonType: 'double',
          minimum: 0,
          maximum: 1
        },
        'moderation_action.action': {
          enum: ['none', 'warn', 'hide', 'delete', 'ban']
        }
      }
    }
  }
});

db.createCollection('context_embeddings');
db.createCollection('moderation_logs');
db.createCollection('feedback');

// Create indexes for optimal performance
print('Creating indexes...');

// Users collection indexes
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "behavior_profile.risk_level": 1 });
db.users.createIndex({ "last_active": -1 });
db.users.createIndex({ "created_at": -1 });

// Conversations collection indexes
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.conversations.createIndex({ "participants": 1 });
db.conversations.createIndex({ "updated_at": -1 });
db.conversations.createIndex({ "status": 1 });
db.conversations.createIndex({ "metadata.platform": 1 });

// Messages collection indexes
db.messages.createIndex({ "message_id": 1 }, { unique: true });
db.messages.createIndex({ "conversation_id": 1 });
db.messages.createIndex({ "user_id": 1 });
db.messages.createIndex({ "timestamp": -1 });
db.messages.createIndex({ "conversation_id": 1, "timestamp": -1 });
db.messages.createIndex({ "toxicity_analysis.overall_score": 1 });
db.messages.createIndex({ "moderation_action.action": 1 });

// Context embeddings collection indexes
db.context_embeddings.createIndex({ "conversation_id": 1 });
db.context_embeddings.createIndex({ "created_at": -1 });
db.context_embeddings.createIndex({ "context_type": 1 });

// Moderation logs collection indexes
db.moderation_logs.createIndex({ "message_id": 1 });
db.moderation_logs.createIndex({ "user_id": 1 });
db.moderation_logs.createIndex({ "timestamp": -1 });
db.moderation_logs.createIndex({ "action": 1 });

// Feedback collection indexes
db.feedback.createIndex({ "message_id": 1 });
db.feedback.createIndex({ "user_id": 1 });
db.feedback.createIndex({ "appeal_id": 1 });
db.feedback.createIndex({ "review_id": 1 });
db.feedback.createIndex({ "created_at": -1 });

print('Indexes created successfully.');

// Insert initial data for demonstration
print('Inserting sample data...');

// Sample users
db.users.insertMany([
  {
    user_id: 'user_demo001',
    username: 'alice',
    email: 'alice@example.com',
    created_at: new Date(),
    last_active: new Date(),
    behavior_profile: {
      average_toxicity_score: 0.1,
      message_frequency: 5,
      moderation_history: {
        total_messages: 50,
        flagged_messages: 2,
        false_positives: 1,
        corrected_moderations: 0
      },
      risk_level: 'low',
      trust_score: 0.85
    },
    preferences: {
      moderation_sensitivity: 'moderate',
      notification_settings: {
        email_notifications: true,
        moderation_warnings: true,
        account_status_changes: true
      }
    }
  },
  {
    user_id: 'user_demo002',
    username: 'bob',
    email: 'bob@example.com',
    created_at: new Date(),
    last_active: new Date(),
    behavior_profile: {
      average_toxicity_score: 0.4,
      message_frequency: 20,
      moderation_history: {
        total_messages: 200,
        flagged_messages: 25,
        false_positives: 3,
        corrected_moderations: 2
      },
      risk_level: 'medium',
      trust_score: 0.6
    },
    preferences: {
      moderation_sensitivity: 'moderate',
      notification_settings: {
        email_notifications: true,
        moderation_warnings: true,
        account_status_changes: true
      }
    }
  }
]);

// Sample conversations
db.conversations.insertMany([
  {
    conversation_id: 'conv_demo001',
    participants: ['user_demo001', 'user_demo002'],
    created_at: new Date(),
    updated_at: new Date(),
    status: 'active',
    metadata: {
      topic: 'General Discussion',
      language: 'en',
      platform: 'discord',
      moderation_level: 'basic'
    }
  }
]);

// Sample messages
db.messages.insertMany([
  {
    message_id: 'msg_demo001',
    conversation_id: 'conv_demo001',
    user_id: 'user_demo001',
    content: 'Hello everyone! How is your day going?',
    timestamp: new Date(),
    toxicity_analysis: {
      overall_score: 0.02,
      predictions: {
        toxic: 0.01,
        severe_toxic: 0.0,
        obscene: 0.0,
        threat: 0.0,
        insult: 0.0,
        identity_hate: 0.0
      },
      confidence: 0.95,
      processing_time_ms: 45
    },
    moderation_action: {
      action: 'none',
      confidence: 0.95,
      reason: 'Content appears to be within acceptable limits',
      adjusted_threshold: 0.4,
      applied_at: new Date(),
      applied_by: 'system'
    },
    feedback: {
      user_reported: false,
      community_flags: 0,
      appeal_status: 'none'
    }
  },
  {
    message_id: 'msg_demo002',
    conversation_id: 'conv_demo001',
    user_id: 'user_demo002',
    content: 'I think this platform could use some improvements.',
    timestamp: new Date(),
    toxicity_analysis: {
      overall_score: 0.15,
      predictions: {
        toxic: 0.1,
        severe_toxic: 0.0,
        obscene: 0.0,
        threat: 0.0,
        insult: 0.05,
        identity_hate: 0.0
      },
      confidence: 0.88,
      processing_time_ms: 52
    },
    moderation_action: {
      action: 'none',
      confidence: 0.88,
      reason: 'Content appears to be within acceptable limits',
      adjusted_threshold: 0.48,
      applied_at: new Date(),
      applied_by: 'system'
    },
    feedback: {
      user_reported: false,
      community_flags: 0,
      appeal_status: 'none'
    }
  }
]);

print('Sample data inserted successfully.');

// Create database user for application
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'hate_speech_mitigation'
    }
  ]
});

print('Database user created successfully.');
print('MongoDB initialization completed successfully!');