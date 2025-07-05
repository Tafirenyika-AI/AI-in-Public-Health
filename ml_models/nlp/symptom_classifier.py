import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import spacy
import re
from typing import List, Dict, Tuple
import os

class SymptomClassifier:
    """NLP-based symptom classifier for health monitoring."""
    
    def __init__(self, model_path: str = None):
        """Initialize the symptom classifier."""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.model_path = model_path
        
        # Load spaCy model for text preprocessing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Using basic preprocessing.")
            self.nlp = None
        
        # Symptom categories mapping
        self.symptom_categories = {
            'respiratory': ['cough', 'shortness of breath', 'chest pain', 'wheezing', 
                           'sore throat', 'runny nose', 'congestion', 'sneezing'],
            'gastrointestinal': ['nausea', 'vomiting', 'diarrhea', 'constipation', 
                               'abdominal pain', 'bloating', 'heartburn', 'loss of appetite'],
            'neurological': ['headache', 'dizziness', 'confusion', 'memory loss', 
                           'seizures', 'numbness', 'tingling', 'weakness'],
            'cardiovascular': ['chest pain', 'palpitations', 'irregular heartbeat', 
                             'swelling', 'shortness of breath', 'fainting'],
            'musculoskeletal': ['joint pain', 'muscle aches', 'back pain', 
                              'stiffness', 'swelling', 'limited mobility'],
            'dermatological': ['rash', 'itching', 'skin changes', 'bruising', 
                             'hair loss', 'nail changes'],
            'systemic': ['fever', 'chills', 'fatigue', 'weight loss', 'weight gain', 
                        'night sweats', 'general malaise']
        }
        
        # Load pre-trained model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess symptom text."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Use spaCy for advanced preprocessing if available
        if self.nlp:
            doc = self.nlp(text)
            tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
            text = ' '.join(tokens)
        
        return text
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract individual symptoms from text."""
        text = self.preprocess_text(text)
        
        # Split by common separators
        symptoms = []
        for separator in [',', ';', ' and ', ' or ', '\n']:
            if separator in text:
                symptoms.extend(text.split(separator))
                break
        else:
            symptoms = [text]
        
        # Clean and filter symptoms
        cleaned_symptoms = []
        for symptom in symptoms:
            symptom = symptom.strip()
            if symptom and len(symptom) > 2:
                cleaned_symptoms.append(symptom)
        
        return cleaned_symptoms
    
    def categorize_symptoms(self, symptoms: List[str]) -> Dict[str, List[str]]:
        """Categorize symptoms into body systems."""
        categorized = {category: [] for category in self.symptom_categories.keys()}
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for category, keywords in self.symptom_categories.items():
                if any(keyword in symptom_lower for keyword in keywords):
                    categorized[category].append(symptom)
                    break
            else:
                # If no category found, add to 'other'
                if 'other' not in categorized:
                    categorized['other'] = []
                categorized['other'].append(symptom)
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        return categorized
    
    def create_training_data(self) -> pd.DataFrame:
        """Create synthetic training data for symptom classification."""
        # This is a simplified version - in production, you'd use real medical data
        training_data = []
        
        # Generate synthetic symptom-disease pairs
        diseases = {
            'common_cold': ['runny nose', 'sore throat', 'cough', 'sneezing', 'congestion'],
            'flu': ['fever', 'body aches', 'fatigue', 'cough', 'headache'],
            'covid19': ['fever', 'cough', 'shortness of breath', 'loss of taste', 'fatigue'],
            'allergies': ['sneezing', 'runny nose', 'itchy eyes', 'congestion'],
            'migraine': ['severe headache', 'nausea', 'sensitivity to light', 'dizziness'],
            'gastroenteritis': ['nausea', 'vomiting', 'diarrhea', 'abdominal pain'],
            'anxiety': ['rapid heartbeat', 'shortness of breath', 'sweating', 'nervousness'],
            'depression': ['fatigue', 'loss of appetite', 'difficulty concentrating', 'sadness'],
            'hypertension': ['headache', 'dizziness', 'chest pain', 'shortness of breath'],
            'diabetes': ['increased thirst', 'frequent urination', 'fatigue', 'blurred vision']
        }
        
        for disease, symptoms in diseases.items():
            for i in range(50):  # Generate 50 examples per disease
                # Select 2-4 symptoms randomly
                selected_symptoms = np.random.choice(symptoms, size=np.random.randint(2, 5), replace=False)
                symptom_text = ', '.join(selected_symptoms)
                
                # Add some noise and variations
                if np.random.random() < 0.3:
                    symptom_text = symptom_text + ' for ' + str(np.random.randint(1, 14)) + ' days'
                
                training_data.append({
                    'symptom_text': symptom_text,
                    'disease': disease,
                    'severity': np.random.choice(['low', 'medium', 'high'])
                })
        
        return pd.DataFrame(training_data)
    
    def train(self, X_train: List[str] = None, y_train: List[str] = None):
        """Train the symptom classifier."""
        if X_train is None or y_train is None:
            # Use synthetic data if no training data provided
            df = self.create_training_data()
            X_train = df['symptom_text'].tolist()
            y_train = df['disease'].tolist()
        
        # Preprocess text data
        X_train_processed = [self.preprocess_text(text) for text in X_train]
        
        # Encode labels
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        # Vectorize text
        X_train_vectorized = self.vectorizer.fit_transform(X_train_processed)
        
        # Train classifier
        self.classifier.fit(X_train_vectorized, y_train_encoded)
        self.is_trained = True
        
        print("Training completed successfully!")
        
        # Evaluate on training data (in production, use separate validation set)
        y_pred = self.classifier.predict(X_train_vectorized)
        accuracy = accuracy_score(y_train_encoded, y_pred)
        print(f"Training accuracy: {accuracy:.3f}")
        
        return accuracy
    
    def predict(self, symptom_text: str) -> Dict:
        """Predict disease/condition from symptom text."""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Preprocess text
        processed_text = self.preprocess_text(symptom_text)
        
        # Vectorize
        text_vectorized = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.classifier.predict(text_vectorized)[0]
        probability = self.classifier.predict_proba(text_vectorized)[0]
        
        # Get prediction details
        predicted_disease = self.label_encoder.inverse_transform([prediction])[0]
        confidence = np.max(probability)
        
        # Extract and categorize symptoms
        symptoms = self.extract_symptoms(symptom_text)
        categorized_symptoms = self.categorize_symptoms(symptoms)
        
        return {
            'predicted_condition': predicted_disease,
            'confidence': float(confidence),
            'symptoms_extracted': symptoms,
            'symptoms_categorized': categorized_symptoms,
            'all_probabilities': {
                disease: float(prob) for disease, prob in 
                zip(self.label_encoder.classes_, probability)
            }
        }
    
    def save_model(self, path: str = None):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        if path is None:
            path = self.model_path or 'symptom_classifier.pkl'
        
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier,
            'label_encoder': self.label_encoder,
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
        
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        self.label_encoder = model_data['label_encoder']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {path}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize classifier
    classifier = SymptomClassifier()
    
    # Train the model
    print("Training symptom classifier...")
    classifier.train()
    
    # Test predictions
    test_symptoms = [
        "I have a severe headache and nausea",
        "Running nose, cough, and fever for 3 days",
        "Chest pain and shortness of breath",
        "Fatigue, increased thirst, and blurred vision"
    ]
    
    print("\nTesting predictions:")
    for symptom in test_symptoms:
        result = classifier.predict(symptom)
        print(f"\nSymptom: {symptom}")
        print(f"Predicted condition: {result['predicted_condition']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Symptoms extracted: {result['symptoms_extracted']}")
    
    # Save the model
    model_path = "ml_models/nlp/trained_symptom_classifier.pkl"
    classifier.save_model(model_path)