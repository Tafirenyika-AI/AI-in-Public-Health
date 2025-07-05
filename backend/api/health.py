from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
import json

from models.user import User, db
from models.health import HealthRecord, SymptomReport, SeverityLevel

health_bp = Blueprint('health', __name__)

@health_bp.route('/records', methods=['GET'])
@jwt_required()
def get_health_records():
    """Get user's health records."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query health records
        records = HealthRecord.query.filter_by(user_id=current_user_id)\
            .order_by(HealthRecord.recorded_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'records': [record.to_dict() for record in records],
            'total': len(records)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching health records: {str(e)}")
        return jsonify({'error': 'Failed to fetch health records'}), 500

@health_bp.route('/records', methods=['POST'])
@jwt_required()
def create_health_record():
    """Create a new health record."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Create health record
        health_record = HealthRecord(
            user_id=current_user_id,
            heart_rate=data.get('heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            temperature=data.get('temperature'),
            weight=data.get('weight'),
            height=data.get('height'),
            sleep_hours=data.get('sleep_hours'),
            exercise_minutes=data.get('exercise_minutes'),
            stress_level=data.get('stress_level'),
            recorded_at=datetime.utcnow()
        )
        
        # Set dietary data if provided
        if 'dietary_data' in data:
            health_record.set_dietary_data(data['dietary_data'])
        
        # Set medications if provided
        if 'medications' in data:
            health_record.set_medications(data['medications'])
        
        db.session.add(health_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Health record created successfully',
            'record': health_record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating health record: {str(e)}")
        return jsonify({'error': 'Failed to create health record'}), 500

@health_bp.route('/records/<int:record_id>', methods=['GET'])
@jwt_required()
def get_health_record(record_id):
    """Get a specific health record."""
    try:
        current_user_id = get_jwt_identity()
        
        record = HealthRecord.query.filter_by(
            id=record_id, 
            user_id=current_user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Health record not found'}), 404
        
        return jsonify({
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching health record: {str(e)}")
        return jsonify({'error': 'Failed to fetch health record'}), 500

@health_bp.route('/records/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_health_record(record_id):
    """Update a health record."""
    try:
        current_user_id = get_jwt_identity()
        
        record = HealthRecord.query.filter_by(
            id=record_id, 
            user_id=current_user_id
        ).first()
        
        if not record:
            return jsonify({'error': 'Health record not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        updatable_fields = [
            'heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'temperature', 'weight', 'height', 'sleep_hours', 'exercise_minutes',
            'stress_level'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(record, field, data[field])
        
        # Update dietary data if provided
        if 'dietary_data' in data:
            record.set_dietary_data(data['dietary_data'])
        
        # Update medications if provided
        if 'medications' in data:
            record.set_medications(data['medications'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Health record updated successfully',
            'record': record.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating health record: {str(e)}")
        return jsonify({'error': 'Failed to update health record'}), 500

@health_bp.route('/symptoms', methods=['GET'])
@jwt_required()
def get_symptom_reports():
    """Get user's symptom reports."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query symptom reports
        reports = SymptomReport.query.filter_by(user_id=current_user_id)\
            .order_by(SymptomReport.reported_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports],
            'total': len(reports)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching symptom reports: {str(e)}")
        return jsonify({'error': 'Failed to fetch symptom reports'}), 500

@health_bp.route('/symptoms', methods=['POST'])
@jwt_required()
def create_symptom_report():
    """Create a new symptom report."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('symptom_text'):
            return jsonify({'error': 'Symptom text is required'}), 400
        
        if not data.get('severity'):
            return jsonify({'error': 'Severity is required'}), 400
        
        # Validate severity level
        try:
            severity = SeverityLevel(data['severity'])
        except ValueError:
            return jsonify({'error': 'Invalid severity level'}), 400
        
        # Parse onset date if provided
        onset_date = None
        if data.get('onset_date'):
            try:
                onset_date = datetime.strptime(data['onset_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid onset date format. Use YYYY-MM-DD'}), 400
        
        # Create symptom report
        symptom_report = SymptomReport(
            user_id=current_user_id,
            symptom_text=data['symptom_text'],
            severity=severity,
            onset_date=onset_date,
            duration_days=data.get('duration_days'),
            location=data.get('location'),
            air_quality_index=data.get('air_quality_index'),
            reported_at=datetime.utcnow()
        )
        
        # Set weather conditions if provided
        if 'weather_conditions' in data:
            symptom_report.set_weather_conditions(data['weather_conditions'])
        
        db.session.add(symptom_report)
        db.session.commit()
        
        return jsonify({
            'message': 'Symptom report created successfully',
            'report': symptom_report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating symptom report: {str(e)}")
        return jsonify({'error': 'Failed to create symptom report'}), 500

@health_bp.route('/symptoms/<int:report_id>', methods=['GET'])
@jwt_required()
def get_symptom_report(report_id):
    """Get a specific symptom report."""
    try:
        current_user_id = get_jwt_identity()
        
        report = SymptomReport.query.filter_by(
            id=report_id, 
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Symptom report not found'}), 404
        
        return jsonify({
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching symptom report: {str(e)}")
        return jsonify({'error': 'Failed to fetch symptom report'}), 500

@health_bp.route('/symptoms/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_symptom_report(report_id):
    """Update a symptom report."""
    try:
        current_user_id = get_jwt_identity()
        
        report = SymptomReport.query.filter_by(
            id=report_id, 
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Symptom report not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'symptom_text' in data:
            report.symptom_text = data['symptom_text']
        
        if 'severity' in data:
            try:
                report.severity = SeverityLevel(data['severity'])
            except ValueError:
                return jsonify({'error': 'Invalid severity level'}), 400
        
        if 'onset_date' in data:
            try:
                report.onset_date = datetime.strptime(data['onset_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid onset date format. Use YYYY-MM-DD'}), 400
        
        if 'duration_days' in data:
            report.duration_days = data['duration_days']
        
        if 'location' in data:
            report.location = data['location']
        
        if 'air_quality_index' in data:
            report.air_quality_index = data['air_quality_index']
        
        # Update weather conditions if provided
        if 'weather_conditions' in data:
            report.set_weather_conditions(data['weather_conditions'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Symptom report updated successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating symptom report: {str(e)}")
        return jsonify({'error': 'Failed to update symptom report'}), 500

@health_bp.route('/symptoms/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_symptom_report(report_id):
    """Delete a symptom report."""
    try:
        current_user_id = get_jwt_identity()
        
        report = SymptomReport.query.filter_by(
            id=report_id, 
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Symptom report not found'}), 404
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Symptom report deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting symptom report: {str(e)}")
        return jsonify({'error': 'Failed to delete symptom report'}), 500

@health_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_health_summary():
    """Get user's health summary."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent health records
        recent_records = HealthRecord.query.filter_by(user_id=current_user_id)\
            .order_by(HealthRecord.recorded_at.desc()).limit(5).all()
        
        # Get recent symptom reports
        recent_symptoms = SymptomReport.query.filter_by(user_id=current_user_id)\
            .order_by(SymptomReport.reported_at.desc()).limit(5).all()
        
        # Calculate basic statistics
        total_records = HealthRecord.query.filter_by(user_id=current_user_id).count()
        total_symptoms = SymptomReport.query.filter_by(user_id=current_user_id).count()
        
        # Get latest vitals
        latest_vitals = {}
        if recent_records:
            latest_record = recent_records[0]
            latest_vitals = {
                'heart_rate': latest_record.heart_rate,
                'blood_pressure_systolic': latest_record.blood_pressure_systolic,
                'blood_pressure_diastolic': latest_record.blood_pressure_diastolic,
                'temperature': latest_record.temperature,
                'weight': latest_record.weight,
                'recorded_at': latest_record.recorded_at.isoformat()
            }
        
        return jsonify({
            'summary': {
                'total_records': total_records,
                'total_symptoms': total_symptoms,
                'latest_vitals': latest_vitals,
                'recent_records': [record.to_dict() for record in recent_records],
                'recent_symptoms': [symptom.to_dict() for symptom in recent_symptoms]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching health summary: {str(e)}")
        return jsonify({'error': 'Failed to fetch health summary'}), 500