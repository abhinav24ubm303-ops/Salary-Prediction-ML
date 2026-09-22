"""
train_model.py
Trains a Scikit-Learn Pipeline with ColumnTransformer and RandomForestRegressor
on the Salary Prediction dataset (1,000 records).
Computes regression metrics, benchmarks, visualizations, and exports model artifacts.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor, _tree
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def tree_to_dict(decision_tree, feature_names, max_depth=3):
    """Recursively converts a scikit-learn decision tree estimator to a JSON dictionary."""
    tree_ = decision_tree.tree_
    def recurse(node, depth):
        if depth >= max_depth or tree_.feature[node] == _tree.TREE_UNDEFINED:
            val = float(tree_.value[node][0][0])
            return {
                "is_leaf": True,
                "value": round(val, 2),
                "samples": int(tree_.n_node_samples[node])
            }
        feat_idx = tree_.feature[node]
        feat_name = feature_names[feat_idx] if feat_idx < len(feature_names) else f"feature_{feat_idx}"
        threshold = float(tree_.threshold[node])
        return {
            "is_leaf": False,
            "feature": feat_name,
            "threshold": round(threshold, 2),
            "samples": int(tree_.n_node_samples[node]),
            "left": recurse(tree_.children_left[node], depth + 1),
            "right": recurse(tree_.children_right[node], depth + 1)
        }
    return recurse(0, 0)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'salary_data.csv')
    
    print(f"[1/6] Loading primary dataset: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"      Rows: {len(df)}, Columns: {len(df.columns)}")
    
    num_cols = ['age', 'experience_years']
    cat_cols = ['education_level', 'job_role', 'location', 'company_size', 'industry', 'remote_work', 'performance_rating']
    target_col = 'salary_lakh'
    
    X = df[num_cols + cat_cols]
    y = df[target_col]
    
    # 80/20 Train-Test split with fixed random_state=42
    print("[2/6] Splitting dataset (80% Train, 20% Test, random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    # Build Scikit-Learn Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', num_cols),
            ('cat', OneHotEncoder(drop=None, sparse_output=False, handle_unknown='ignore'), cat_cols)
        ]
    )
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])
    
    print("[3/6] Fitting RandomForestRegressor Pipeline...")
    pipeline.fit(X_train, y_train)
    
    # Model Evaluation
    y_test_pred = pipeline.predict(X_test)
    r2 = float(r2_score(y_test, y_test_pred))
    mae = float(mean_absolute_error(y_test, y_test_pred))
    mse = float(mean_squared_error(y_test, y_test_pred))
    rmse = float(np.sqrt(mse))
    mape = float(np.mean(np.abs((y_test.values - y_test_pred) / y_test.values)) * 100)
    
    print(f"      Metrics on Test Set (200 records):")
    print(f"      R2 Score : {r2:.4f} ({r2*100:.2f}%)")
    print(f"      MAE      : {mae:.2f} Lakh")
    print(f"      MSE      : {mse:.2f}")
    print(f"      RMSE     : {rmse:.2f} Lakh")
    print(f"      MAPE     : {mape:.2f}%")
    
    # Save Pipeline
    model_save_path = os.path.join(base_dir, 'model', 'salary_rf_pipeline.joblib')
    joblib.dump(pipeline, model_save_path)
    print(f"      Saved trained pipeline to: {model_save_path}")
    
    # Extract feature names & importances
    encoder = pipeline.named_steps['preprocessor'].named_transformers_['cat']
    encoded_cat_names = list(encoder.get_feature_names_out(cat_cols))
    all_feature_names = num_cols + encoded_cat_names
    rf = pipeline.named_steps['regressor']
    raw_importances = rf.feature_importances_
    
    # Granular Feature Importances
    granular_importances = []
    for name, imp in zip(all_feature_names, raw_importances):
        readable = name
        for c in cat_cols:
            if name.startswith(f"{c}_"):
                val = name[len(c)+1:]
                c_title = c.replace('_', ' ').title()
                readable = f"{c_title}: {val}"
                break
        if name == 'experience_years':
            readable = 'Years of Experience'
        elif name == 'age':
            readable = 'Employee Age'
        granular_importances.append({
            "raw_name": name,
            "name": readable,
            "importance_pct": round(float(imp) * 100, 2)
        })
    granular_importances.sort(key=lambda x: x["importance_pct"], reverse=True)
    
    # Aggregated Feature Importances by original feature column
    aggregated_map = {col: 0.0 for col in (num_cols + cat_cols)}
    aggregated_map['experience_years'] += float(raw_importances[all_feature_names.index('experience_years')])
    aggregated_map['age'] += float(raw_importances[all_feature_names.index('age')])
    
    for name, imp in zip(encoded_cat_names, raw_importances[len(num_cols):]):
        for col in cat_cols:
            if name.startswith(f"{col}_"):
                aggregated_map[col] += float(imp)
                break
                
    aggregated_importances = [
        {
            "feature": col,
            "label": col.replace('_', ' ').title(),
            "importance_pct": round(val * 100, 2)
        }
        for col, val in aggregated_map.items()
    ]
    aggregated_importances.sort(key=lambda x: x["importance_pct"], reverse=True)
    
    # Benchmark Comparison Models
    print("[4/6] Computing Benchmark Comparisons for presentation...")
    X_train_enc = preprocessor.transform(X_train)
    X_test_enc = preprocessor.transform(X_test)
    
    benchmarks = {
        "Random Forest Regressor": {
            "r2": round(r2, 4),
            "mae": round(mae, 2),
            "mse": round(mse, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2)
        }
    }
    
    comparison_models = {
        "Decision Tree Regressor": DecisionTreeRegressor(max_depth=10, random_state=42),
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0)
    }
    
    for b_name, b_model in comparison_models.items():
        b_model.fit(X_train_enc, y_train)
        b_preds = b_model.predict(X_test_enc)
        benchmarks[b_name] = {
            "r2": round(float(r2_score(y_test, b_preds)), 4),
            "mae": round(float(mean_absolute_error(y_test, b_preds)), 2),
            "mse": round(float(mean_squared_error(y_test, b_preds)), 2),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, b_preds))), 2),
            "mape": round(float(np.mean(np.abs((y_test.values - b_preds) / y_test.values)) * 100), 2)
        }
        
    # Sample Decision Trees for Tree Inspector
    sample_trees = [
        tree_to_dict(rf.estimators_[i], all_feature_names, max_depth=3)
        for i in range(min(5, len(rf.estimators_)))
    ]
    
    # Actual vs Predicted Scatter Points
    test_indices = list(X_test.index)
    scatter_actual_vs_predicted = []
    for i, idx in enumerate(test_indices):
        orig_row = df.loc[idx]
        act = float(orig_row['salary_lakh'])
        prd = round(float(y_test_pred[i]), 2)
        scatter_actual_vs_predicted.append({
            "id": int(idx),
            "actual": act,
            "predicted": prd,
            "residual": round(act - prd, 2),
            "age": int(orig_row['age']),
            "experience_years": float(orig_row['experience_years']),
            "job_role": str(orig_row['job_role']),
            "education_level": str(orig_row['education_level']),
            "location": str(orig_row['location']),
            "company_size": str(orig_row['company_size']),
            "industry": str(orig_row['industry']),
            "remote_work": str(orig_row['remote_work']),
            "performance_rating": str(orig_row['performance_rating'])
        })
        
    # Dataset Summary Statistics
    num_summary = {}
    for c in ['age', 'experience_years', 'salary_lakh']:
        s = df[c]
        num_summary[c] = {
            "count": int(s.count()),
            "mean": round(float(s.mean()), 2),
            "std": round(float(s.std()), 2),
            "min": round(float(s.min()), 2),
            "q25": round(float(s.quantile(0.25)), 2),
            "median": round(float(s.median()), 2),
            "q75": round(float(s.quantile(0.75)), 2),
            "max": round(float(s.max()), 2)
        }
        
    cat_summary = {}
    for c in cat_cols:
        grouped = df.groupby(c)['salary_lakh'].agg(['count', 'mean', 'median', 'min', 'max']).reset_index()
        cat_summary[c] = [
            {
                "category": str(row[c]),
                "count": int(row['count']),
                "mean_salary": round(float(row['mean']), 2),
                "median_salary": round(float(row['median']), 2),
                "min_salary": round(float(row['min']), 2),
                "max_salary": round(float(row['max']), 2)
            }
            for _, row in grouped.iterrows()
        ]
        cat_summary[c].sort(key=lambda x: x['mean_salary'], reverse=True)
        
    categories_meta = {
        col: sorted(df[col].unique().tolist())
        for col in cat_cols
    }
    
    # 6 Visualizations Datasets
    print("[5/6] Compiling Visualization Datasets...")
    # Chart 1: Experience vs Salary
    exp_vs_salary = [
        {"x": float(r['experience_years']), "y": float(r['salary_lakh']), "role": str(r['job_role']), "age": int(r['age'])}
        for _, r in df.iterrows()
    ]
    
    # Chart 2: Age vs Salary
    age_vs_salary = [
        {"x": int(r['age']), "y": float(r['salary_lakh']), "exp": float(r['experience_years']), "role": str(r['job_role'])}
        for _, r in df.iterrows()
    ]
    
    # Chart 3: Salary by Education Level
    edu_grouped = df.groupby('education_level')['salary_lakh'].agg(['mean', 'median', 'count']).reindex(["High School", "Diploma", "Bachelor's", "Master's", "PhD"]).dropna()
    salary_by_edu = [
        {"education": idx, "mean": round(float(row['mean']), 2), "median": round(float(row['median']), 2), "count": int(row['count'])}
        for idx, row in edu_grouped.iterrows()
    ]
    
    # Chart 4: Salary by Job Role
    role_grouped = df.groupby('job_role')['salary_lakh'].agg(['mean', 'median', 'count']).sort_values(by='mean', ascending=True)
    salary_by_role = [
        {"role": idx, "mean": round(float(row['mean']), 2), "median": round(float(row['median']), 2), "count": int(row['count'])}
        for idx, row in role_grouped.iterrows()
    ]
    
    # Chart 5: Salary by Company Size
    size_order = ['Small', 'Medium', 'Large']
    size_grouped = df.groupby('company_size')['salary_lakh'].agg(['mean', 'median', 'min', 'max', 'count']).reindex(size_order)
    salary_by_size = [
        {"size": idx, "mean": round(float(row['mean']), 2), "median": round(float(row['median']), 2), "min": round(float(row['min']), 2), "max": round(float(row['max']), 2), "count": int(row['count'])}
        for idx, row in size_grouped.iterrows()
    ]
    
    # Chart 6: Salary Distribution (Histogram)
    salary_values = df['salary_lakh'].values
    hist_counts, bin_edges = np.histogram(salary_values, bins=16)
    salary_distribution = [
        {
            "bin_start": round(float(bin_edges[i]), 2),
            "bin_end": round(float(bin_edges[i+1]), 2),
            "count": int(hist_counts[i]),
            "label": f"{round(float(bin_edges[i]), 1)} - {round(float(bin_edges[i+1]), 1)} L"
        }
        for i in range(len(hist_counts))
    ]
    
    payload = {
        "project_info": {
            "title": "Salary Prediction Using Random Forest Regression",
            "subtitle": "Machine Learning Based Salary Prediction System",
            "dataset_rows": len(df),
            "total_features": len(num_cols) + len(cat_cols),
            "num_features_count": len(num_cols),
            "cat_features_count": len(cat_cols),
            "encoded_features_count": len(all_feature_names),
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "target_variable": "salary_lakh",
            "target_unit": "Lakh INR per Annum",
            "problem_type": "Regression",
            "model_type": "Random Forest Regressor",
            "n_estimators": 100,
            "random_state": 42
        },
        "metrics": {
            "r2_score": round(r2, 4),
            "r2_percentage": round(r2 * 100, 2),
            "mae": round(mae, 2),
            "mse": round(mse, 2),
            "rmse": round(rmse, 2),
            "mape": round(mape, 2)
        },
        "benchmarks": benchmarks,
        "aggregated_importances": aggregated_importances,
        "granular_importances": granular_importances,
        "num_summary": num_summary,
        "cat_summary": cat_summary,
        "categories_meta": categories_meta,
        "sample_trees": sample_trees,
        "scatter_actual_vs_predicted": scatter_actual_vs_predicted,
        "visualizations": {
            "exp_vs_salary": exp_vs_salary,
            "age_vs_salary": age_vs_salary,
            "salary_by_edu": salary_by_edu,
            "salary_by_role": salary_by_role,
            "salary_by_size": salary_by_size,
            "salary_distribution": salary_distribution
        },
        "preview_records": df.to_dict(orient='records')[:50]
    }
    
    out_json = os.path.join(base_dir, 'static', 'data', 'model_data.json')
    print(f"[6/6] Writing serialized data to {out_json}...")
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
        
    print(f"Done! Pipeline & Model Data successfully exported. File size: {os.path.getsize(out_json):,} bytes.")

if __name__ == '__main__':
    main()
