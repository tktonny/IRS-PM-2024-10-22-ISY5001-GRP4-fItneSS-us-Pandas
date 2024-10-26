import pandas as pd
import numpy as np
import os
import joblib

class WorkoutRecommender:
    def __init__(self):
        self.scaler = None
        self.knn_model = None
        self.rf_avg = None
        self.rf_frequency = None
        self.rf_duration = None
        self.rf_water = None
        self.features = None
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
        try:
            self.scaler = joblib.load(os.path.join(directory, 'scaler.joblib'))
            self.knn_model = joblib.load(os.path.join(directory, 'knn_model.joblib'))
            self.rf_avg = joblib.load(os.path.join(directory, 'rf_avg.joblib'))
            self.rf_frequency = joblib.load(os.path.join(directory, 'rf_frequency.joblib'))
            self.rf_duration = joblib.load(os.path.join(directory, 'rf_duration.joblib'))
            self.rf_water = joblib.load(os.path.join(directory, 'rf_water.joblib'))
            self.features = self.rf_avg.feature_names_in_
        except Exception as e:
            print(f"Error loading models: {e}")

    def recommend_workout(self, age, gender, weight, height, experience_level):
        try:
            print("\n1. Loading models successful")
            gender_numeric = 0 if gender.lower() == 'female' else 1
            bmi = weight / (height ** 2)

            # 直接使用模型加载的特征名创建数组
            values = np.zeros(len(self.features))
            values[0] = age  # Age
            values[1] = gender_numeric   # Gender
            values[2] = weight  # Weight
            values[3] = height  # Height
            values[4] = bmi  # BMI
            values[5] = experience_level   # Experience
            
            # Create DataFrame using the model's feature names
            print("\n2. Creating input DataFrame...")
            df = pd.DataFrame([values], columns=self.features)

            print("\n3. Finding similar users with KNN...")
            
            scaled_input = self.scaler.transform(df)
            distances, indices = self.knn_model.kneighbors(scaled_input)

            print("\n4. Processing similar users...")
            workout_counts = {'Cardio': 0, 'HIIT': 0, 'Strength': 0, 'Yoga': 0}
            for idx in indices[0]:
                workout_types = self.knn_model._fit_X[idx][-4:]
                if workout_types[0] > 0.5: workout_counts['Cardio'] += 1
                if workout_types[1] > 0.5: workout_counts['HIIT'] += 1
                if workout_types[2] > 0.5: workout_counts['Strength'] += 1
                if workout_types[3] > 0.5: workout_counts['Yoga'] += 1

            recommended_workouts = [k for k, v in sorted(workout_counts.items(), key=lambda x: x[1], reverse=True) if v > 0]
            print(f"\n5. Recommended workouts: {recommended_workouts}")

            predictions = []
            print("\n6. Making predictions for each workout...")
            for workout in recommended_workouts:
                # 复制原始值数组
                pred_values = values.copy()
                
                # 获取workout类型的索引位置
                type_columns = ['Workout_Type_Cardio', 'Workout_Type_HIIT', 
                              'Workout_Type_Strength', 'Workout_Type_Yoga']
                type_indices = [list(self.features).index(col) for col in type_columns]
                
                # 重置所有workout type为0
                for idx in type_indices:
                    pred_values[idx] = 0
                
                # 设置当前workout type为1
                current_type_idx = list(self.features).index(f'Workout_Type_{workout}')
                pred_values[current_type_idx] = 1

                # 创建预测DataFrame
                pred_df = pd.DataFrame([pred_values], columns=self.features)

                # 进行预测
                predicted_avg_bpm = self.rf_avg.predict(pred_df)[0]
                predicted_frequency = self.rf_frequency.predict(pred_df)[0]
                predicted_duration = self.rf_duration.predict(pred_df)[0]
                predicted_water = self.rf_water.predict(pred_df)[0]

                predictions.append({
                    'workout': workout,
                    'avg_bpm': round(predicted_avg_bpm),
                    'frequency': round(predicted_frequency),
                    'duration': round(predicted_duration, 2),
                    'water_intake': round(predicted_water, 2)
                })

            print("\n7. Predictions completed successfully!")
            return {'recommended_workouts': predictions}

        except Exception as e:
            print(f"Error in recommend_workout: {str(e)}")
            print(f"Model features: {self.features}")
            if 'df' in locals():
                print(f"DataFrame columns: {df.columns.tolist()}")
            raise


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

if __name__ == "__main__":
    # 示例使用
    recommender = WorkoutRecommender()
    recommender.load_models('models')  # 替换为你的模型路径
    recommender.print_recommendation(60, 'Male', 80.0, 1.76, 3)



