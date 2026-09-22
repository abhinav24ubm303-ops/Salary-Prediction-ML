"""
app.py - Flask Web Backend for Salary Prediction Machine Learning System
Provides full REST API and serves the modern interactive user interface.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'salary_data.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'salary_rf_pipeline.joblib')
JSON_DATA_PATH = os.path.join(BASE_DIR, 'static', 'data', 'model_data.json')

app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

# Load raw dataset
raw_df = pd.read_csv(DATA_PATH)

# Load cached model metadata
with open(JSON_DATA_PATH, 'r', encoding='utf-8') as f:
    model_metadata = json.load(f)

# Load trained pipeline
pipeline = joblib.load(MODEL_PATH)
rf_regressor = pipeline.named_steps['regressor']
preprocessor = pipeline.named_steps['preprocessor']

NUM_COLS = ['age', 'experience_years']
CAT_COLS = ['education_level', 'job_role', 'location', 'company_size', 'industry', 'remote_work', 'performance_rating']

@app.route('/')
def index():
    """Renders the main single-page interactive application."""
    return render_template('index.html', model_data=model_metadata)

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Returns the full project metadata, metrics, and chart data."""
    return jsonify(model_metadata)

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Returns model performance metrics and benchmarks."""
    return jsonify({
        "metrics": model_metadata["metrics"],
        "benchmarks": model_metadata["benchmarks"],
        "project_info": model_metadata["project_info"]
    })

@app.route('/api/predict', methods=['POST'])
def predict_salary():
    """
    Accepts employee features, executes Scikit-Learn Random Forest Pipeline,
    and returns predicted salary, monthly breakdown, and tree ensemble statistics.
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload received"}), 400

        # Validate inputs
        try:
            age = float(data.get('age', 30))
            exp = float(data.get('experience_years', 5))
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Age and Experience must be valid numbers"}), 400

        if age < 18 or age > 75:
            return jsonify({"status": "error", "message": "Age must be between 18 and 75 years."}), 400
        if exp < 0 or exp > 50:
            return jsonify({"status": "error", "message": "Years of Experience must be between 0 and 50."}), 400
        if age < (exp + 16):
            return jsonify({
                "status": "error",
                "message": f"Validation Warning: Age ({int(age)}) is too low for {exp:.1f} years of experience (assumes starting work at 16+)."
            }), 400

        education = str(data.get('education_level', "Bachelor's")).strip()
        job_role = str(data.get('job_role', 'Data Scientist')).strip()
        location = str(data.get('location', 'Bangalore')).strip()
        company_size = str(data.get('company_size', 'Medium')).strip()
        industry = str(data.get('industry', 'IT')).strip()
        remote_work = str(data.get('remote_work', 'No')).strip()
        performance_rating = str(data.get('performance_rating', 'Good')).strip()

        # Build DataFrame with proper column order
        input_dict = {
            'age': [age],
            'experience_years': [exp],
            'education_level': [education],
            'job_role': [job_role],
            'location': [location],
            'company_size': [company_size],
            'industry': [industry],
            'remote_work': [remote_work],
            'performance_rating': [performance_rating]
        }
        df_input = pd.DataFrame(input_dict)

        # Primary Pipeline Prediction
        pred_array = pipeline.predict(df_input)
        predicted_annual_lakh = float(pred_array[0])
        predicted_annual_lakh = max(3.0, round(predicted_annual_lakh, 2))

        # Monthly Salary Calculation
        monthly_inr = int(round((predicted_annual_lakh * 100000.0) / 12.0))

        # Individual Decision Trees for Ensemble Consensus
        transformed_input = preprocessor.transform(df_input)
        tree_predictions = [float(tree.predict(transformed_input)[0]) for tree in rf_regressor.estimators_]

        mean_tree = float(np.mean(tree_predictions))
        std_tree = float(np.std(tree_predictions))
        min_tree = float(np.min(tree_predictions))
        max_tree = float(np.max(tree_predictions))
        ci_lower = max(2.5, round(mean_tree - 1.96 * std_tree, 2))
        ci_upper = round(mean_tree + 1.96 * std_tree, 2)

        return jsonify({
            "status": "success",
            "predicted_annual_lakh": predicted_annual_lakh,
            "approx_monthly_inr": monthly_inr,
            "approx_monthly_formatted": f"₹{monthly_inr:,}",
            "predicted_annual_formatted": f"₹ {predicted_annual_lakh:.2f} Lakh / Year",
            "model_name": "Random Forest Regressor (Scikit-Learn Pipeline)",
            "ensemble_stats": {
                "total_trees": len(rf_regressor.estimators_),
                "mean_tree_lakh": round(mean_tree, 2),
                "std_deviation": round(std_tree, 2),
                "min_tree_lakh": round(min_tree, 2),
                "max_tree_lakh": round(max_tree, 2),
                "ci_95": [ci_lower, ci_upper],
                "sample_tree_preds": [round(p, 2) for p in tree_predictions[:15]]
            },
            "input_summary": {
                "age": int(age),
                "experience_years": exp,
                "education_level": education,
                "job_role": job_role,
                "location": location,
                "company_size": company_size,
                "industry": industry,
                "remote_work": remote_work,
                "performance_rating": performance_rating
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    """
    Searchable, filterable, sortable, and paginated dataset records.
    """
    try:
        page = max(1, int(request.args.get('page', 1)))
        page_size = min(100, max(5, int(request.args.get('page_size', 10))))
        search_query = request.args.get('q', '').strip().lower()
        role_filter = request.args.get('role', '').strip()
        location_filter = request.args.get('location', '').strip()
        edu_filter = request.args.get('education', '').strip()
        sort_col = request.args.get('sort_col', '').strip()
        sort_dir = request.args.get('sort_dir', 'asc').strip().lower()

        df_filtered = raw_df.copy()

        if search_query:
            mask = (
                df_filtered['job_role'].str.lower().str.contains(search_query) |
                df_filtered['location'].str.lower().str.contains(search_query) |
                df_filtered['industry'].str.lower().str.contains(search_query) |
                df_filtered['education_level'].str.lower().str.contains(search_query)
            )
            df_filtered = df_filtered[mask]

        if role_filter:
            df_filtered = df_filtered[df_filtered['job_role'] == role_filter]
        if location_filter:
            df_filtered = df_filtered[df_filtered['location'] == location_filter]
        if edu_filter:
            df_filtered = df_filtered[df_filtered['education_level'] == edu_filter]

        if sort_col and sort_col in df_filtered.columns:
            ascending = (sort_dir == 'asc')
            df_filtered = df_filtered.sort_values(by=sort_col, ascending=ascending)

        total_records = len(df_filtered)
        total_pages = max(1, int(np.ceil(total_records / page_size)))
        start_idx = (page - 1) * page_size
        end_idx = min(total_records, start_idx + page_size)

        records = df_filtered.iloc[start_idx:end_idx].to_dict(orient='records')

        return jsonify({
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "records": records
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    """Returns the 6 visualization datasets and actual vs predicted scatter points."""
    return jsonify({
        "visualizations": model_metadata["visualizations"],
        "scatter_actual_vs_predicted": model_metadata["scatter_actual_vs_predicted"],
        "aggregated_importances": model_metadata["aggregated_importances"],
        "granular_importances": model_metadata["granular_importances"]
    })

@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """
    Classroom live experimentation endpoint:
    Allows changing number of trees and test split ratio live to see how metrics change.
    """
    global pipeline, rf_regressor, preprocessor
    try:
        data = request.get_json(force=True) or {}
        n_estimators = int(data.get('n_estimators', 100))
        test_size = float(data.get('test_size', 0.20))
        max_depth = int(data.get('max_depth', 0)) or None

        if n_estimators < 10 or n_estimators > 300:
            return jsonify({"status": "error", "message": "Number of trees must be between 10 and 300."}), 400
        if test_size < 0.1 or test_size > 0.4:
            return jsonify({"status": "error", "message": "Test size must be between 10% and 40%."}), 400

        X = raw_df[NUM_COLS + CAT_COLS]
        y = raw_df['salary_lakh']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        new_preprocessor = ColumnTransformer(
            transformers=[
                ('num', 'passthrough', NUM_COLS),
                ('cat', OneHotEncoder(drop=None, sparse_output=False, handle_unknown='ignore'), CAT_COLS)
            ]
        )

        new_pipeline = Pipeline(steps=[
            ('preprocessor', new_preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1))
        ])

        new_pipeline.fit(X_train, y_train)
        y_test_pred = new_pipeline.predict(X_test)

        r2 = float(r2_score(y_test, y_test_pred))
        mae = float(mean_absolute_error(y_test, y_test_pred))
        mse = float(mean_squared_error(y_test, y_test_pred))
        rmse = float(np.sqrt(mse))

        # Update active pipeline
        pipeline = new_pipeline
        rf_regressor = new_pipeline.named_steps['regressor']
        preprocessor = new_pipeline.named_steps['preprocessor']

        return jsonify({
            "status": "success",
            "message": f"Successfully retrained with {n_estimators} trees on {int((1-test_size)*100)}% training data!",
            "n_estimators": n_estimators,
            "test_size_pct": int(test_size * 100),
            "train_size_pct": int((1 - test_size) * 100),
            "metrics": {
                "r2_score": round(r2, 4),
                "r2_percentage": round(r2 * 100, 2),
                "mae": round(mae, 2),
                "mse": round(mse, 2),
                "rmse": round(rmse, 2)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Retraining failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("=" * 70)
    print(" [Antigravity] Salary Prediction Machine Learning Web System")
    print(" Server Running at: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(debug=True, host='127.0.0.1', port=5000)
