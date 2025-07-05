from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime

# Import configuration
from config.config import get_config

# Import models
from models.user import db as user_db, User
from models.health import db as health_db, HealthRecord, SymptomReport, RiskAssessment, EnvironmentalData

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register API blueprints
    from api.auth import auth_bp
    from api.health import health_bp
    from api.predictions import predictions_bp
    from api.environmental import environmental_bp
    from api.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(environmental_bp, url_prefix='/api/environmental')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # API root endpoint
    @app.route('/api')
    def api_root():
        return jsonify({
            'message': 'AI-Powered Health Monitoring System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'health': '/api/health',
                'predictions': '/api/predictions',
                'environmental': '/api/environmental',
                'dashboard': '/api/dashboard'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@healthmonitor.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@healthmonitor.com',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            app.logger.info('Created default admin user')
    
    return app

# Create the Flask app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)