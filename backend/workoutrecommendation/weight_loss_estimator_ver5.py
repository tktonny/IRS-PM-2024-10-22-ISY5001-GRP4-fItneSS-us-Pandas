import pandas as pd
import tensorflow as tf
import joblib
import math
import os
import json

class WeightLossEstimator:
    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 构建模型文件的完整路径
        model_path = os.path.join(current_dir, 'calories_prediction_model.keras')
        preprocessor_path = os.path.join(current_dir, 'preprocessor.joblib')

        # 添加调试信息
        print(f"Attempting to load model from: {model_path}")
        print(f"Attempting to load preprocessor from: {preprocessor_path}")

        if os.path.exists(model_path):
            print("Model file found")
        else:
            print("Model file not found")

        if os.path.exists(preprocessor_path):
            print("Preprocessor file found")
        else:
            print("Preprocessor file not found")

        # 加载模型和预处理器
        self.model = tf.keras.models.load_model(model_path)
        self.preprocessor = joblib.load(preprocessor_path)

        self.activities = [
            {'name': 'Walking', 'intensity': 0.5},
            {'name': 'Jogging', 'intensity': 0.7},
            {'name': 'Swimming', 'intensity': 0.6},
            {'name': 'Sit_ups', 'intensity': 0.6},
            {'name': 'Squats', 'intensity': 0.65},
            {'name': 'Jumping_Jacks', 'intensity': 0.7}
        ]

        self.mixed_plan = [
            ('Jumping_Jacks', 2),
            ('Jogging', 2),
            ('Swimming', 1),
            ('Walking', 1),
            ('Sit_ups', 1)
        ]

    def predict_calories(self, gender, age, height, weight, heart_rate):
        input_data = pd.DataFrame({
            'Gender': [gender],
            'Age': [age],
            'Height': [height],
            'Weight': [weight],
            'Duration': [30],  # Fixed at 30 minutes
            'Heart_Rate': [heart_rate]
        })
        input_preprocessed = self.preprocessor.transform(input_data)
        return self.model.predict(input_preprocessed, verbose=0)[0][0]

    def calculate_target_heart_rate(self, age, intensity):
        max_heart_rate = 220 - age
        target_heart_rate = max_heart_rate * intensity
        return round(target_heart_rate)

    def calculate_bmr(self, gender, weight, height, age):
        if gender.lower() == 'male':
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    def estimate_weight_loss_time(self, gender, age, height, current_weight, target_weight):
        weight_to_lose = current_weight - target_weight
        if weight_to_lose <= 0:
            return "You've already reached or exceeded your target weight!", [], None

        daily_calorie_intake = 2000 if gender.lower() == 'male' else 1500
        single_activity_results = []
        mixed_plan_result = None

        # 单项运动估算
        for activity in self.activities:
            result = self.calculate_single_activity(gender, age, height, current_weight, target_weight, activity, daily_calorie_intake)
            single_activity_results.append(result)

        # 混合运动计划估算
        mixed_plan_result = self.calculate_mixed_plan(gender, age, height, current_weight, target_weight, daily_calorie_intake)

        return f"You need to lose {weight_to_lose:.1f} kg to reach your target weight.", single_activity_results, mixed_plan_result

    def calculate_single_activity(self, gender, age, height, current_weight, target_weight, activity, daily_calorie_intake):
        heart_rate = self.calculate_target_heart_rate(age, activity['intensity'])
        
        weight = current_weight
        total_days = 0
        previous_sets = 0
        stages = []

        initial_calories = self.predict_calories(gender, age, height, current_weight, heart_rate)

        while weight > target_weight:
            bmr = self.calculate_bmr(gender, weight, height, age)
            calorie_difference = daily_calorie_intake - bmr

            calories_per_session = self.predict_calories(gender, age, height, weight, heart_rate)
            sets_needed = math.ceil(calorie_difference / calories_per_session) + 4

            if sets_needed != previous_sets or weight == current_weight:
                if stages:
                    stages[-1]['days'] = total_days - stages[-1]['start_day']
                stages.append({
                    'weight': round(weight, 1),
                    'minutes': sets_needed * 30,  # Convert sets to minutes
                    'start_day': total_days
                })
                previous_sets = sets_needed

            calories_burned = calories_per_session * sets_needed
            net_calorie_loss = calories_burned - calorie_difference
            weight_loss = net_calorie_loss / 7700  # Approximate calories per kg of fat
            weight -= weight_loss
            total_days += 1

        if stages:
            stages[-1]['days'] = total_days - stages[-1]['start_day']

        return {
            'name': activity['name'],
            'heart_rate': heart_rate,
            'total_days': total_days,
            'stages': stages,
            'initial_calories': initial_calories
        }

    def calculate_mixed_plan(self, gender, age, height, current_weight, target_weight, daily_calorie_intake):
        weight = current_weight
        total_days = 0
        previous_sets = 0
        stages = []
        initial_calories = {}
        heart_rates = {}

        while weight > target_weight:
            bmr = self.calculate_bmr(gender, weight, height, age)
            calorie_difference = daily_calorie_intake - bmr

            weekly_calories_burned = 0
            for activity_name, days in self.mixed_plan:
                activity = next(a for a in self.activities if a['name'] == activity_name)
                if activity_name not in heart_rates:
                    heart_rates[activity_name] = self.calculate_target_heart_rate(age, activity['intensity'])
                heart_rate = heart_rates[activity_name]
                calories_per_session = self.predict_calories(gender, age, height, weight, heart_rate)
                
                if weight == current_weight:
                    initial_calories[activity_name] = calories_per_session

                weekly_calories_burned += calories_per_session * days

            daily_calories_burned = weekly_calories_burned / 7
            sets_needed = math.ceil(calorie_difference / daily_calories_burned) + 4

            if sets_needed != previous_sets or weight == current_weight:
                if stages:
                    stages[-1]['days'] = total_days - stages[-1]['start_day']
                stages.append({
                    'weight': round(weight, 1),
                    'minutes': sets_needed * 30,  # Convert sets to minutes
                    'start_day': total_days
                })
                previous_sets = sets_needed

            net_calorie_loss = (daily_calories_burned * sets_needed) - calorie_difference
            weight_loss = (net_calorie_loss * 7) / 7700  # Approximate calories per kg of fat
            weight -= weight_loss
            total_days += 7

        if stages:
            stages[-1]['days'] = total_days - stages[-1]['start_day']

        return {
            'name': 'Mixed_Plan',
            'total_days': total_days,
            'stages': stages,
            'initial_calories': initial_calories,
            'plan': dict(self.mixed_plan),
            'heart_rates': heart_rates
        }

    def get_estimate_object(self, gender, age, height, current_weight, target_weight):
        message, single_results, mixed_plan = self.estimate_weight_loss_time(gender, age, height, current_weight, target_weight)
        
        # Prepare single plan activities
        single_plan_activities = []
        for result in single_results:
            single_plan_activities.append({
                "name": result['name'],
                "heart_rate": result['heart_rate'],
                "total_days": result['total_days'],
                "stages": [
                    {
                        "weight": stage['weight'],
                        "minutes": stage['minutes'],
                        "start_day": stage['start_day'],
                        "days": stage.get('days', 0)  # Ensure 'days' is always present
                    } for stage in result['stages']
                ],
                "initial_calories": result['initial_calories']
            })

        # Prepare mixed plan
        mixed_plan_data = {
            "name": mixed_plan['name'],
            "total_days": mixed_plan['total_days'],
            "stages": [
                {
                    "weight": stage['weight'],
                    "minutes": stage['minutes'],
                    "start_day": stage['start_day'],
                    "days": stage.get('days', 0)  # Ensure 'days' is always present
                } for stage in mixed_plan['stages']
            ],
            "initial_calories": mixed_plan['initial_calories'],
            "plan": mixed_plan['plan'],
            "heart_rates": mixed_plan['heart_rates']
        }

        return {
            'message': message,
            'input_params': {
                'gender': gender,
                'age': age,
                'height': height,
                'current_weight': current_weight,
                'target_weight': target_weight
            },
            'single_plan': {
                'description': "Estimated results for individual exercises",
                'activities': single_plan_activities
            },
            'mixed_plan': {
                'description': "Estimated result for combined exercise plan",
                'plan': [mixed_plan_data]  # Wrap in a list to match the Swift structure
            }
        }

    def print_estimate(self, estimate):
        print(json.dumps(estimate, indent=2))

# 使用示例
if __name__ == "__main__":
    estimator = WeightLossEstimator()
    estimate = estimator.get_estimate_object('Male', 30, 165, 100, 70)
    estimator.print_estimate(estimate)