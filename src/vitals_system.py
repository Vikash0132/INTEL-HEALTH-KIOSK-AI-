from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class VitalSign:
    """Data class for individual vital sign"""
    name: str
    value: Optional[float]
    unit: str
    normal_range: Tuple[float, float]
    category: str
    timestamp: datetime
    status: str = "normal"  # normal, low, high, critical
    
    def __post_init__(self):
        """Determine status based on value and normal range"""
        if self.value is not None:
            min_val, max_val = self.normal_range
            if self.value < min_val:
                self.status = "low"
            elif self.value > max_val:
                self.status = "high"
            # Add critical thresholds (example: very high or very low)
            critical_low = min_val * 0.7
            critical_high = max_val * 1.3
            if self.value < critical_low or self.value > critical_high:
                self.status = "critical"

class VitalsCollectionSystem:
    """
    Comprehensive system for collecting and managing 28 vital signs
    """
    
    def __init__(self):
        """Initialize the vitals collection system"""
        self.vital_definitions = self._initialize_vital_definitions()
        self.current_session = {}
        logger.info("Vitals Collection System initialized")
    
    def _initialize_vital_definitions(self) -> Dict[str, Dict]:
        """Initialize definitions for all 28 vital signs"""
        return {
            # Cardiovascular
            'heart_rate': {
                'name': 'Heart Rate',
                'unit': 'bpm',
                'normal_range': (60, 100),
                'category': 'cardiovascular',
                'description': 'Number of heartbeats per minute'
            },
            'blood_pressure_systolic': {
                'name': 'Systolic Blood Pressure',
                'unit': 'mmHg',
                'normal_range': (90, 120),
                'category': 'cardiovascular',
                'description': 'Pressure when heart contracts'
            },
            'blood_pressure_diastolic': {
                'name': 'Diastolic Blood Pressure',
                'unit': 'mmHg',
                'normal_range': (60, 80),
                'category': 'cardiovascular',
                'description': 'Pressure when heart relaxes'
            },
            'pulse_rate': {
                'name': 'Pulse Rate',
                'unit': 'bpm',
                'normal_range': (60, 100),
                'category': 'cardiovascular',
                'description': 'Arterial pulse rate'
            },
            'mean_arterial_pressure': {
                'name': 'Mean Arterial Pressure',
                'unit': 'mmHg',
                'normal_range': (70, 100),
                'category': 'cardiovascular',
                'description': 'Average arterial pressure'
            },
            'blood_pressure_pulse_pressure': {
                'name': 'Pulse Pressure',
                'unit': 'mmHg',
                'normal_range': (30, 40),
                'category': 'cardiovascular',
                'description': 'Difference between systolic and diastolic'
            },
            
            # Respiratory
            'respiratory_rate': {
                'name': 'Respiratory Rate',
                'unit': 'breaths/min',
                'normal_range': (12, 20),
                'category': 'respiratory',
                'description': 'Number of breaths per minute'
            },
            'oxygen_saturation': {
                'name': 'Oxygen Saturation',
                'unit': '%',
                'normal_range': (95, 100),
                'category': 'respiratory',
                'description': 'Oxygen saturation in blood'
            },
            
            # Metabolic
            'body_temperature': {
                'name': 'Body Temperature',
                'unit': '°C',
                'normal_range': (36.1, 37.2),
                'category': 'metabolic',
                'description': 'Core body temperature'
            },
            'blood_glucose': {
                'name': 'Blood Glucose',
                'unit': 'mg/dL',
                'normal_range': (70, 140),
                'category': 'metabolic',
                'description': 'Blood sugar level'
            },
            
            # Lipid Profile
            'cholesterol_total': {
                'name': 'Total Cholesterol',
                'unit': 'mg/dL',
                'normal_range': (0, 200),
                'category': 'lipid_profile',
                'description': 'Total cholesterol level'
            },
            'cholesterol_ldl': {
                'name': 'LDL Cholesterol',
                'unit': 'mg/dL',
                'normal_range': (0, 100),
                'category': 'lipid_profile',
                'description': 'Low-density lipoprotein cholesterol'
            },
            'cholesterol_hdl': {
                'name': 'HDL Cholesterol',
                'unit': 'mg/dL',
                'normal_range': (40, 100),
                'category': 'lipid_profile',
                'description': 'High-density lipoprotein cholesterol'
            },
            'triglycerides': {
                'name': 'Triglycerides',
                'unit': 'mg/dL',
                'normal_range': (0, 150),
                'category': 'lipid_profile',
                'description': 'Blood triglyceride level'
            },
            
            # Hematology
            'hemoglobin': {
                'name': 'Hemoglobin',
                'unit': 'g/dL',
                'normal_range': (12.0, 16.0),
                'category': 'hematology',
                'description': 'Hemoglobin level in blood'
            },
            'white_blood_cells': {
                'name': 'White Blood Cells',
                'unit': 'cells/μL',
                'normal_range': (4000, 11000),
                'category': 'hematology',
                'description': 'White blood cell count'
            },
            'red_blood_cells': {
                'name': 'Red Blood Cells',
                'unit': 'cells/μL',
                'normal_range': (4200000, 5400000),
                'category': 'hematology',
                'description': 'Red blood cell count'
            },
            'platelets': {
                'name': 'Platelets',
                'unit': 'cells/μL',
                'normal_range': (150000, 450000),
                'category': 'hematology',
                'description': 'Platelet count'
            },
            
            # Anthropometric
            'height': {
                'name': 'Height',
                'unit': 'cm',
                'normal_range': (140, 220),
                'category': 'anthropometric',
                'description': 'Body height'
            },
            'weight': {
                'name': 'Weight',
                'unit': 'kg',
                'normal_range': (30, 200),
                'category': 'anthropometric',
                'description': 'Body weight'
            },
            'bmi': {
                'name': 'Body Mass Index',
                'unit': 'kg/m²',
                'normal_range': (18.5, 24.9),
                'category': 'anthropometric',
                'description': 'Body mass index'
            },
            'waist_circumference': {
                'name': 'Waist Circumference',
                'unit': 'cm',
                'normal_range': (70, 102),
                'category': 'anthropometric',
                'description': 'Waist measurement'
            },
            'hip_circumference': {
                'name': 'Hip Circumference',
                'unit': 'cm',
                'normal_range': (85, 120),
                'category': 'anthropometric',
                'description': 'Hip measurement'
            },
            
            # Body Composition
            'body_fat_percentage': {
                'name': 'Body Fat Percentage',
                'unit': '%',
                'normal_range': (10, 25),
                'category': 'body_composition',
                'description': 'Percentage of body fat'
            },
            'muscle_mass': {
                'name': 'Muscle Mass',
                'unit': 'kg',
                'normal_range': (25, 50),
                'category': 'body_composition',
                'description': 'Total muscle mass'
            },
            'bone_density': {
                'name': 'Bone Density',
                'unit': 'g/cm²',
                'normal_range': (0.8, 1.2),
                'category': 'body_composition',
                'description': 'Bone mineral density'
            },
            
            # Sensory
            'vision_acuity': {
                'name': 'Vision Acuity',
                'unit': 'ratio',
                'normal_range': (0.8, 1.0),
                'category': 'sensory',
                'description': 'Visual acuity measurement'
            },
            'hearing_threshold': {
                'name': 'Hearing Threshold',
                'unit': 'dB',
                'normal_range': (0, 25),
                'category': 'sensory',
                'description': 'Hearing threshold level'
            }
        }
    
    def collect_vital(self, vital_name: str, value: float) -> VitalSign:
        """
        Collect a single vital sign measurement
        
        Args:
            vital_name: Name of the vital sign
            value: Measured value
            
        Returns:
            VitalSign object with the measurement
        """
        if vital_name not in self.vital_definitions:
            raise ValueError(f"Unknown vital sign: {vital_name}")
        
        vital_def = self.vital_definitions[vital_name]
        
        vital_sign = VitalSign(
            name=vital_def['name'],
            value=value,
            unit=vital_def['unit'],
            normal_range=vital_def['normal_range'],
            category=vital_def['category'],
            timestamp=datetime.now()
        )
        
        # Store in current session
        self.current_session[vital_name] = vital_sign
        
        logger.info(f"Collected {vital_name}: {value} {vital_def['unit']} - Status: {vital_sign.status}")
        
        return vital_sign
    
    def collect_multiple_vitals(self, vitals_data: Dict[str, float]) -> Dict[str, VitalSign]:
        """
        Collect multiple vital signs at once
        
        Args:
            vitals_data: Dictionary of vital_name -> value pairs
            
        Returns:
            Dictionary of VitalSign objects
        """
        collected_vitals = {}
        
        for vital_name, value in vitals_data.items():
            try:
                vital_sign = self.collect_vital(vital_name, value)
                collected_vitals[vital_name] = vital_sign
            except ValueError as e:
                logger.warning(f"Failed to collect {vital_name}: {str(e)}")
        
        return collected_vitals
    
    def calculate_derived_vitals(self) -> Dict[str, VitalSign]:
        """Calculate derived vital signs from collected data"""
        derived = {}
        
        # Calculate BMI if height and weight are available
        if 'height' in self.current_session and 'weight' in self.current_session:
            height_m = self.current_session['height'].value / 100  # Convert cm to m
            weight_kg = self.current_session['weight'].value
            bmi_value = weight_kg / (height_m ** 2)
            
            derived['bmi'] = self.collect_vital('bmi', bmi_value)
        
        # Calculate Mean Arterial Pressure if both BP readings available
        if ('blood_pressure_systolic' in self.current_session and 
            'blood_pressure_diastolic' in self.current_session):
            
            systolic = self.current_session['blood_pressure_systolic'].value
            diastolic = self.current_session['blood_pressure_diastolic'].value
            map_value = diastolic + (systolic - diastolic) / 3
            
            derived['mean_arterial_pressure'] = self.collect_vital('mean_arterial_pressure', map_value)
        
        # Calculate Pulse Pressure
        if ('blood_pressure_systolic' in self.current_session and 
            'blood_pressure_diastolic' in self.current_session):
            
            systolic = self.current_session['blood_pressure_systolic'].value
            diastolic = self.current_session['blood_pressure_diastolic'].value
            pulse_pressure = systolic - diastolic
            
            derived['blood_pressure_pulse_pressure'] = self.collect_vital(
                'blood_pressure_pulse_pressure', pulse_pressure
            )
        
        return derived
    
    def get_vitals_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of collected vitals"""
        summary = {
            'total_vitals': len(self.current_session),
            'categories': {},
            'status_counts': {'normal': 0, 'low': 0, 'high': 0, 'critical': 0},
            'critical_vitals': [],
            'abnormal_vitals': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze by category and status
        for vital_name, vital_sign in self.current_session.items():
            category = vital_sign.category
            status = vital_sign.status
            
            # Count by category
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
            
            # Count by status
            summary['status_counts'][status] += 1
            
            # Track critical and abnormal vitals
            if status == 'critical':
                summary['critical_vitals'].append({
                    'name': vital_sign.name,
                    'value': vital_sign.value,
                    'unit': vital_sign.unit,
                    'normal_range': vital_sign.normal_range
                })
            elif status in ['low', 'high']:
                summary['abnormal_vitals'].append({
                    'name': vital_sign.name,
                    'value': vital_sign.value,
                    'unit': vital_sign.unit,
                    'status': status,
                    'normal_range': vital_sign.normal_range
                })
        
        return summary
    
    def export_vitals_data(self, format: str = 'json') -> str:
        """Export collected vitals data in specified format"""
        vitals_data = {
            vital_name: asdict(vital_sign) 
            for vital_name, vital_sign in self.current_session.items()
        }
        
        if format.lower() == 'json':
            return json.dumps(vitals_data, indent=2, default=str)
        elif format.lower() == 'csv':
            df = pd.DataFrame([
                {
                    'vital_name': vital_name,
                    'display_name': vital.name,
                    'value': vital.value,
                    'unit': vital.unit,
                    'status': vital.status,
                    'category': vital.category,
                    'timestamp': vital.timestamp
                }
                for vital_name, vital in self.current_session.items()
            ])
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def get_health_score(self) -> Dict[str, Any]:
        """Calculate overall health score based on vitals"""
        if not self.current_session:
            return {'score': 0, 'grade': 'Unknown', 'message': 'No vitals collected'}
        
        total_vitals = len(self.current_session)
        normal_count = sum(1 for v in self.current_session.values() if v.status == 'normal')
        abnormal_count = sum(1 for v in self.current_session.values() if v.status in ['low', 'high'])
        critical_count = sum(1 for v in self.current_session.values() if v.status == 'critical')
        
        # Calculate score (0-100)
        base_score = (normal_count / total_vitals) * 100
        abnormal_penalty = (abnormal_count / total_vitals) * 20
        critical_penalty = (critical_count / total_vitals) * 50
        
        final_score = max(0, base_score - abnormal_penalty - critical_penalty)
        
        # Determine grade
        if final_score >= 90:
            grade = 'Excellent'
        elif final_score >= 80:
            grade = 'Good'
        elif final_score >= 70:
            grade = 'Fair'
        elif final_score >= 60:
            grade = 'Poor'
        else:
            grade = 'Critical'
        
        return {
            'score': round(final_score, 1),
            'grade': grade,
            'normal_vitals': normal_count,
            'abnormal_vitals': abnormal_count,
            'critical_vitals': critical_count,
            'total_vitals': total_vitals
        }
    
    def clear_session(self):
        """Clear current vitals session"""
        self.current_session.clear()
        logger.info("Vitals session cleared")
    
    def get_vital_definition(self, vital_name: str) -> Dict[str, Any]:
        """Get definition for a specific vital sign"""
        return self.vital_definitions.get(vital_name, {})
    
    def get_all_vital_definitions(self) -> Dict[str, Dict]:
        """Get all vital sign definitions"""
        return self.vital_definitions
    
    def validate_vital_value(self, vital_name: str, value: float) -> Dict[str, Any]:
        """Validate if a vital value is reasonable"""
        if vital_name not in self.vital_definitions:
            return {'valid': False, 'error': 'Unknown vital sign'}
        
        vital_def = self.vital_definitions[vital_name]
        min_val, max_val = vital_def['normal_range']
        
        # Allow some tolerance outside normal range for measurement validity
        tolerance_factor = 2.0
        min_valid = min_val / tolerance_factor
        max_valid = max_val * tolerance_factor
        
        if min_valid <= value <= max_valid:
            return {'valid': True, 'message': 'Value within acceptable range'}
        else:
            return {
                'valid': False, 
                'error': f'Value {value} outside acceptable range ({min_valid:.1f} - {max_valid:.1f})'
            }
