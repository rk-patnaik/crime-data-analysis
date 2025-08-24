import pandas as pd
import numpy as np

def assign_to_grid(df, x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0, nx=10, ny=10):
    df = df.copy()
    x_scaled = np.clip(((df['lon']-x_min)/(x_max-x_min))*nx, 0, nx-1-1e-8)
    y_scaled = np.clip(((df['lat']-y_min)/(y_max-y_min))*ny, 0, ny-1-1e-8)
    df['grid_x'] = x_scaled.astype(int)
    df['grid_y'] = y_scaled.astype(int)
    return df

if __name__ == '__main__':
    df = pd.read_csv('crime_jun_jul_2024.csv', parse_dates=['occurred_at'])
    df = assign_to_grid(df)
    df.to_csv('crime_jun_jul_2024_gridded.csv', index=False)