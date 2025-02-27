import pandas as pd
import numpy as np
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Lasso, Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectFromModel

stats_url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
salaries_url = 'https://hoopshype.com/salaries/players/2024-2025/'

# Scrape NBA Player stats
def scrape_nba_stats(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'per_game_stats'})
    headers = [th.text for th in table.find('thead').find_all('th')][1:]  # Skip the first empty header
    rows = table.find('tbody').find_all('tr')
    data = []
    for row in rows:
        if row.find('th', {'scope': 'row'}) is not None:
            row_data = [td.text for td in row.find_all('td')]
            data.append(row_data)
    df_stats = pd.DataFrame(data, columns=headers)
    return df_stats

# Scrape NBA player salaries
def scrape_nba_salaries(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'hh-salaries-ranking-table'})
    headers = [th.text for th in table.find('thead').find_all('th')]
    rows = table.find('tbody').find_all('tr')
    data = []
    for row in rows:
        row_data = [td.text.strip() for td in row.find_all('td')]
        data.append(row_data)
    df_salaries = pd.DataFrame(data, columns=headers)
    return df_salaries
    
# Function to predict salary for a new player
# Example usage:
# new_player = {
#     'Age': 25, 'G': 82, 'FG%': 0.480, '3P%': 0.380, '2P%': 0.520,
#     'eFG%': 0.550, 'FT%': 0.850, 'TRB': 6.0, 'AST': 5.0,
#     'STL': 1.5, 'BLK': 0.5, 'PTS': 20.0
# }
# predicted_salary = predict_salary(new_player)
# print(f"Predicted Salary: ${predicted_salary:.2f}")
def predict_salary(new_player_stats):
    new_player_df = pd.DataFrame([new_player_stats])
    new_player_scaled = scaler.transform(new_player_df)
    predicted_salary = model.predict(new_player_scaled)[0]
    return predicted_salary

def stats(): 
    stats = scrape_nba_stats(stats_url)
    stats = stats[["Player", "Age", "G", "FG%", "3P%", "2P%", "eFG%", "FT%", "TRB", "AST", "STL", "BLK", "PTS"]]
    agg_funcs = {'Age': 'max','G': 'sum','FG%': 'mean','3P%': 'mean','2P%': 'mean','eFG%': 'mean','FT%': 'mean',
      'TRB': 'mean','AST': 'mean','STL': 'mean','BLK': 'mean','PTS': 'mean'}
    stats = stats.groupby('Player').agg(agg_funcs).reset_index()
    stats.iloc[:, 1:] = stats.iloc[:, 1:].round(2)
    stats = stats.dropna()
    salary = scrape_nba_salaries(salaries_url)
    salary = salary[["Player", "2024-25"]]
    salary = salary.rename(columns={'2024-25': 'Salary'})
    salary = salary.dropna()
    df = stats.merge(salary, on='Player', how='inner')
    df.dropna(subset=['Salary'])
    df['Salary'] = df['Salary'].replace('[\$,]', '', regex=True).astype(int)
    
    '''data = df.drop(columns=['Player'])
    X = data.drop(columns=['Salary'])
    y = data['Salary']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)'''
    #print(f'Mean Squared Error: {mse}')
    #print(f'R^2 Score: {r2}')
    
    X = data.drop(['Salary'], axis=1)
    y = data['Salary']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Create and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Make predictions on test set
    y_pred = model.predict(X_test_scaled)
    
    # Evaluate model
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = pd.DataFrame({'feature': X.columns, 'importance': model.feature_importances_})
    feature_importance = feature_importance.sort_values('importance', ascending=False)
    
    #Evaluate Results
    data['PTS_per_G'] = data['PTS'] / data['G']
    data['TRB_per_G'] = data['TRB'] / data['G']
    data['AST_per_G'] = data['AST'] / data['G']
    X = data.drop(['Salary'], axis=1)
    y = data['Salary']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    selector = SelectFromModel(RandomForestRegressor(n_estimators=100, random_state=42), threshold='median')
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)
    
    #Try different models
    models = {
    'Random Forest': RandomForestRegressor(random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(random_state=42),
    'Lasso': Lasso(random_state=42),
    'Ridge': Ridge(random_state=42)
    }
    best_model = None
    best_score = 0
    for name, model in models.items():
    # Define parameter grid for each model
    if name == 'Random Forest':
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
    elif name == 'Gradient Boosting':
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 4, 5]
        }
    else:  # Lasso and Ridge
        param_grid = {
            'alpha': [0.1, 1, 10, 100]
        }
        
    #  Grid search
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='r2', n_jobs=-1)
    grid_search.fit(X_train_selected, y_train)
    
    y_pred = grid_search.predict(X_test_selected)
    r2 = r2_score(y_test, y_pred)
    #print(f"{name} - R^2 Score: {r2:.4f}")
    if r2 > best_score:
        best_score = r2
        best_model = grid_search.best_estimator_
    
    #print(f"\nBest model: {type(best_model).__name__}")
    #print(f"Best R^2 Score: {best_score:.4f}")
    
    # Use  best model for final predictions
    y_pred_best = best_model.predict(X_test_selected)
    
    # final metrics
    mse = mean_squared_error(y_test, y_pred_best)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred_best)
    
    print(f"\nFinal Results:")
    print(f"Root Mean Squared Error: ${rmse:.2f}")
    print(f"R-squared Score: {r2:.4f}")
    
    if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': X.columns[selector.get_support()],
        'importance': best_model.feature_importances_
    })
    feature_importance = feature_importance.sort_values('importance', ascending=False)
    print("\nTop 10 Feature Importances:")
    print(feature_importance.head(10))
