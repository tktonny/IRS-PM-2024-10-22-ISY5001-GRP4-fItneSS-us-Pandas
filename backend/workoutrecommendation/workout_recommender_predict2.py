import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class WorkoutRecommender:
    def __init__(self):
        self.scaler = None
        self.rf_avg = None
        self.rf_frequency = None
        self.rf_duration = None
        self.rf_water = None
        self.features = None
        self.workout_types = None
        self.exercise_mapping = {
            'Strength': [
                'Dumbbell Flat Bench Press', 'Barbell Bench Press', 'Bent-over Barbell Row',
                'Wide-Grip Lat Pulldown', 'Butterfly Machine Chest Fly', 'Lateral Raise',
                'Standing Barbell Shoulder', 'Barbell Bicep Curl', 'Barbell Curl',
                'Barbell Squat', 'Leg Extension Machine', 'Leg Press'
            ],
            'Cardio': ['Push-up'],
            'HIIT': ['Push-up'],
            'Yoga': ['Plank', 'Sit-up']
        }

    def load_models(self, directory):
        self.scaler = joblib.load(os.path.join(directory, 'scaler.joblib'))
        self.rf_avg = joblib.load(os.path.join(directory, 'rf_avg.joblib'))
        self.rf_frequency = joblib.load(os.path.join(directory, 'rf_frequency.joblib'))
        self.rf_duration = joblib.load(os.path.join(directory, 'rf_duration.joblib'))
        self.rf_water = joblib.load(os.path.join(directory, 'rf_water.joblib'))
        self.workout_types = joblib.load(os.path.join(directory, 'workout_types.joblib'))
        self.features = joblib.load(os.path.join(directory, 'features.joblib'))

    def recommend_workout(self, age, gender, weight, height, experience_level):
        gender_numeric = 0 if gender.lower() == 'female' else 1
        bmi = weight / (height ** 2)
        
        input_data = pd.DataFrame(columns=self.features)
        input_data.loc[0] = 0  # 用0初始化所有列
        
        # 填充已知的特征值
        input_data.loc[0, 'Age'] = age
        input_data.loc[0, 'Gender'] = gender_numeric
        input_data.loc[0, 'Weight (kg)'] = weight
        input_data.loc[0, 'Height (m)'] = height
        input_data.loc[0, 'BMI'] = bmi
        input_data.loc[0, 'Experience_Level'] = experience_level
        
        predictions = []
        for workout in self.workout_types:
            input_data_copy = input_data.copy()
            input_data_copy.loc[0, f'Workout_Type_{workout}'] = 1
            
            predicted_avg_bpm = self.rf_avg.predict(input_data_copy)[0]
            predicted_frequency = self.rf_frequency.predict(input_data_copy)[0]
            predicted_duration = self.rf_duration.predict(input_data_copy)[0]
            predicted_water = self.rf_water.predict(input_data_copy)[0]
            
            predictions.append({
                'workout': workout,
                'avg_bpm': round(predicted_avg_bpm),
                'frequency': round(predicted_frequency),
                'duration': round(predicted_duration, 2),
                'water_intake': round(predicted_water, 2)
            })
        
        predictions.sort(key=lambda x: x['frequency'], reverse=True)
        top_predictions = predictions[:3]  # 推荐前3种运动
        
        return {
            'recommended_workouts': top_predictions,
        }

    def print_recommendation(self, age, gender, weight, height, experience_level):
        recommendation = self.recommend_workout(age, gender, weight, height, experience_level)
        for pred in recommendation['recommended_workouts']:
            print(f"\nRecommended Workout: {pred['workout']}")
            print(f"Predicted Average BPM: {pred['avg_bpm']}")
            print(f"Recommended Workout Frequency: {pred['frequency']} days/week")
            print(f"Recommended Duration: {pred['duration']} hours")
            print(f"Suggested Water Intake: {pred['water_intake']} liters")
            print("Recommended Exercises:")
            for exercise in self.exercise_mapping.get(pred['workout'], []):
                print(f"- {exercise}")

    def get_recommendation(self, age, gender, weight, height, experience_level):
        recommendation = self.recommend_workout(age, gender, weight, height, experience_level)
        result = []
        for pred in recommendation['recommended_workouts']:
            workout_info = {
                'workout': pred['workout'],
                'avg_bpm': pred['avg_bpm'],
                'frequency': pred['frequency'],
                'duration': pred['duration'],
                'water_intake': pred['water_intake'],
                'exercises': self.exercise_mapping.get(pred['workout'], [])
            }
            result.append(workout_info)
        return result

# 使用示例
if __name__ == "__main__":
    recommender = WorkoutRecommender()
    recommender.load_models('path_to_models')  # 请替换为实际的模型路径

    # 打印推荐信息
    print("Printed Recommendation:")
    recommender.print_recommendation(30, 'Male', 75, 1.75, 2)

    # 获取推荐变量
    print("\nReturned Recommendation:")
    recommendation = recommender.get_recommendation(30, 'Male', 75, 1.75, 2)
    for rec in recommendation:
        print(rec)