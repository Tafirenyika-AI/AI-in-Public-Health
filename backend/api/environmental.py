from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import requests
import json

from models.health import EnvironmentalData, db

environmental_bp = Blueprint('environmental', __name__)

@environmental_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_environmental_data():
    """Get current environmental data for user's location."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get location from query parameters
        location = request.args.get('location')
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not location and not (latitude and longitude):
            return jsonify({'error': 'Location or coordinates required'}), 400
        
        # Fetch environmental data
        env_data = fetch_environmental_data(location, latitude, longitude)
        
        return jsonify({
            'environmental_data': env_data,
            'message': 'Environmental data retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching environmental data: {str(e)}")
        return jsonify({'error': 'Failed to fetch environmental data'}), 500

@environmental_bp.route('/history', methods=['GET'])
@jwt_required()
def get_environmental_history():
    """Get historical environmental data."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        location = request.args.get('location')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query environmental data
        query = EnvironmentalData.query
        
        if location:
            query = query.filter(EnvironmentalData.location.ilike(f'%{location}%'))
        
        env_data = query.order_by(EnvironmentalData.recorded_at.desc())\
            .limit(limit).offset(offset).all()
        
        return jsonify({
            'environmental_data': [data.to_dict() for data in env_data],
            'total': len(env_data)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching environmental history: {str(e)}")
        return jsonify({'error': 'Failed to fetch environmental history'}), 500

@environmental_bp.route('/air-quality', methods=['GET'])
@jwt_required()
def get_air_quality():
    """Get air quality data for a specific location."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get location from query parameters
        location = request.args.get('location')
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not location and not (latitude and longitude):
            return jsonify({'error': 'Location or coordinates required'}), 400
        
        # Fetch air quality data (mock implementation)
        air_quality = fetch_air_quality_data(location, latitude, longitude)
        
        return jsonify({
            'air_quality': air_quality,
            'message': 'Air quality data retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching air quality data: {str(e)}")
        return jsonify({'error': 'Failed to fetch air quality data'}), 500

@environmental_bp.route('/weather', methods=['GET'])
@jwt_required()
def get_weather_data():
    """Get weather data for a specific location."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get location from query parameters
        location = request.args.get('location')
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lon', type=float)
        
        if not location and not (latitude and longitude):
            return jsonify({'error': 'Location or coordinates required'}), 400
        
        # Fetch weather data (mock implementation)
        weather = fetch_weather_data(location, latitude, longitude)
        
        return jsonify({
            'weather': weather,
            'message': 'Weather data retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

@environmental_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_environmental_alerts():
    """Get environmental health alerts for a location."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get location from query parameters
        location = request.args.get('location')
        
        if not location:
            return jsonify({'error': 'Location required'}), 400
        
        # Generate mock environmental alerts
        alerts = generate_environmental_alerts(location)
        
        return jsonify({
            'alerts': alerts,
            'location': location,
            'message': 'Environmental alerts retrieved successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching environmental alerts: {str(e)}")
        return jsonify({'error': 'Failed to fetch environmental alerts'}), 500

def fetch_environmental_data(location, latitude=None, longitude=None):
    """Fetch environmental data from external APIs."""
    try:
        # Mock environmental data (in production, use real APIs)
        env_data = {
            'location': location or f"{latitude},{longitude}",
            'air_quality_index': 85,  # Mock AQI
            'pm25': 12.5,
            'pm10': 18.3,
            'co2': 410,
            'pollen_count': 45,
            'temperature': 22.5,
            'humidity': 65,
            'pressure': 1013.25,
            'wind_speed': 5.2,
            'uv_index': 6,
            'recorded_at': datetime.utcnow().isoformat()
        }
        
        # Save to database
        env_record = EnvironmentalData(
            location=env_data['location'],
            latitude=latitude,
            longitude=longitude,
            air_quality_index=env_data['air_quality_index'],
            pm25=env_data['pm25'],
            pm10=env_data['pm10'],
            co2=env_data['co2'],
            pollen_count=env_data['pollen_count'],
            temperature=env_data['temperature'],
            humidity=env_data['humidity'],
            pressure=env_data['pressure'],
            wind_speed=env_data['wind_speed'],
            recorded_at=datetime.utcnow()
        )
        
        db.session.add(env_record)
        db.session.commit()
        
        return env_data
        
    except Exception as e:
        current_app.logger.error(f"Error fetching environmental data: {str(e)}")
        # Return mock data even if database save fails
        return {
            'location': location or f"{latitude},{longitude}",
            'air_quality_index': 85,
            'pm25': 12.5,
            'pm10': 18.3,
            'temperature': 22.5,
            'humidity': 65,
            'error': 'Using mock data'
        }

def fetch_air_quality_data(location, latitude=None, longitude=None):
    """Fetch air quality data from external APIs."""
    try:
        # Mock air quality data
        air_quality = {
            'aqi': 85,
            'pm25': 12.5,
            'pm10': 18.3,
            'co': 0.5,
            'no2': 15.2,
            'o3': 45.8,
            'so2': 2.1,
            'status': 'Moderate',
            'health_message': 'Air quality is acceptable for most people.',
            'recommendations': [
                'Sensitive individuals should limit outdoor activities',
                'Consider wearing a mask if you have respiratory conditions'
            ]
        }
        
        # Add health risk assessment based on AQI
        if air_quality['aqi'] > 150:
            air_quality['health_risk'] = 'High'
            air_quality['recommendations'].append('Avoid outdoor activities')
        elif air_quality['aqi'] > 100:
            air_quality['health_risk'] = 'Moderate'
            air_quality['recommendations'].append('Limit prolonged outdoor activities')
        else:
            air_quality['health_risk'] = 'Low'
            air_quality['recommendations'] = ['Air quality is good for outdoor activities']
        
        return air_quality
        
    except Exception as e:
        current_app.logger.error(f"Error fetching air quality data: {str(e)}")
        return {
            'aqi': 85,
            'status': 'Moderate',
            'health_risk': 'Moderate',
            'error': 'Using mock data'
        }

def fetch_weather_data(location, latitude=None, longitude=None):
    """Fetch weather data from external APIs."""
    try:
        # Mock weather data
        weather = {
            'temperature': 22.5,
            'feels_like': 24.1,
            'humidity': 65,
            'pressure': 1013.25,
            'wind_speed': 5.2,
            'wind_direction': 'SW',
            'visibility': 10,
            'uv_index': 6,
            'condition': 'Partly Cloudy',
            'forecast': [
                {
                    'day': 'Today',
                    'high': 25,
                    'low': 18,
                    'condition': 'Sunny',
                    'precipitation': 0
                },
                {
                    'day': 'Tomorrow',
                    'high': 23,
                    'low': 16,
                    'condition': 'Cloudy',
                    'precipitation': 10
                }
            ]
        }
        
        # Add health-related weather alerts
        weather['health_alerts'] = []
        
        if weather['temperature'] > 35:
            weather['health_alerts'].append('Heat warning - stay hydrated and avoid prolonged sun exposure')
        
        if weather['uv_index'] > 8:
            weather['health_alerts'].append('High UV index - use sunscreen and wear protective clothing')
        
        if weather['humidity'] > 80:
            weather['health_alerts'].append('High humidity - may affect those with respiratory conditions')
        
        return weather
        
    except Exception as e:
        current_app.logger.error(f"Error fetching weather data: {str(e)}")
        return {
            'temperature': 22.5,
            'condition': 'Partly Cloudy',
            'error': 'Using mock data'
        }

def generate_environmental_alerts(location):
    """Generate environmental health alerts for a location."""
    try:
        # Mock environmental alerts
        alerts = [
            {
                'type': 'air_quality',
                'severity': 'moderate',
                'title': 'Moderate Air Quality',
                'message': 'Air quality is acceptable for most people. Sensitive individuals should limit outdoor activities.',
                'recommendations': [
                    'Limit outdoor activities if you have respiratory conditions',
                    'Consider wearing a mask during outdoor activities'
                ],
                'expires_at': (datetime.utcnow()).isoformat()
            },
            {
                'type': 'pollen',
                'severity': 'high',
                'title': 'High Pollen Count',
                'message': 'Pollen levels are high. Those with allergies should take precautions.',
                'recommendations': [
                    'Take allergy medications as prescribed',
                    'Keep windows closed',
                    'Shower after outdoor activities'
                ],
                'expires_at': (datetime.utcnow()).isoformat()
            }
        ]
        
        return alerts
        
    except Exception as e:
        current_app.logger.error(f"Error generating environmental alerts: {str(e)}")
        return []

@environmental_bp.route('/report', methods=['POST'])
@jwt_required()
def report_environmental_issue():
    """Allow users to report environmental issues."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('location') or not data.get('issue_type'):
            return jsonify({'error': 'Location and issue type are required'}), 400
        
        # Create environmental report (mock implementation)
        report = {
            'id': 12345,  # Mock ID
            'user_id': current_user_id,
            'location': data['location'],
            'issue_type': data['issue_type'],
            'description': data.get('description', ''),
            'severity': data.get('severity', 'medium'),
            'reported_at': datetime.utcnow().isoformat(),
            'status': 'submitted'
        }
        
        return jsonify({
            'report': report,
            'message': 'Environmental issue reported successfully'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error reporting environmental issue: {str(e)}")
        return jsonify({'error': 'Failed to report environmental issue'}), 500