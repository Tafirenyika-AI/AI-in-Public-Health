from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import json

from models.user import User, UserRole, db
from models.health import HealthRecord, SymptomReport, RiskAssessment, EnvironmentalData, SeverityLevel, RiskCategory

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    """Get dashboard overview for current user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's recent data
        recent_health_records = HealthRecord.query.filter_by(user_id=current_user_id)\
            .order_by(HealthRecord.recorded_at.desc()).limit(5).all()
        
        recent_symptoms = SymptomReport.query.filter_by(user_id=current_user_id)\
            .order_by(SymptomReport.reported_at.desc()).limit(3).all()
        
        recent_assessments = RiskAssessment.query.filter_by(user_id=current_user_id)\
            .order_by(RiskAssessment.assessed_at.desc()).limit(3).all()
        
        # Calculate health metrics
        health_metrics = calculate_health_metrics(recent_health_records)
        
        # Get latest risk assessment
        latest_risk = None
        if recent_assessments:
            latest_risk = recent_assessments[0].to_dict()
        
        overview = {
            'user_info': {
                'name': f"{user.first_name} {user.last_name}",
                'age': user.age,
                'location': user.location
            },
            'health_metrics': health_metrics,
            'recent_symptoms': [symptom.to_dict() for symptom in recent_symptoms],
            'latest_risk_assessment': latest_risk,
            'total_records': len(recent_health_records),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'overview': overview,
            'message': 'Dashboard overview retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard overview: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard overview'}), 500

@dashboard_bp.route('/public-health', methods=['GET'])
@jwt_required()
def get_public_health_dashboard():
    """Get public health dashboard (for health officials)."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in [UserRole.PUBLIC_HEALTH_OFFICIAL, UserRole.ADMIN]:
            return jsonify({'error': 'Public health official access required'}), 403
        
        # Get location filter
        location = request.args.get('location')
        
        # Get time range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get aggregated data
        health_trends = get_health_trends(location, start_date)
        symptom_patterns = get_symptom_patterns(location, start_date)
        risk_distribution = get_risk_distribution(location, start_date)
        environmental_impact = get_environmental_impact(location, start_date)
        
        dashboard = {
            'health_trends': health_trends,
            'symptom_patterns': symptom_patterns,
            'risk_distribution': risk_distribution,
            'environmental_impact': environmental_impact,
            'location': location,
            'date_range': {
                'start': start_date.isoformat(),
                'end': datetime.utcnow().isoformat()
            }
        }
        
        return jsonify({
            'dashboard': dashboard,
            'message': 'Public health dashboard retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting public health dashboard: {str(e)}")
        return jsonify({'error': 'Failed to get public health dashboard'}), 500

@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_health_alerts():
    """Get health alerts for the current user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate personalized health alerts
        alerts = generate_health_alerts(user)
        
        return jsonify({
            'alerts': alerts,
            'message': 'Health alerts retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting health alerts: {str(e)}")
        return jsonify({'error': 'Failed to get health alerts'}), 500

@dashboard_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_health_trends():
    """Get health trends for the current user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get time range
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's health records
        health_records = HealthRecord.query.filter(
            and_(
                HealthRecord.user_id == current_user_id,
                HealthRecord.recorded_at >= start_date
            )
        ).order_by(HealthRecord.recorded_at).all()
        
        # Generate trends
        trends = {
            'blood_pressure': [],
            'heart_rate': [],
            'weight': [],
            'sleep_hours': [],
            'stress_level': []
        }
        
        for record in health_records:
            date_str = record.recorded_at.strftime('%Y-%m-%d')
            
            if record.blood_pressure_systolic and record.blood_pressure_diastolic:
                trends['blood_pressure'].append({
                    'date': date_str,
                    'systolic': record.blood_pressure_systolic,
                    'diastolic': record.blood_pressure_diastolic
                })
            
            if record.heart_rate:
                trends['heart_rate'].append({
                    'date': date_str,
                    'value': record.heart_rate
                })
            
            if record.weight:
                trends['weight'].append({
                    'date': date_str,
                    'value': record.weight
                })
            
            if record.sleep_hours:
                trends['sleep_hours'].append({
                    'date': date_str,
                    'value': record.sleep_hours
                })
            
            if record.stress_level:
                trends['stress_level'].append({
                    'date': date_str,
                    'value': record.stress_level
                })
        
        return jsonify({
            'trends': trends,
            'date_range': {
                'start': start_date.isoformat(),
                'end': datetime.utcnow().isoformat()
            },
            'message': 'Health trends retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting health trends: {str(e)}")
        return jsonify({'error': 'Failed to get health trends'}), 500

def calculate_health_metrics(health_records):
    """Calculate health metrics from recent health records."""
    if not health_records:
        return {}
    
    latest_record = health_records[0]
    
    metrics = {
        'latest_vitals': {
            'heart_rate': latest_record.heart_rate,
            'blood_pressure': {
                'systolic': latest_record.blood_pressure_systolic,
                'diastolic': latest_record.blood_pressure_diastolic
            },
            'temperature': latest_record.temperature,
            'weight': latest_record.weight,
            'recorded_at': latest_record.recorded_at.isoformat()
        },
        'averages': {}
    }
    
    # Calculate averages
    if len(health_records) > 1:
        heart_rates = [r.heart_rate for r in health_records if r.heart_rate]
        bp_systolic = [r.blood_pressure_systolic for r in health_records if r.blood_pressure_systolic]
        bp_diastolic = [r.blood_pressure_diastolic for r in health_records if r.blood_pressure_diastolic]
        sleep_hours = [r.sleep_hours for r in health_records if r.sleep_hours]
        stress_levels = [r.stress_level for r in health_records if r.stress_level]
        
        if heart_rates:
            metrics['averages']['heart_rate'] = round(sum(heart_rates) / len(heart_rates), 1)
        if bp_systolic:
            metrics['averages']['bp_systolic'] = round(sum(bp_systolic) / len(bp_systolic), 1)
        if bp_diastolic:
            metrics['averages']['bp_diastolic'] = round(sum(bp_diastolic) / len(bp_diastolic), 1)
        if sleep_hours:
            metrics['averages']['sleep_hours'] = round(sum(sleep_hours) / len(sleep_hours), 1)
        if stress_levels:
            metrics['averages']['stress_level'] = round(sum(stress_levels) / len(stress_levels), 1)
    
    return metrics

def get_health_trends(location, start_date):
    """Get health trends for public health dashboard."""
    # Mock implementation - in production, use actual aggregated data
    trends = {
        'total_users': 1250,
        'active_users_last_30_days': 985,
        'new_users_last_30_days': 127,
        'symptom_reports_last_30_days': 456,
        'high_risk_assessments': 89,
        'trends_by_day': [
            {'date': '2024-01-01', 'symptom_reports': 15, 'high_risk': 3},
            {'date': '2024-01-02', 'symptom_reports': 18, 'high_risk': 4},
            {'date': '2024-01-03', 'symptom_reports': 12, 'high_risk': 2}
        ]
    }
    
    return trends

def get_symptom_patterns(location, start_date):
    """Get symptom patterns for public health dashboard."""
    # Mock implementation
    patterns = {
        'most_common_symptoms': [
            {'symptom': 'headache', 'count': 124, 'percentage': 27.2},
            {'symptom': 'fatigue', 'count': 98, 'percentage': 21.5},
            {'symptom': 'cough', 'count': 87, 'percentage': 19.1},
            {'symptom': 'fever', 'count': 65, 'percentage': 14.3}
        ],
        'symptom_severity_distribution': {
            'low': 45,
            'medium': 35,
            'high': 15,
            'critical': 5
        }
    }
    
    return patterns

def get_risk_distribution(location, start_date):
    """Get risk distribution for public health dashboard."""
    # Mock implementation
    distribution = {
        'by_risk_level': {
            'low': 65,
            'medium': 25,
            'high': 8,
            'critical': 2
        },
        'by_category': {
            'cardiovascular': 35,
            'respiratory': 28,
            'diabetes': 22,
            'other': 15
        }
    }
    
    return distribution

def get_environmental_impact(location, start_date):
    """Get environmental impact data for public health dashboard."""
    # Mock implementation
    impact = {
        'air_quality_correlation': {
            'poor_air_quality_days': 8,
            'increased_respiratory_symptoms': 23,
            'correlation_coefficient': 0.67
        },
        'weather_impact': {
            'high_temperature_days': 15,
            'heat_related_symptoms': 12,
            'precipitation_days': 7,
            'allergy_symptoms': 45
        }
    }
    
    return impact

def generate_health_alerts(user):
    """Generate personalized health alerts for a user."""
    alerts = []
    
    # Get user's recent data
    recent_records = HealthRecord.query.filter_by(user_id=user.id)\
        .order_by(HealthRecord.recorded_at.desc()).limit(5).all()
    
    recent_assessments = RiskAssessment.query.filter_by(user_id=user.id)\
        .order_by(RiskAssessment.assessed_at.desc()).limit(3).all()
    
    # Check for health concerns
    if recent_records:
        latest_record = recent_records[0]
        
        # Blood pressure alert
        if (latest_record.blood_pressure_systolic and 
            latest_record.blood_pressure_systolic > 140):
            alerts.append({
                'type': 'health_metric',
                'severity': 'high',
                'title': 'High Blood Pressure Detected',
                'message': f'Your latest blood pressure reading ({latest_record.blood_pressure_systolic}/{latest_record.blood_pressure_diastolic}) is elevated.',
                'recommendations': [
                    'Monitor blood pressure daily',
                    'Consult your healthcare provider',
                    'Reduce sodium intake'
                ]
            })
        
        # Heart rate alert
        if latest_record.heart_rate and latest_record.heart_rate > 100:
            alerts.append({
                'type': 'health_metric',
                'severity': 'medium',
                'title': 'Elevated Heart Rate',
                'message': f'Your latest heart rate ({latest_record.heart_rate} bpm) is higher than normal.',
                'recommendations': [
                    'Monitor heart rate throughout the day',
                    'Consider stress management techniques',
                    'Consult healthcare provider if persists'
                ]
            })
        
        # Sleep alert
        if latest_record.sleep_hours and latest_record.sleep_hours < 6:
            alerts.append({
                'type': 'lifestyle',
                'severity': 'medium',
                'title': 'Insufficient Sleep',
                'message': f'You\'re only getting {latest_record.sleep_hours} hours of sleep per night.',
                'recommendations': [
                    'Aim for 7-8 hours of sleep',
                    'Establish a regular sleep schedule',
                    'Limit screen time before bed'
                ]
            })
    
    # Check risk assessments
    if recent_assessments:
        latest_assessment = recent_assessments[0]
        if latest_assessment.risk_level == SeverityLevel.HIGH:
            alerts.append({
                'type': 'risk_assessment',
                'severity': 'high',
                'title': 'High Health Risk Detected',
                'message': f'Your latest risk assessment shows high risk for {latest_assessment.predicted_condition}.',
                'recommendations': latest_assessment.get_recommendations()
            })
    
    # Add general health reminders
    if len(alerts) == 0:
        alerts.append({
            'type': 'reminder',
            'severity': 'info',
            'title': 'Health Check Reminder',
            'message': 'It\'s time for your regular health check-up.',
            'recommendations': [
                'Log your daily symptoms',
                'Record your vital signs',
                'Maintain a healthy lifestyle'
            ]
        })
    
    return alerts

@dashboard_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_user_statistics():
    """Get user's health statistics."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's statistics
        stats = {
            'total_health_records': HealthRecord.query.filter_by(user_id=current_user_id).count(),
            'total_symptom_reports': SymptomReport.query.filter_by(user_id=current_user_id).count(),
            'total_risk_assessments': RiskAssessment.query.filter_by(user_id=current_user_id).count(),
            'account_created': user.created_at.isoformat(),
            'last_activity': user.last_login.isoformat() if user.last_login else None
        }
        
        return jsonify({
            'statistics': stats,
            'message': 'User statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user statistics: {str(e)}")
        return jsonify({'error': 'Failed to get user statistics'}), 500