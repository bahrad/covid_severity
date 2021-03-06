# -*- coding: utf-8 -*-
"""XGBoost Binary Classifier
"""

import numpy as np
import sys
import os
import sklearn as sk
import xgboost as xgb
import pandas as pd

DATA_FILE = sys.argv[1]     # CSV file with features, groups, labels, and indices for which rows to use for training (use -1 or neg. for mask)
FEATURE_NAMES = sys.argv[2] # column header names (treated as strings) to use as features (data in rows, i.e. generated by np.savetxt)
CLASS_LABELS_COL = sys.argv[3]  # column header name (string) to use for class labels (i.e. y)
TRAIN_INDEX_COL = sys.argv[4]   # column header name (string) that has a 1 if that row of features should be used for training
OUTPUT_FILE = sys.argv[5]   # name for model output file (script adds the correct extension)
PRED_FILE = sys.argv[6]     # raw (not rounded) predictions (in rows, no extension will be added)
NUM_EST = int(sys.argv[7])       # no. estimators typical value = 300
MAX_DEPTH = int(sys.argv[8])    # max. depth of tree (typical 5-10)
LEARN_RATE = float(sys.argv[9]) # learning rate (typical 0.01)
REG_LAMBDA = float(sys.argv[10]) # L2 regularization (typical 1.0)
GAMMA = float(sys.argv[11])      # gamma (typical 0)
try:
    RAND_STATE = int(sys.argv[12])
except:
    RAND_STATE = 324

# If any of PREDICT_FILE or OUTPUT_FILE are set to "na",
# then it won't be used

data = pd.read_csv(DATA_FILE)

feature_names = np.loadtxt(FEATURE_NAMES, dtype='str')
x = data[feature_names].values
# mask values that are unavailable -- indicated as negative
x = np.where(x < 0, np.nan, x)
y = data[CLASS_LABELS_COL].values
trainindex_col = data[TRAIN_INDEX_COL].values

trainindex = np.where(trainindex_col == 1)[0]
xtrain = x[trainindex]
ytrain = y[trainindex]

def xgboost_setup():
    return xgb.XGBRegressor(
        objective = "binary:logistic",
        random_state = RAND_STATE,
        subsample = 0.8,    # typically 0.5-1, lower values = more conservative
        reg_lambda = REG_LAMBDA,   # L2 regularization, default 1 (reg_alpha default 0 is L1)
        max_depth= MAX_DEPTH,
        learning_rate = LEARN_RATE,
        gamma = GAMMA,          # makes model more conservative
        colsample_bytree = 0.8, # typically 0.5-1, fraction of columns to be randomly sampled / tree
        eval_metric = 'auc',
        predictor = "cpu_predictor",
        n_jobs = -1,
        n_estimators = NUM_EST,
        importance_type = 'gain',
        )

xgbmodel = xgboost_setup()
xgbmodel.fit(xtrain, ytrain)

if OUTPUT_FILE.lower() != "na":
    xgbmodel.save_model(OUTPUT_FILE+".json")

if PRED_FILE.lower() != "na":
    pred = xgbmodel.predict(x)
    np.savetxt(PRED_FILE, pred)
