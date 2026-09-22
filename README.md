# Salary Prediction Using Random Forest Regression
### Machine Learning Based Employee Salary Prediction System

A complete, professional, interactive Machine Learning web application developed for **Salary Prediction Using Random Forest Regression**. Inspired by the modern interactive architecture of [anoop2101.github.io/Project/](https://anoop2101.github.io/Project/), this project delivers a production-grade, academic presentation-ready platform built around real employee data, empirical Scikit-Learn training pipelines, interactive Chart.js visualizations, and an integrated Classroom Presentation Mode.

---

## 1. Project Highlights & Verified Metrics

- **Real Primary Dataset**: 1,000 employee records across 9 independent features with zero synthetic/hard-coded values.
- **Algorithm**: `RandomForestRegressor` with 100 decision trees via a Scikit-Learn `Pipeline` and `ColumnTransformer`.
- **Reproducible Partitioning**: 80% Training Data (800 records) / 20% Hold-out Testing Data (200 records), `random_state=42`.
- **Validation Metrics (Unseen Test Set)**:
  - **$R^2$ Score**: **0.9828 (98.28% Variance Explained)**
  - **Mean Absolute Error (MAE)**: **₹1.73 Lakh / Year**
  - **Mean Squared Error (MSE)**: **4.77**
  - **Root Mean Squared Error (RMSE)**: **₹2.18 Lakh / Year**
  - **Mean Absolute Percentage Error (MAPE)**: **7.01%**

---

## 2. Dataset Structure

| Column Name | Feature Type | Description & Domain Values |
| :--- | :--- | :--- |
| `age` | Numerical (Discrete) | Employee age in years (Range: 21 to 49, Mean: 33.74) |
| `experience_years` | Numerical (Continuous) | Total career experience in years (Range: 0.0 to 20.0, Mean: 9.94) |
| `education_level` | Categorical | High School, Diploma, Bachelor's, Master's, PhD |
| `job_role` | Categorical | Data Scientist, Software Engineer, Senior Developer, Junior Developer, Data Analyst, Business Analyst, Project Manager, Accountant, HR Specialist, Marketing Executive |
| `location` | Categorical | Bangalore, Chennai, Delhi, Hyderabad, Kochi, Kolkata, Mumbai, Pune |
| `company_size` | Categorical | Small (&lt;50), Medium (50–500), Large (500+) |
| `industry` | Categorical | IT, Finance, Consulting, Manufacturing, Healthcare, Education, Retail |
| `remote_work` | Categorical | No (On-Site/Hybrid), Yes (Fully Remote) |
| `performance_rating` | Categorical | Average, Good, Excellent |
| **`salary_lakh`** | **Target (Continuous)** | **Annual employee salary in Lakh INR (Range: ₹5.36L to ₹65.55L, Mean: ₹29.57L)** |

---

## 3. Project Architecture & Components

```
salary-prediction-rf-app/
├── data/
│   └── salary_data.csv               # Primary dataset (1,000 records × 10 columns)
├── model/
│   └── salary_rf_pipeline.joblib     # Serialized Scikit-Learn Pipeline
├── static/
│   ├── css/
│   │   └── styles.css                # Dark/Light responsive UI styling
│   ├── js/
│   │   ├── app.js                    # Frontend controller & Chart.js renderer
│   │   └── model_data.js             # Pre-loaded model metadata for offline mode
│   └── data/
│       └── model_data.json           # JSON metrics, charts, & sample tree splits
├── templates/
│   └── index.html                    # Jinja2 Flask web template
├── index.html                        # Standalone offline-ready HTML file
├── train_model.py                    # Scikit-Learn training & artifact generation
├── app.py                            # Flask web server & REST API
├── verify_app.py                     # Automated backend verification suite
├── test_js.py                        # Automated frontend syntax verification
└── README.md                         # Project documentation & presentation guide
```

---

## 4. Key Sections & User Experience

1. **Sticky Navigation Bar**:
   - Navigation links: Home, Predict Salary, Model Performance, Dataset, Visualizations, How It Works, Model Details, About.
   - Light/Dark theme toggle with local storage persistence.
   - **Presentation Mode** button launching the interactive slideshow.
2. **Interactive Prediction Form**:
   - Synchronized sliders and numeric boxes for Age and Years of Experience.
   - Dropdown selections dynamically populated from the dataset.
   - Real-time client-side validation (e.g. checking age vs. experience consistency).
   - Instant calculation of **Predicted Annual Salary (₹ XX.XX Lakh)**, **Approximate Monthly Salary (₹ XX,XXX)**, and 95% Confidence Interval across the 100 individual decision trees.
3. **Model Evaluation & Benchmarking**:
   - Attractive metric cards with definitions, units, and interpretation.
   - Comparative benchmark table displaying Random Forest vs. Decision Tree vs. Linear Regression vs. Ridge Regression.
4. **Dataset Explorer**:
   - Summary statistics cards: 1,000 records, 9 features, 2 numerical, 7 categorical.
   - Searchable, filterable, sortable, and paginated table (10, 25, 50 rows per page).
5. **6 Interactive Data Visualizations**:
   - **Chart 1**: Experience vs. Salary (Scatter Plot with trend)
   - **Chart 2**: Age vs. Salary (Scatter Plot)
   - **Chart 3**: Salary by Education Level (Bar Chart)
   - **Chart 4**: Salary by Job Role (Ranked Bar Chart)
   - **Chart 5**: Salary by Company Size (Grouped Bar Chart)
   - **Chart 6**: Salary Distribution (16-Bin Histogram)
6. **Actual vs. Predicted Salary Scatter**:
   - Visual comparison of actual salary vs. predicted salary on the 20% test dataset (200 records).
   - $45^\circ$ diagonal dashed reference line ($y = x$) demonstrating high fit.
7. **Feature Importance (Aggregated & Granular)**:
   - Horizontal bar chart with toggle between Business View (Parent Factors) and Technical View (One-Hot Encoded Levels).
8. **Interactive Tree Inspector & Random Forest Explanation**:
   - Step-by-step visual diagram explaining bootstrap aggregation (bagging).
   - Visual inspector allowing students to inspect sample tree nodes, feature split thresholds, and leaf values.
9. **Live Retraining Experimenter**:
   - Interactive sliders to modify number of trees ($N$) and test split ratio to demonstrate live accuracy changes.
10. **Classroom Presentation Mode**:
    - Full-screen 8-slide presentation walkthrough tailored for B.Com Business Analytics and academic vivas.
11. **Text-to-Speech Voice Narration**:
    - Web Speech API integration allowing listeners to hear audio explanations for each section.

---

## 5. How to Run the Application

### Option A: Run with Python Flask Server (Recommended)

1. Open PowerShell or Terminal in the project directory:
   ```powershell
   cd C:\Users\abhin\.gemini\antigravity\scratch\salary-prediction-rf-app
   ```
2. Start the Flask application:
   ```powershell
   python app.py
   ```
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Option B: Open as Standalone Offline Application

You can also directly open `index.html` in any modern web browser (Google Chrome, Microsoft Edge, etc.) without starting any server:
```powershell
Start-Process "C:\Users\abhin\.gemini\antigravity\scratch\salary-prediction-rf-app\index.html"
```
The application will automatically use its pre-loaded metadata (`model_data.js`) and client-side inference engine!

---

## 6. How to Run Automated Verification Tests

To verify that the model pipeline, API endpoints, metrics, and frontend scripts are working correctly:

```powershell
python verify_app.py
python test_js.py
```

Expected output:
```
ALL BACKEND AUTOMATED TESTS PASSED SUCCESSFULLY!
app.js syntax balance verification: PASS!
```

---

## 7. Viva Q&A Guide (For B.Com Business Analytics Students)

- **Q1: Why is this a regression problem and not a classification problem?**
  - *Answer*: "The target variable, salary (`salary_lakh`), is a continuous numerical value measured on a continuous monetary scale. Classification predicts categorical labels (e.g. Approved/Rejected), whereas regression models predict continuous quantities."
- **Q2: Why choose Random Forest over a single Decision Tree or Linear Regression?**
  - *Answer*: "A single decision tree tends to overfit and has high variance. Linear regression assumes a strictly linear relationship and struggles with non-linear feature interactions. Random Forest constructs an ensemble of 100 trees using bootstrap sampling and random feature selection, averaging out individual tree errors to achieve a 98.28% $R^2$ score."
- **Q3: What does an $R^2$ score of 0.9828 mean?**
  - *Answer*: "It means that 98.28% of the variation in employee salaries in the test set is explained by the 9 features in our model. Only 1.72% of the variation is due to unobserved factors or random noise."
- **Q4: What is the most critical feature in predicting salary?**
  - *Answer*: "Feature importance analysis proves that `experience_years` accounts for over 97% of tree split purity, followed by `job_role` (specialized roles like Data Scientist and Project Manager command significant premiums) and `education_level`."

---

*Random Forest Regression – Salary Prediction | Machine Learning Project*
