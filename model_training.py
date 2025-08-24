import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_absolute_error

def load_data(path):
    df = pd.read_csv(path, parse_dates=['occurred_at'])
    return df

def engineer_features(df):
    df['hour'] = df['occurred_at'].dt.hour
    df['dow'] = df['occurred_at'].dt.dayofweek
    df['month'] = df['occurred_at'].dt.month
    df['day'] = df['occurred_at'].dt.day
    df['is_weekend'] = df['dow'].isin([5,6]).astype(int)
    # Hotspot label for classification (top 15% cells become 1)
    grid_counts = df.groupby(['grid_x','grid_y']).size().reset_index(name='cnt')
    thresh = np.quantile(grid_counts['cnt'], 0.85)
    grid_counts['hotspot'] = (grid_counts['cnt'] >= thresh).astype(int)
    df = df.merge(grid_counts[['grid_x','grid_y','hotspot']], on=['grid_x','grid_y'], how='left')
    return df

def train_models(df):
    features = ['hour','dow','month','day','is_weekend','grid_x','grid_y','severity','weapon_used','arrested']
    df['weapon_used'] = df['weapon_used'].astype(int)
    df['arrested'] = df['arrested'].astype(int)

    # Classification: predict hotspot (1/0)
    cls_df = df.copy().dropna(subset=['hotspot'])
    Xc = cls_df[features]
    yc = cls_df['hotspot']
    Xc_train, Xc_test, yc_train, yc_test = train_test_split(Xc, yc, test_size=0.2, random_state=42, stratify=yc)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(Xc_train, yc_train)
    yc_pred = clf.predict(Xc_test)
    cls_report = classification_report(yc_test, yc_pred, output_dict=True)

    # Regression: predict crimes per grid-day
    agg = df.groupby(['date_key','grid_x','grid_y']).size().reset_index(name='count')
    agg['dow'] = pd.to_datetime(agg['date_key']).dt.dayofweek
    agg['month'] = pd.to_datetime(agg['date_key']).dt.month
    agg['day'] = pd.to_datetime(agg['date_key']).dt.day
    agg['is_weekend'] = agg['dow'].isin([5,6]).astype(int)
    Xr = agg[['dow','month','day','is_weekend','grid_x','grid_y']]
    yr = agg['count']
    Xr_train, Xr_test, yr_train, yr_test = train_test_split(Xr, yr, test_size=0.2, random_state=42)
    rgr = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
    rgr.fit(Xr_train, yr_train)
    yr_pred = rgr.predict(Xr_test)
    mae = mean_absolute_error(yr_test, yr_pred)

    return clf, rgr, cls_report, mae

def predict_next_week(rgr, last_date):
    future_dates = pd.date_range(pd.to_datetime(last_date)+pd.Timedelta(days=1), periods=7)
    grid = [(x,y) for x in range(10) for y in range(10)]
    rows = []
    for d in future_dates:
        dow = d.dayofweek
        month = d.month
        day = d.day
        is_weekend = int(dow in [5,6])
        for (gx,gy) in grid:
            rows.append([dow,month,day,is_weekend,gx,gy,d])
    fut = pd.DataFrame(rows, columns=['dow','month','day','is_weekend','grid_x','grid_y','date'])
    fut['predicted_count'] = rgr.predict(fut[['dow','month','day','is_weekend','grid_x','grid_y']])
    return fut

if __name__ == '__main__':
    path = os.environ.get('CRIME_CSV','crime_jun_jul_2024.csv')
    df = load_data(path)
    df = engineer_features(df)
    clf, rgr, cls_report, mae = train_models(df)
    fut = predict_next_week(rgr, df['date_key'].max())
    print('Classification F1 (macro):', cls_report['macro avg']['f1-score'])
    print('Regression MAE:', mae)
    fut.to_csv('predicted_grid_next_week.csv', index=False)