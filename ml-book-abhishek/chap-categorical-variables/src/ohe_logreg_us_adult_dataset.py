# Apply Logisitc Regression on One-Hot Encoded features
# Note that, features has to normalized/converted to standard form e.g one hot encoding

# dataset used: us_adult_dataset

import pandas as pd

from sklearn import linear_model
from sklearn import metrics
from sklearn import preprocessing

def run(fold):

    df = pd.read_csv("../../data/adult_folds.csv", sep=",")

    # print(df[df.target.values == 1].shape)
    # print(df[df.target.values == 0].shape)
    
    # numerical cols (for now lets drop numerical cols)
    num_cols = [
        "fnlwgt",
        "age",
        "capital-gain",
        "capital-loss",
        "hours-per-week"
    ]

    # drop numerical cols
    df = df.drop(num_cols, axis=1)

    # map targets to 0s and 1s
    target_mapping = {
        "<=50K": 0,
        ">50K": 1
    }

    df.loc[:, "income"] = df.income.map(target_mapping)

    # print(df[df.income == 1].shape)
    # all cols are features except incomde and kfold columns
    features = [feature for feature in df.columns if feature not in ["income", "kfold"]]

    # fill all nan with None
    # convert all feature to string type as all are categorical

    for feature in features:
        df.loc[:, feature] = df[feature].astype(str).fillna("NONE")

    # get train and valid data
    df_train = df[df.kfold != fold].reset_index(drop=True)
    df_valid = df[df.kfold == fold].reset_index(drop=True)

    # print(df_train.shape)
    # print(df_valid.shape)

    # initialize OneHotEncoder
    ohe = preprocessing.OneHotEncoder(sparse=True)

    # fit ohe on both train and test
    full_data = pd.concat([df_train[features], 
                                df_valid[features]],
                                axis=0)
    # print(f" full data after concatenating {full_data.shape}")

    ohe.fit(full_data[features])

    # transform train and valid data
    # print(f"df_train[features] {df_train[features].shape}")
    x_train = ohe.transform(df_train[features])
    # print(x_train["ord_2"])
    
    x_valid = ohe.transform(df_valid[features])

    # initialize LR Model
    model = linear_model.LogisticRegression()

    # fit/train model
    model.fit(x_train, df_train.income.values)

    # prediction on validation data
    # we need the probs. as we are calculating AUC 
    # we will use probs. of 1s
    print(model.predict_proba(x_valid))
    valid_preds = model.predict_proba(x_valid)[:, 1]
    
    # print(f"valid pred {valid_preds}")
    # get roc auc score
    auc = metrics.roc_auc_score(df_valid.income.values, valid_preds)

    print(f"fold : {fold} auc : {auc}")
    
    return auc

if __name__ == "__main__":
    
    average_auc_score = 0
    total_folds = 5
    for fold in range(total_folds):
        average_auc_score += run(fold=fold)

    print(f"Average auc score {average_auc_score/total_folds}")