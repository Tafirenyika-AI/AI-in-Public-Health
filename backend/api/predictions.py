from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Add parent directory to path to import ML models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User, db
from models.health import RiskAssessment, RiskCategory, SeverityLevel
from ml_models.nlp.symptom_classifier import SymptomClassifier
from ml_models.numerical.risk_predictor import HealthRiskPredictor

predictions_bp = Blueprint('predictions', __name__)

# Initialize ML models (these would be loaded from saved models in production)
symptom_classifier = None
risk_predictor = None

def initialize_models():
    """Initialize ML models."""
    global symptom_classifier, risk_predictor
    
    try:
        # Initialize symptom classifier
        symptom_classifier = SymptomClassifier()
        if not symptom_classifier.is_trained:
            print("Training symptom classifier...")
            symptom_classifier.train()
            # Save the model
            symptom_classifier.save_model("ml_models/nlp/trained_symptom_classifier.pkl")
        
        # Initialize risk predictor
        risk_predictor = HealthRiskPredictor()
        if not risk_predictor.is_trained:
            print("Training risk predictor...")
            risk_predictor.train()
            # Save the model
            risk_predictor.save_model("ml_models/numerical/trained_risk_predictor.pkl")
            
        print("ML models initialized successfully")
        
    except Exception as e:
        print(f"Error initializing ML models: {str(e)}")
        current_app.logger.error(f"Error initializing ML models: {str(e)}")

@predictions_bp.route('/symptoms/analyze', methods=['POST'])
@jwt_required()
def analyze_symptoms():
    """Analyze symptoms using NLP model."""
    try:
        global symptom_classifier
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('symptom_text'):
            return jsonify({'error': 'Symptom text is required'}), 400
        
        # Initialize models if not already done
        if symptom_classifier is None:
            initialize_models()
        
        if symptom_classifier is None or not symptom_classifier.is_trained:
            return jsonify({'error': 'Symptom classifier not available'}), 503
        
        # Analyze symptoms
        analysis_result = symptom_classifier.predict(data['symptom_text'])
        
        # Create risk assessment record
        risk_assessment = RiskAssessment(
            user_id=current_user_id,
            risk_category=RiskCategory.INFECTIOUS_DISEASE,  # Default category
            risk_level=SeverityLevel.MEDIUM,  # Default level
            risk_score=analysis_result['confidence'],
            predicted_condition=analysis_result['predicted_condition'],
            confidence_score=analysis_result['confidence'],
            model_version='1.0',
            model_type='nlp_symptom_classifier',
            assessed_at=datetime.utcnow()
        )
        
        # Set risk factors and recommendations
        risk_assessment.set_risk_factors(analysis_result['symptoms_categorized'])
        risk_assessment.set_recommendations([
            f"Consult healthcare provider about {analysis_result['predicted_condition']}",
            "Monitor symptoms closely",
            "Take rest and stay hydrated"
        ])
        
        db.session.add(risk_assessment)
        db.session.commit()
        
        return jsonify({
            'analysis': analysis_result,
            'risk_assessment_id': risk_assessment.id,
            'message': 'Symptom analysis completed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error analyzing symptoms: {str(e)}")
        return jsonify({'error': 'Failed to analyze symptoms'}), 500

@predictions_bp.route('/risk/assess', methods=['POST'])
@jwt_required()
def assess_health_risk():
    """Assess health risk using numerical model."""
    try:
        global risk_predictor
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Initialize models if not already done
        if risk_predictor is None:
            initialize_models()
        
        if risk_predictor is None or not risk_predictor.is_trained:
            return jsonify({'error': 'Risk predictor not available'}), 503
        
        # Prepare features for prediction
        features = {}
        
        # User demographics
        features['age'] = user.age or data.get('age', 30)
        features['gender'] = user.gender or data.get('gender', 'unknown')
        
        # Health metrics from request
        health_metrics = [
            'bp_systolic', 'bp_diastolic', 'heart_rate', 'temperature',
            'weight', 'height', 'bmi', 'glucose', 'cholesterol',
            'smoking', 'alcohol_consumption', 'physical_activity',
            'sleep_hours', 'stress_level', 'diet_score', 'salt_intake'
        ]
        
        for metric in health_metrics:
            if metric in data:
                features[metric] = data[metric]
        
        # Family history
        family_history_fields = [
            'family_history_cvd', 'family_history_diabetes', 'family_history_hypertension'
        ]
        
        for field in family_history_fields:
            features[field] = data.get(field, 0)
        
        # Environmental factors
        environmental_fields = [
            'air_quality', 'pollen_count', 'allergies', 'respiratory_infections'
        ]
        
        for field in environmental_fields:
            features[field] = data.get(field, 0)
        
        # Calculate BMI if height and weight are provided
        if 'height' in features and 'weight' in features and features['height'] > 0:
            height_m = features['height'] / 100  # Convert cm to m
            features['bmi'] = features['weight'] / (height_m ** 2)
        
        # Make prediction
        prediction_result = risk_predictor.predict(features)
        
        # Determine risk category and level
        risk_category = RiskCategory.CHRONIC_DISEASE
        risk_level = SeverityLevel.LOW
        
        if prediction_result['overall_risk'] == 'high':
            risk_level = SeverityLevel.HIGH
        elif prediction_result['overall_risk'] == 'medium':
            risk_level = SeverityLevel.MEDIUM
        
        # Create risk assessment record
        risk_assessment = RiskAssessment(
            user_id=current_user_id,
            risk_category=risk_category,
            risk_level=risk_level,
            risk_score=prediction_result['confidence'],
            predicted_condition=prediction_result['overall_risk'],
            confidence_score=prediction_result['confidence'],
            model_version='1.0',
            model_type='numerical_risk_predictor',
            assessed_at=datetime.utcnow()
        )
        
        # Set risk factors and recommendations
        risk_assessment.set_risk_factors(prediction_result['risk_scores'])
        risk_assessment.set_recommendations(prediction_result['recommendations'])
        
        db.session.add(risk_assessment)
        db.session.commit()
        
        return jsonify({
            'prediction': prediction_result,
            'risk_assessment_id': risk_assessment.id,
            'message': 'Health risk assessment completed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assessing health risk: {str(e)}")
        return jsonify({'error': 'Failed to assess health risk'}), 500

@predictions_bp.route('/assessments', methods=['GET'])
@jwt_required()
def get_risk_assessments():
    """Get user's risk assessments."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query risk assessments
        assessments = RiskAssessment.query.filter_by(user_id=current_user_id)\
            .order_by(RiskAssessment.assessed_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'assessments': [assessment.to_dict() for assessment in assessments],
            'total': len(assessments)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching risk assessments: {str(e)}")
        return jsonify({'error': 'Failed to fetch risk assessments'}), 500

@predictions_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
@jwt_required()
def get_risk_assessment(assessment_id):
    """Get a specific risk assessment."""
    try:
        current_user_id = get_jwt_identity()
        
        assessment = RiskAssessment.query.filter_by(
            id=assessment_id, 
            user_id=current_user_id
        ).first()
        
        if not assessment:
            return jsonify({'error': 'Risk assessment not found'}), 404
        
        return jsonify({
            'assessment': assessment.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching risk assessment: {str(e)}")
        return jsonify({'error': 'Failed to fetch risk assessment'}), 500

@predictions_bp.route('/quick-check', methods=['POST'])
@jwt_required()
def quick_health_check():
    """Perform a quick health check based on basic symptoms and vitals."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Basic health check logic
        alerts = []
        recommendations = []
        overall_status = "good"
        
        # Check vitals
        if data.get('bp_systolic', 0) > 140 or data.get('bp_diastolic', 0) > 90:
            alerts.append("High blood pressure detected")
            recommendations.append("Monitor blood pressure regularly")
            overall_status = "warning"
        
        if data.get('heart_rate', 0) > 100:
            alerts.append("Elevated heart rate detected")
            recommendations.append("Consider rest and check if persists")
            overall_status = "warning"
        
        if data.get('temperature', 0) > 99.5:
            alerts.append("Fever detected")
            recommendations.append("Monitor temperature and consider medical consultation")
            overall_status = "warning"
        
        # Check symptoms
        if data.get('symptom_text'):
            concerning_symptoms = [
                'chest pain', 'difficulty breathing', 'severe headache',
                'confusion', 'loss of consciousness', 'severe abdominal pain'
            ]
            
            symptom_text = data['symptom_text'].lower()
            for symptom in concerning_symptoms:
                if symptom in symptom_text:
                    alerts.append(f"Concerning symptom detected: {symptom}")
                    recommendations.append("Seek immediate medical attention")
                    overall_status = "urgent"
                    break
        
        # Check lifestyle factors
        if data.get('stress_level', 0) > 8:
            alerts.append("High stress level reported")
            recommendations.append("Consider stress management techniques")
        
        if data.get('sleep_hours', 8) < 5:
            alerts.append("Insufficient sleep detected")
            recommendations.append("Aim for 7-8 hours of sleep per night")
        
        # Set default recommendations if none generated
        if not recommendations:
            recommendations = [
                "Continue maintaining healthy lifestyle habits",
                "Regular exercise and balanced diet",
                "Stay hydrated and get adequate rest"
            ]
        
        return jsonify({
            'status': overall_status,
            'alerts': alerts,
            'recommendations': recommendations,
            'checked_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error performing quick health check: {str(e)}")
        return jsonify({'error': 'Failed to perform health check'}), 500

@predictions_bp.route('/models/status', methods=['GET'])
def get_model_status():
    """Get the status of ML models."""
    try:
        global symptom_classifier, risk_predictor
        
        status = {
            'symptom_classifier': {
                'loaded': symptom_classifier is not None,
                'trained': symptom_classifier.is_trained if symptom_classifier else False,
                'model_type': 'RandomForestClassifier with TF-IDF'
            },
            'risk_predictor': {
                'loaded': risk_predictor is not None,
                'trained': risk_predictor.is_trained if risk_predictor else False,
                'model_type': 'GradientBoostingClassifier'
            }
        }
        
        return jsonify({
            'models': status,
            'message': 'Model status retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting model status: {str(e)}")
        return jsonify({'error': 'Failed to get model status'}), 500

@predictions_bp.route('/models/retrain', methods=['POST'])
@jwt_required()
def retrain_models():
    """Retrain ML models (admin only)."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role.value != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        global symptom_classifier, risk_predictor
        
        # Retrain symptom classifier
        if symptom_classifier is None:
            symptom_classifier = SymptomClassifier()
        
        symptom_classifier.train()
        symptom_classifier.save_model("ml_models/nlp/trained_symptom_classifier.pkl")
        
        # Retrain risk predictor
        if risk_predictor is None:
            risk_predictor = HealthRiskPredictor()
        
        risk_predictor.train()
        risk_predictor.save_model("ml_models/numerical/trained_risk_predictor.pkl")
        
        return jsonify({
            'message': 'Models retrained successfully',
            'retrained_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retraining models: {str(e)}")
        return jsonify({'error': 'Failed to retrain models'}), 500

# Initialize models when the module is imported
initialize_models()