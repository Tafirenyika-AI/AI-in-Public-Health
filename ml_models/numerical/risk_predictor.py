import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.impute import SimpleImputer
import joblib
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class HealthRiskPredictor:
    """Numerical risk predictor for health monitoring using structured data."""
    
    def __init__(self, model_path: str = None):
        """Initialize the risk predictor."""
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.label_encoder = LabelEncoder()
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        self.is_trained = False
        self.model_path = model_path
        self.feature_names = []
        
        # Risk categories and thresholds
        self.risk_categories = {
            'cardiovascular': {
                'features': ['age', 'bp_systolic', 'bp_diastolic', 'heart_rate', 
                           'cholesterol', 'bmi', 'smoking', 'family_history_cvd'],
                'high_risk_threshold': 0.7
            },
            'diabetes': {
                'features': ['age', 'bmi', 'glucose', 'family_history_diabetes', 
                           'physical_activity', 'diet_score'],
                'high_risk_threshold': 0.6
            },
            'hypertension': {
                'features': ['age', 'bp_systolic', 'bp_diastolic', 'bmi', 'salt_intake', 
                           'stress_level', 'family_history_hypertension'],
                'high_risk_threshold': 0.65
            },
            'respiratory': {
                'features': ['age', 'smoking', 'air_quality', 'allergies', 
                           'respiratory_infections', 'lung_function'],
                'high_risk_threshold': 0.6
            }
        }
        
        # Load pre-trained model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model()
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic health data for training."""
        np.random.seed(42)
        
        data = []
        for _ in range(n_samples):
            # Demographics
            age = np.random.randint(18, 80)
            gender = np.random.choice(['male', 'female'])
            
            # Vitals
            bp_systolic = np.random.normal(120, 20)
            bp_diastolic = np.random.normal(80, 10)
            heart_rate = np.random.normal(70, 15)
            temperature = np.random.normal(98.6, 1)
            
            # Physical measurements
            height = np.random.normal(170, 10)  # cm
            weight = np.random.normal(70, 15)   # kg
            bmi = weight / ((height / 100) ** 2)
            
            # Lab values
            glucose = np.random.normal(90, 20)
            cholesterol = np.random.normal(200, 40)
            
            # Lifestyle factors
            smoking = np.random.choice([0, 1], p=[0.7, 0.3])
            alcohol_consumption = np.random.randint(0, 7)  # drinks per week
            physical_activity = np.random.randint(0, 10)   # hours per week
            sleep_hours = np.random.normal(7, 1.5)
            stress_level = np.random.randint(1, 11)        # 1-10 scale
            
            # Environmental factors
            air_quality = np.random.randint(0, 300)        # AQI
            pollen_count = np.random.randint(0, 100)
            
            # Family history
            family_history_cvd = np.random.choice([0, 1], p=[0.8, 0.2])
            family_history_diabetes = np.random.choice([0, 1], p=[0.85, 0.15])
            family_history_hypertension = np.random.choice([0, 1], p=[0.7, 0.3])
            
            # Diet and other factors
            diet_score = np.random.randint(1, 11)          # 1-10 scale
            salt_intake = np.random.normal(2300, 500)      # mg per day
            
            # Medical history
            allergies = np.random.choice([0, 1], p=[0.8, 0.2])
            respiratory_infections = np.random.randint(0, 5)  # last year
            lung_function = np.random.normal(100, 15)         # % of normal
            
            # Calculate risk factors based on values
            # Cardiovascular risk
            cv_risk_score = 0
            if age > 45:
                cv_risk_score += 0.2
            if bp_systolic > 140 or bp_diastolic > 90:
                cv_risk_score += 0.3
            if cholesterol > 240:
                cv_risk_score += 0.2
            if bmi > 30:
                cv_risk_score += 0.1
            if smoking:
                cv_risk_score += 0.3
            if family_history_cvd:
                cv_risk_score += 0.2
            
            # Diabetes risk
            diabetes_risk_score = 0
            if age > 45:
                diabetes_risk_score += 0.2
            if bmi > 25:
                diabetes_risk_score += 0.2
            if glucose > 100:
                diabetes_risk_score += 0.3
            if family_history_diabetes:
                diabetes_risk_score += 0.3
            if physical_activity < 3:
                diabetes_risk_score += 0.1
            
            # Determine overall risk category
            max_risk = max(cv_risk_score, diabetes_risk_score)
            if max_risk > 0.7:
                risk_category = 'high'
            elif max_risk > 0.4:
                risk_category = 'medium'
            else:
                risk_category = 'low'
            
            data.append({
                'age': age,
                'gender': gender,
                'bp_systolic': bp_systolic,
                'bp_diastolic': bp_diastolic,
                'heart_rate': heart_rate,
                'temperature': temperature,
                'height': height,
                'weight': weight,
                'bmi': bmi,
                'glucose': glucose,
                'cholesterol': cholesterol,
                'smoking': smoking,
                'alcohol_consumption': alcohol_consumption,
                'physical_activity': physical_activity,
                'sleep_hours': sleep_hours,
                'stress_level': stress_level,
                'air_quality': air_quality,
                'pollen_count': pollen_count,
                'family_history_cvd': family_history_cvd,
                'family_history_diabetes': family_history_diabetes,
                'family_history_hypertension': family_history_hypertension,
                'diet_score': diet_score,
                'salt_intake': salt_intake,
                'allergies': allergies,
                'respiratory_infections': respiratory_infections,
                'lung_function': lung_function,
                'risk_category': risk_category,
                'cv_risk_score': cv_risk_score,
                'diabetes_risk_score': diabetes_risk_score
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training or prediction."""
        # Select numerical features
        numerical_features = [
            'age', 'bp_systolic', 'bp_diastolic', 'heart_rate', 'temperature',
            'height', 'weight', 'bmi', 'glucose', 'cholesterol', 'smoking',
            'alcohol_consumption', 'physical_activity', 'sleep_hours', 'stress_level',
            'air_quality', 'pollen_count', 'family_history_cvd', 'family_history_diabetes',
            'family_history_hypertension', 'diet_score', 'salt_intake', 'allergies',
            'respiratory_infections', 'lung_function'
        ]
        
        # Handle categorical variables
        df_processed = df.copy()
        if 'gender' in df_processed.columns:
            df_processed['gender_male'] = (df_processed['gender'] == 'male').astype(int)
            df_processed['gender_female'] = (df_processed['gender'] == 'female').astype(int)
            numerical_features.extend(['gender_male', 'gender_female'])
        
        # Select only available features
        available_features = [f for f in numerical_features if f in df_processed.columns]
        self.feature_names = available_features
        
        return df_processed[available_features]
    
    def train(self, X_train: pd.DataFrame = None, y_train: pd.Series = None):
        """Train the risk prediction model."""
        if X_train is None or y_train is None:
            # Generate synthetic data if no training data provided
            df = self.generate_synthetic_data(2000)
            X_train = self.prepare_features(df)
            y_train = df['risk_category']
        
        # Handle missing values
        X_train_imputed = self.imputer.fit_transform(X_train)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_imputed)
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        # Split data for validation
        X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
            X_train_scaled, y_train_encoded, test_size=0.2, random_state=42, stratify=y_train_encoded
        )
        
        # Train model
        self.model.fit(X_train_split, y_train_split)
        self.is_trained = True
        
        # Evaluate model
        y_pred = self.model.predict(X_val_split)
        accuracy = accuracy_score(y_val_split, y_pred)
        
        # Calculate AUC for binary classification (high risk vs others)
        y_val_binary = (y_val_split == 2).astype(int)  # Assuming 'high' is encoded as 2
        y_pred_proba = self.model.predict_proba(X_val_split)[:, 2] if len(self.model.classes_) > 2 else self.model.predict_proba(X_val_split)[:, 1]
        auc_score = roc_auc_score(y_val_binary, y_pred_proba)
        
        print("Training completed successfully!")
        print(f"Validation accuracy: {accuracy:.3f}")
        print(f"AUC score (high risk): {auc_score:.3f}")
        
        return accuracy, auc_score
    
    def predict(self, features: Dict) -> Dict:
        """Predict health risk from features."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Convert features to DataFrame
        df = pd.DataFrame([features])
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Handle missing values
        X_imputed = self.imputer.transform(X)
        
        # Scale features
        X_scaled = self.scaler.transform(X_imputed)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get prediction details
        risk_category = self.label_encoder.inverse_transform([prediction])[0]
        confidence = np.max(probabilities)
        
        # Calculate specific risk scores
        risk_scores = self.calculate_specific_risks(features)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(features, risk_scores)
        
        return {
            'overall_risk': risk_category,
            'confidence': float(confidence),
            'risk_scores': risk_scores,
            'recommendations': recommendations,
            'all_probabilities': {
                category: float(prob) for category, prob in 
                zip(self.label_encoder.classes_, probabilities)
            }
        }
    
    def calculate_specific_risks(self, features: Dict) -> Dict:
        """Calculate specific risk scores for different conditions."""
        risk_scores = {}
        
        # Cardiovascular risk
        cv_score = 0
        if features.get('age', 0) > 45:
            cv_score += 0.2
        if features.get('bp_systolic', 0) > 140:
            cv_score += 0.3
        if features.get('cholesterol', 0) > 240:
            cv_score += 0.2
        if features.get('bmi', 0) > 30:
            cv_score += 0.1
        if features.get('smoking', 0):
            cv_score += 0.3
        if features.get('family_history_cvd', 0):
            cv_score += 0.2
        risk_scores['cardiovascular'] = min(cv_score, 1.0)
        
        # Diabetes risk
        diabetes_score = 0
        if features.get('age', 0) > 45:
            diabetes_score += 0.2
        if features.get('bmi', 0) > 25:
            diabetes_score += 0.2
        if features.get('glucose', 0) > 100:
            diabetes_score += 0.3
        if features.get('family_history_diabetes', 0):
            diabetes_score += 0.3
        risk_scores['diabetes'] = min(diabetes_score, 1.0)
        
        # Hypertension risk
        hypertension_score = 0
        if features.get('bp_systolic', 0) > 130:
            hypertension_score += 0.4
        if features.get('bp_diastolic', 0) > 85:
            hypertension_score += 0.3
        if features.get('salt_intake', 0) > 2300:
            hypertension_score += 0.2
        if features.get('stress_level', 0) > 7:
            hypertension_score += 0.1
        risk_scores['hypertension'] = min(hypertension_score, 1.0)
        
        # Respiratory risk
        respiratory_score = 0
        if features.get('smoking', 0):
            respiratory_score += 0.4
        if features.get('air_quality', 0) > 100:
            respiratory_score += 0.3
        if features.get('allergies', 0):
            respiratory_score += 0.2
        if features.get('respiratory_infections', 0) > 2:
            respiratory_score += 0.1
        risk_scores['respiratory'] = min(respiratory_score, 1.0)
        
        return risk_scores
    
    def generate_recommendations(self, features: Dict, risk_scores: Dict) -> List[str]:
        """Generate personalized health recommendations."""
        recommendations = []
        
        # Cardiovascular recommendations
        if risk_scores.get('cardiovascular', 0) > 0.5:
            recommendations.append("Consider cardiovascular screening with your doctor")
            if features.get('smoking', 0):
                recommendations.append("Quit smoking to reduce cardiovascular risk")
            if features.get('bp_systolic', 0) > 140:
                recommendations.append("Monitor blood pressure regularly")
            if features.get('cholesterol', 0) > 240:
                recommendations.append("Consider cholesterol management")
        
        # Diabetes recommendations
        if risk_scores.get('diabetes', 0) > 0.5:
            recommendations.append("Consider diabetes screening")
            if features.get('bmi', 0) > 25:
                recommendations.append("Consider weight management")
            if features.get('physical_activity', 0) < 3:
                recommendations.append("Increase physical activity")
        
        # Hypertension recommendations
        if risk_scores.get('hypertension', 0) > 0.5:
            recommendations.append("Monitor blood pressure regularly")
            if features.get('salt_intake', 0) > 2300:
                recommendations.append("Reduce sodium intake")
            if features.get('stress_level', 0) > 7:
                recommendations.append("Consider stress management techniques")
        
        # Respiratory recommendations
        if risk_scores.get('respiratory', 0) > 0.5:
            recommendations.append("Consider respiratory health assessment")
            if features.get('air_quality', 0) > 100:
                recommendations.append("Limit outdoor activities during poor air quality")
            if features.get('allergies', 0):
                recommendations.append("Manage allergies with appropriate treatment")
        
        # General recommendations
        if features.get('sleep_hours', 0) < 6:
            recommendations.append("Aim for 7-8 hours of sleep per night")
        
        if not recommendations:
            recommendations.append("Continue maintaining healthy lifestyle habits")
        
        return recommendations
    
    def save_model(self, path: str = None):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        if path is None:
            path = self.model_path or 'risk_predictor.pkl'
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'imputer': self.imputer,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        joblib.dump(model_data, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str = None):
        """Load a trained model."""
        if path is None:
            path = self.model_path
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.imputer = model_data['imputer']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {path}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize predictor
    predictor = HealthRiskPredictor()
    
    # Train the model
    print("Training risk prediction model...")
    accuracy, auc = predictor.train()
    
    # Test predictions
    test_cases = [
        {
            'age': 55,
            'gender': 'male',
            'bp_systolic': 150,
            'bp_diastolic': 95,
            'heart_rate': 80,
            'bmi': 28,
            'glucose': 110,
            'cholesterol': 250,
            'smoking': 1,
            'physical_activity': 2,
            'stress_level': 8,
            'family_history_cvd': 1,
            'family_history_diabetes': 0
        },
        {
            'age': 30,
            'gender': 'female',
            'bp_systolic': 115,
            'bp_diastolic': 75,
            'heart_rate': 65,
            'bmi': 22,
            'glucose': 85,
            'cholesterol': 180,
            'smoking': 0,
            'physical_activity': 5,
            'stress_level': 3,
            'family_history_cvd': 0,
            'family_history_diabetes': 0
        }
    ]
    
    print("\nTesting predictions:")
    for i, case in enumerate(test_cases):
        result = predictor.predict(case)
        print(f"\nCase {i+1}:")
        print(f"Overall risk: {result['overall_risk']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Risk scores: {result['risk_scores']}")
        print(f"Recommendations: {result['recommendations']}")
    
    # Save the model
    model_path = "ml_models/numerical/trained_risk_predictor.pkl"
    predictor.save_model(model_path)