# -*- coding: utf-8 -*-
"""Kaggle_Titanic.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lHCc3xa4KP_VyHyjIyEo5mEb8REMsrC9
"""

# Imports
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import make_column_transformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

# Read in the train and test datasets
test_pd = pd.read_csv("https://raw.githubusercontent.com/jrdowns/Kaggle_Titanic/main/test.csv")
train_pd = pd.read_csv("https://raw.githubusercontent.com/jrdowns/Kaggle_Titanic/main/train.csv")

# Dropping characteristics I'm assuming wouldn't be deterministic
train_pd_pruned = train_pd.drop(['Name', 'Ticket', 'Cabin'], axis=1)
test_pd_pruned = test_pd.drop(['Name', 'Ticket', 'Cabin'], axis=1)
# There's nan values in our data set. We can us Pandas fillna() to replace them with zeros
train_pd_pruned = train_pd_pruned.fillna(0)
test_pd_pruned = test_pd_pruned.fillna(0)
train_pd_pruned.head()

# Something the 'Sex' or 'Embarked' column is not an int or string.
# It's making the OneHotEncoder error out. How to fix?
train_pd_pruned = train_pd_pruned.astype({'Sex': 'string', 'Embarked': 'string'})
test_pd_pruned = test_pd_pruned.astype({'Sex': 'string', 'Embarked': 'string'})
train_pd_pruned.dtypes

"""Both the 'Sex' and 'Embarked' columns were type 'object'.
I guess one of the entries in one of the columns was not a string or int.
OneHotEncoder will only work on string and int.
Since they're obviously supposed to be strings, I just converted them with .astype.
Seems to have worked.
"""

# Create a column transformer to normalize data and onehot encode
ct = make_column_transformer(
    (MinMaxScaler(), ['PassengerId', 'Pclass', 'Age', 'Fare']),
    (OneHotEncoder(handle_unknown="ignore"),["Sex", "Embarked"]),
    remainder = 'passthrough'
)

# Since we're trying to predict 'Survived', we need to drop it from X and it to y
X = train_pd_pruned.drop("Survived", axis=1)
y = train_pd_pruned["Survived"]

# Create a train and test split of our training data
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=42)
len(X), len(X_train), len(X_test), len(y_train)

# Fit column transformer to training data and transform train and test data with normalization
ct.fit(X_train)
X_train_normal = ct.transform(X_train)
X_test_normal = ct.transform(X_test)
test_pd_normal = ct.transform(test_pd_pruned)

tf.random.set_seed(42)

# 1. Create a model
model_1 = tf.keras.Sequential([
  tf.keras.layers.Dense(11, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(4, activation="relu"),
  tf.keras.layers.Dense(1, activation="sigmoid")                                     
])

# 2. Compile the model
model_1.compile(loss=tf.keras.losses.BinaryCrossentropy(),
                        optimizer=tf.keras.optimizers.Adam(),
                        metrics=["accuracy"])
# 3. Fit the model
history_1 = model_1.fit(X_train_normal,y_train, epochs=100, verbose=0)

model_1.evaluate(X_test_normal, y_test)

model_1_pred_probs = model_1.predict(test_pd_normal)
model_1_pred_probs[:10]

model_1_preds = tf.round(model_1_pred_probs)
model_1_preds = tf.cast(model_1_preds, tf.int32)

predictions = []
for val in model_1_preds:
  value = np.asscalar(val.numpy())
  predictions.append(value)

output = pd.DataFrame({'PassengerId': test_pd.PassengerId, 'Survived': predictions})
output.to_csv('submission.csv', index=False)