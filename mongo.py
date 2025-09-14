from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
import os
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv:/uster0')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'jiotv_bot')

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db['users']
    interactions_collection = db['interactions']
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    client = None

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if client:
            # Test database connection
            client.admin.command('ping')
            return jsonify({
                'status': 'healthy',
                'message': 'MongoDB API is running',
                'database': DATABASE_NAME,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user to the database"""
    try:
        data = request.get_json()
        
        if not data or 'userId' not in data:
            return jsonify({'error': 'userId is required'}), 400
        
        user_id = str(data['userId'])
        
        # Check if user already exists
        existing_user = users_collection.find_one({'userId': user_id})
        if existing_user:
            # Update last active time
            users_collection.update_one(
                {'userId': user_id},
                {'$set': {'lastActive': datetime.now(timezone.utc)}}
            )
            return jsonify({
                'success': True,
                'message': 'User already exists, updated activity',
                'isNew': False
            }), 200
        
        # Create new user document
        user_doc = {
            'userId': user_id,
            'firstName': data.get('firstName'),
            'lastName': data.get('lastName'),
            'username': data.get('username'),
            'languageCode': data.get('languageCode'),
            'joinedAt': datetime.now(timezone.utc),
            'lastActive': datetime.now(timezone.utc)
        }
        
        result = users_collection.insert_one(user_doc)
        
        return jsonify({
            'success': True,
            'message': 'User added successfully',
            'userId': user_id,
            'isNew': True,
            'insertedId': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>/exists', methods=['GET'])
def check_user_exists(user_id):
    """Check if a user exists in the database"""
    try:
        user = users_collection.find_one({'userId': str(user_id)})
        return jsonify({
            'exists': user is not None,
            'userId': str(user_id)
        }), 200
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users/<user_id>/activity', methods=['PUT'])
def update_user_activity(user_id):
    """Update user's last active time"""
    try:
        result = users_collection.update_one(
            {'userId': str(user_id)},
            {'$set': {'lastActive': datetime.now(timezone.utc)}}
        )
        
        return jsonify({
            'success': True,
            'modified': result.modified_count > 0,
            'userId': str(user_id)
        }), 200
    except Exception as e:
        logger.error(f"Error updating user activity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users from the database"""
    try:
        users = list(users_collection.find({}, {'_id': 0}))  # Exclude _id field
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users/count', methods=['GET'])
def get_user_count():
    """Get total number of users"""
    try:
        count = users_collection.count_documents({})
        return jsonify({
            'success': True,
            'count': count
        }), 200
    except Exception as e:
        logger.error(f"Error getting user count: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/interactions', methods=['POST'])
def add_interaction():
    """Add a user interaction record"""
    try:
        data = request.get_json()
        
        if not data or 'userId' not in data or 'action' not in data:
            return jsonify({'error': 'userId and action are required'}), 400
        
        interaction_doc = {
            'userId': str(data['userId']),
            'action': data['action'],
            'timestamp': datetime.now(timezone.utc),
            'command': data.get('command'),
            'channelKey': data.get('channelKey'),
            'details': data.get('details', {})
        }
        
        result = interactions_collection.insert_one(interaction_doc)
        
        return jsonify({
            'success': True,
            'message': 'Interaction recorded',
            'insertedId': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding interaction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/interactions/<user_id>', methods=['GET'])
def get_user_interactions(user_id):
    """Get interactions for a specific user"""
    try:
        interactions = list(interactions_collection.find(
            {'userId': str(user_id)}, 
            {'_id': 0}
        ).sort('timestamp', -1).limit(50))  # Get last 50 interactions
        
        return jsonify({
            'success': True,
            'interactions': interactions,
            'count': len(interactions),
            'userId': str(user_id)
        }), 200
    except Exception as e:
        logger.error(f"Error getting user interactions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        user_count = users_collection.count_documents({})
        interaction_count = interactions_collection.count_documents({})
        
        # Get recent users (joined in last 24 hours)
        yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        recent_users = users_collection.count_documents({
            'joinedAt': {'$gte': yesterday}
        })
        
        # Get active users (active in last 24 hours)
        active_users = users_collection.count_documents({
            'lastActive': {'$gte': yesterday}
        })
        
        return jsonify({
            'success': True,
            'stats': {
                'totalUsers': user_count,
                'totalInteractions': interaction_count,
                'recentUsers24h': recent_users,
                'activeUsers24h': active_users,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users/broadcast-list', methods=['GET'])
def get_broadcast_list():
    """Get list of user IDs for broadcasting"""
    try:
        users = users_collection.find({}, {'userId': 1, '_id': 0})
        user_ids = [user['userId'] for user in users]
        
        return jsonify({
            'success': True,
            'userIds': user_ids,
            'count': len(user_ids)
        }), 200
    except Exception as e:
        logger.error(f"Error getting broadcast list: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
