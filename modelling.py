from typing import Tuple
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score
import shap
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from data_request import pull_data, create_postgres_engine


def preprocess_hr_data(df : pd.DataFrame) ->Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series] :
    """Preprocesses the IBM HR dataset, and returns training and testing for input and output variables. Currently only designated the Attrition variable as output.
    TODO: Changeable output variable
    :args
    - df : input dataset pulled from DB or downloaded from source
    :returns
    - pd.DataFrame : stratified train input variables (80% of data) 
    - pd.DataFrame : stratified test input variables (20% of data)
    - pd.Series : stratified train output variable (80%)
    - pd.Series : stratified test output variable (20%)
    """
    df.dropna(how= "any", axis="index", inplace=True)
    ind = df.loc[:,"EmployeeNumber"] ## TODO: UI should take this as a basis for querying data.
    df.drop(columns="EmployeeNumber", inplace=True)
    y = df.loc[:, "Attrition"]
    df.drop(columns ="Attrition", inplace=True)
    y.loc[y == "Yes"] = 1
    y.loc[y == "No"] = 0
    y = y.astype(int) ## for xgboost
    
    cat_vars= df.dtypes == "object"
    names = [i for i in cat_vars.index if cat_vars[i]]
    for i in names:
        df[i] = df[i].astype("category")
        ## TODO: better data preprocessing

    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2)
    
    return X_train, X_test, y_train, y_test


def create_heatmap(X_train, y_train):
    """Creates a heatmap to check correlations out. Since there is a lot of categorical variable, this is hard to interpret.
    Returns matplotlib axes for the heatmap."""
    return sns.heatmap(pd.concat((X_train.loc[:, X_train.dtypes == int], y_train), axis="columns").corr())
    

def create_classification_model_xgboost(X_train : pd.DataFrame, y_train : pd.Series) -> xgb.XGBClassifier:
    """Trains an XGBboost classifier with scikit gridsearch so that we do not have to 'manually' optimize the model (AutoML approach).
    :args
        X_train : input variables (preferably from preprocess_hr_data)
        y_train : corresponding values of the output variable (preferably from preprocess_hr_data)
        
    :returns
    xgb.XGBClassifier : Preferably usable classifier.
    """
    param_grid = {
    'max_depth': [3, 5, 7],
    'learning_rate': [0.1, 0.01, 0.001],
    'subsample': [0.5, 0.7, 1]
    }
    clf = GridSearchCV(estimator=xgb.XGBClassifier(enable_categorical=True), 
                            param_grid=param_grid, 
                            cv=5,  # 5-fold cross-validation
                            scoring='accuracy')
    clf.fit(X_train, y_train)
    model = clf.best_estimator_
    print(f"Accuracy: {clf.best_score_}" )
    return model

def check_model(model, X_test, y_test, threshold = 0.8) -> bool:
    """Checks if the prediction is accurate. User must give a threshold value."""
    y_hat = model.predict(X_test)
    return accuracy_score(y_test, y_hat) > threshold


def calculate_shap_values(model, X)-> shap.Explanation:
    """Returns the shapley value to explain xgboost classifier model."""
    exp = shap.TreeExplainer(model)
    explainer = exp(X) 
    return explainer


if __name__ == "__main__":
    
    engine = create_postgres_engine()
    data = pull_data(engine)
    
