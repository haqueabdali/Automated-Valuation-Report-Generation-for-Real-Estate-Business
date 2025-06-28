import pandas as pd
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Union, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValuationModel:
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the valuation model with robust error handling
        
        Args:
            model_path: Optional path to pretrained model file
        """
        self.model = None
        self.features = [
            'bedrooms',
            'bathrooms',
            'square_footage', 
            'lot_size',
            'year_built',
            'location_score'
        ]
        self._initialize_model(model_path)

    def _initialize_model(self, model_path: Optional[str]):
        """Internal method to handle model initialization"""
        try:
            if model_path:
                self.load_model(model_path)
            else:
                self.load_model(self.get_default_model_path())
            
            # Verify model is properly initialized
            if not hasattr(self.model, 'predict'):
                raise AttributeError("Model initialization failed")
                
        except Exception as e:
            logger.error(f"Model initialization error: {str(e)}")
            self._initialize_fallback_model()

    def get_default_model_path(self) -> Path:
        """Get path to default model file"""
        return Path(__file__).parent / 'trained_model.pkl'

    def load_model(self, model_path: str) -> bool:
        """
        Safely load trained model from file
        
        Args:
            model_path: Path to model file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        model_path = Path(model_path)
        try:
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return False
                
            if model_path.stat().st_size < 100:  # Minimum 100 bytes
                logger.warning(f"Model file too small: {model_path}")
                return False
                
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
            logger.info(f"Successfully loaded model from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {str(e)}")
            return False

    def _initialize_fallback_model(self):
        """Initialize a new model as fallback"""
        logger.info("Initializing new RandomForest model")
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            verbose=1
        )
        logger.info("New model initialized. Requires training before use.")

    def predict_valuation(self, property_data: Union[Dict, pd.DataFrame]) -> Optional[float]:
        """
        Predict property valuation with comprehensive error handling
        
        Args:
            property_data: Property features as dict or DataFrame
            
        Returns:
            Predicted value (float) or None if prediction fails
        """
        try:
            if not hasattr(self.model, 'predict'):
                raise ValueError("Model not properly initialized")
                
            features = self._prepare_features(property_data)
            prediction = self.model.predict([features])[0]
            return round(float(prediction), 2)
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            return None

    def _prepare_features(self, property_data: Union[Dict, pd.DataFrame]) -> list:
        """
        Prepare input features for prediction
        
        Args:
            property_data: Input data to convert
            
        Returns:
            list: Prepared feature values
        """
        if isinstance(property_data, pd.DataFrame):
            property_data = property_data.iloc[0].to_dict()
            
        return [
            float(property_data.get('bedrooms', 0)),
            float(property_data.get('bathrooms', 0)),
            float(property_data.get('square_footage', 0)),
            float(property_data.get('lot_size', 0)),
            float(property_data.get('year_built', 0)),
            float(property_data.get('location_score', 0))
        ]

    def train_model(self, training_data: pd.DataFrame, save_path: Optional[str] = None) -> bool:
        """
        Train the model and optionally save it
        
        Args:
            training_data: DataFrame with features and target
            save_path: Optional path to save trained model
            
        Returns:
            bool: True if training succeeded
        """
        try:
            # Validate input data
            if not isinstance(training_data, pd.DataFrame):
                raise ValueError("training_data must be a DataFrame")
                
            if 'price' not in training_data.columns:
                raise ValueError("training_data must contain 'price' column")
                
            # Train model
            self.model.fit(training_data[self.features], training_data['price'])
            logger.info("Model training completed successfully")
            
            # Save model if requested
            if save_path:
                self._save_model(save_path)
                
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False

    def _save_model(self, save_path: str):
        """Internal method to save model with error handling"""
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise


# Singleton instance for application-wide access
valuation_model = ValuationModel()

def predict_valuation(property_data: Union[Dict, pd.DataFrame]) -> Optional[float]:
    """
    Public interface for valuation prediction
    
    Args:
        property_data: Property features as dict or DataFrame
        
    Returns:
        Predicted valuation or None if prediction fails
    """
    return valuation_model.predict_valuation(property_data)