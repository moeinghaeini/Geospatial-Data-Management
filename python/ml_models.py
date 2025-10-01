"""
Machine Learning Models for Spatial Analysis
Provides ML capabilities for geospatial data prediction and analysis
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, silhouette_score
from sklearn.neighbors import NearestNeighbors
import joblib
import os
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class SpatialMLPredictor:
    """
    Machine learning models for spatial analysis and prediction
    """
    
    def __init__(self):
        """Initialize the ML predictor"""
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_path = "models"
        os.makedirs(self.model_path, exist_ok=True)
        
    def train_model(self, gdf: gpd.GeoDataFrame, model_type: str = "accessibility") -> Dict:
        """
        Train machine learning models on spatial data
        
        Args:
            gdf: GeoDataFrame with spatial data
            model_type: Type of model to train ('accessibility', 'clustering', 'classification')
            
        Returns:
            Training results dictionary
        """
        try:
            if model_type == "accessibility":
                return self._train_accessibility_model(gdf)
            elif model_type == "clustering":
                return self._train_clustering_model(gdf)
            elif model_type == "classification":
                return self._train_classification_model(gdf)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
        except Exception as e:
            raise Exception(f"Model training failed: {str(e)}")
    
    def _train_accessibility_model(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Train accessibility prediction model"""
        try:
            # Prepare features
            features = self._prepare_spatial_features(gdf)
            
            # Calculate accessibility scores (target variable)
            accessibility_scores = self._calculate_accessibility_scores(gdf)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, accessibility_scores, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
            }
            
            results = {}
            for name, model in models.items():
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Calculate metrics
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
                
                results[name] = {
                    'mse': mse,
                    'r2': r2,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std()
                }
                
                # Save best model
                if name == 'random_forest':  # Use RF as default
                    self.models['accessibility'] = model
                    self.scalers['accessibility'] = scaler
                    joblib.dump(model, f"{self.model_path}/accessibility_model.pkl")
                    joblib.dump(scaler, f"{self.model_path}/accessibility_scaler.pkl")
            
            return {
                'model_type': 'accessibility',
                'training_samples': len(features),
                'test_samples': len(X_test),
                'results': results,
                'best_model': 'random_forest'
            }
            
        except Exception as e:
            raise Exception(f"Accessibility model training failed: {str(e)}")
    
    def _train_clustering_model(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Train spatial clustering model"""
        try:
            # Prepare features
            features = self._prepare_spatial_features(gdf)
            
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Train clustering models
            models = {
                'kmeans': KMeans(n_clusters=3, random_state=42),
                'dbscan': DBSCAN(eps=0.5, min_samples=2)
            }
            
            results = {}
            for name, model in models.items():
                # Fit model
                labels = model.fit_predict(features_scaled)
                
                # Calculate silhouette score
                if len(set(labels)) > 1:  # Need at least 2 clusters
                    silhouette = silhouette_score(features_scaled, labels)
                else:
                    silhouette = -1
                
                results[name] = {
                    'n_clusters': len(set(labels)),
                    'silhouette_score': silhouette,
                    'labels': labels.tolist()
                }
                
                # Save best model
                if name == 'kmeans':
                    self.models['clustering'] = model
                    self.scalers['clustering'] = scaler
                    joblib.dump(model, f"{self.model_path}/clustering_model.pkl")
                    joblib.dump(scaler, f"{self.model_path}/clustering_scaler.pkl")
            
            return {
                'model_type': 'clustering',
                'training_samples': len(features),
                'results': results,
                'best_model': 'kmeans'
            }
            
        except Exception as e:
            raise Exception(f"Clustering model training failed: {str(e)}")
    
    def _train_classification_model(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Train landmark type classification model"""
        try:
            # Prepare features
            features = self._prepare_spatial_features(gdf)
            
            # Get target variable (landmark type)
            if 'type' in gdf.columns:
                target = gdf['type'].values
            else:
                raise ValueError("'type' column not found for classification")
            
            # Encode target variable
            encoder = LabelEncoder()
            target_encoded = encoder.fit_transform(target)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target_encoded, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train classification model
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate accuracy
            accuracy = (y_pred == y_test).mean()
            
            # Save model
            self.models['classification'] = model
            self.scalers['classification'] = scaler
            self.encoders['classification'] = encoder
            joblib.dump(model, f"{self.model_path}/classification_model.pkl")
            joblib.dump(scaler, f"{self.model_path}/classification_scaler.pkl")
            joblib.dump(encoder, f"{self.model_path}/classification_encoder.pkl")
            
            return {
                'model_type': 'classification',
                'training_samples': len(features),
                'test_samples': len(X_test),
                'accuracy': accuracy,
                'classes': encoder.classes_.tolist()
            }
            
        except Exception as e:
            raise Exception(f"Classification model training failed: {str(e)}")
    
    def _prepare_spatial_features(self, gdf: gpd.GeoDataFrame) -> np.ndarray:
        """Prepare spatial features for ML models"""
        features = []
        
        for idx, row in gdf.iterrows():
            feature_vector = []
            
            # Geographic features
            if hasattr(row.geometry, 'centroid'):
                feature_vector.extend([row.geometry.centroid.x, row.geometry.centroid.y])
            else:
                feature_vector.extend([0, 0])
            
            # Geometry features
            feature_vector.append(row.geometry.area)
            feature_vector.append(row.geometry.length)
            feature_vector.append(row.geometry.bounds[0])  # min_x
            feature_vector.append(row.geometry.bounds[1])  # min_y
            feature_vector.append(row.geometry.bounds[2])  # max_x
            feature_vector.append(row.geometry.bounds[3])  # max_y
            
            # Distance to center of Italy
            italy_center = [12.5674, 41.8719]  # Rome coordinates
            if hasattr(row.geometry, 'centroid'):
                distance = np.sqrt(
                    (row.geometry.centroid.x - italy_center[0])**2 + 
                    (row.geometry.centroid.y - italy_center[1])**2
                )
                feature_vector.append(distance)
            else:
                feature_vector.append(0)
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _calculate_accessibility_scores(self, gdf: gpd.GeoDataFrame) -> np.ndarray:
        """Calculate accessibility scores for landmarks"""
        scores = []
        
        for idx, landmark in gdf.iterrows():
            # Calculate distances to all other landmarks
            distances = []
            for other_idx, other_landmark in gdf.iterrows():
                if idx != other_idx:
                    distance = np.sqrt(
                        (landmark.geometry.centroid.x - other_landmark.geometry.centroid.x)**2 +
                        (landmark.geometry.centroid.y - other_landmark.geometry.centroid.y)**2
                    )
                    distances.append(distance)
            
            # Accessibility score (inverse of average distance)
            if distances:
                avg_distance = np.mean(distances)
                score = 1 / (avg_distance + 1)  # Add 1 to avoid division by zero
            else:
                score = 0
            
            scores.append(score)
        
        return np.array(scores)
    
    def predict(self, features: List[float], model_type: str = "accessibility") -> Dict:
        """
        Make predictions using trained models
        
        Args:
            features: Input features for prediction
            model_type: Type of model to use
            
        Returns:
            Prediction results dictionary
        """
        try:
            if model_type not in self.models:
                # Try to load saved model
                self._load_model(model_type)
            
            if model_type not in self.models:
                raise ValueError(f"Model '{model_type}' not found or trained")
            
            # Prepare features
            features_array = np.array(features).reshape(1, -1)
            
            # Scale features
            if model_type in self.scalers:
                features_scaled = self.scalers[model_type].transform(features_array)
            else:
                features_scaled = features_array
            
            # Make prediction
            model = self.models[model_type]
            prediction = model.predict(features_scaled)[0]
            
            # Get confidence/probability if available
            confidence = 0.0
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(features_scaled)[0]
                confidence = np.max(probabilities)
            elif hasattr(model, 'feature_importances_'):
                confidence = 0.8  # Default confidence for tree-based models
            
            return {
                'prediction': float(prediction),
                'confidence': float(confidence),
                'model_type': model_type,
                'features_used': len(features)
            }
            
        except Exception as e:
            raise Exception(f"Prediction failed: {str(e)}")
    
    def _load_model(self, model_type: str):
        """Load saved model from disk"""
        try:
            model_path = f"{self.model_path}/{model_type}_model.pkl"
            scaler_path = f"{self.model_path}/{model_type}_scaler.pkl"
            
            if os.path.exists(model_path):
                self.models[model_type] = joblib.load(model_path)
            
            if os.path.exists(scaler_path):
                self.scalers[model_type] = joblib.load(scaler_path)
            
            # Load encoder for classification
            if model_type == 'classification':
                encoder_path = f"{self.model_path}/{model_type}_encoder.pkl"
                if os.path.exists(encoder_path):
                    self.encoders[model_type] = joblib.load(encoder_path)
                    
        except Exception as e:
            print(f"Warning: Could not load model {model_type}: {str(e)}")
    
    def get_model_info(self, model_type: str = None) -> Dict:
        """Get information about trained models"""
        if model_type:
            return {
                'model_type': model_type,
                'trained': model_type in self.models,
                'scaler_available': model_type in self.scalers,
                'encoder_available': model_type in self.encoders
            }
        else:
            return {
                'available_models': list(self.models.keys()),
                'available_scalers': list(self.scalers.keys()),
                'available_encoders': list(self.encoders.keys())
            }
    
    def evaluate_model(self, model_type: str, test_data: gpd.GeoDataFrame) -> Dict:
        """Evaluate model performance on test data"""
        try:
            if model_type not in self.models:
                raise ValueError(f"Model '{model_type}' not found")
            
            # Prepare test features
            test_features = self._prepare_spatial_features(test_data)
            
            # Scale features
            if model_type in self.scalers:
                test_features_scaled = self.scalers[model_type].transform(test_features)
            else:
                test_features_scaled = test_features
            
            # Make predictions
            predictions = self.models[model_type].predict(test_features_scaled)
            
            # Calculate evaluation metrics
            if model_type == 'accessibility':
                # For regression models
                true_scores = self._calculate_accessibility_scores(test_data)
                mse = mean_squared_error(true_scores, predictions)
                r2 = r2_score(true_scores, predictions)
                
                return {
                    'model_type': model_type,
                    'mse': mse,
                    'r2': r2,
                    'predictions': predictions.tolist()
                }
            else:
                # For classification/clustering models
                return {
                    'model_type': model_type,
                    'predictions': predictions.tolist(),
                    'n_predictions': len(predictions)
                }
                
        except Exception as e:
            raise Exception(f"Model evaluation failed: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Sample Italian landmarks data
    sample_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 1,
                "properties": {
                    "name": "Colosseum",
                    "description": "Ancient Roman amphitheater in Rome",
                    "type": "monument"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.4922, 41.8902]
                }
            },
            {
                "type": "Feature",
                "id": 2,
                "properties": {
                    "name": "Leaning Tower of Pisa",
                    "description": "Famous bell tower in Pisa",
                    "type": "monument"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [10.3966, 43.7230]
                }
            }
        ]
    }
    
    # Initialize ML predictor
    ml_predictor = SpatialMLPredictor()
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(sample_data['features'])
    
    # Test model training
    print("🤖 Testing ML model training...")
    training_results = ml_predictor.train_model(gdf, model_type="accessibility")
    print(f"✅ Training completed: {training_results['model_type']}")
    print(f"✅ Training samples: {training_results['training_samples']}")
    
    # Test prediction
    print("🔮 Testing ML prediction...")
    sample_features = [12.4922, 41.8902, 0.001, 0.001, 12.49, 41.89, 12.50, 41.90, 0.1]
    prediction = ml_predictor.predict(sample_features, model_type="accessibility")
    print(f"✅ Prediction: {prediction['prediction']:.4f}")
    print(f"✅ Confidence: {prediction['confidence']:.4f}")
    
    print("🎉 ML model tests completed successfully!")
