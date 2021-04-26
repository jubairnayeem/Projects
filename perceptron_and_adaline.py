# -*- coding: utf-8 -*-
"""Perceptron and Adaline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14pIoqHzDIc9_-qNsL5mbguPcwi7p6L5G

# An object-oriented perceptron API
"""

import numpy as np

class Perceptron(object):
  """
  Perceptron classifier.

  Parameters
  ----------
  eta: float
    Learning rate (0.0<eta<=1.0)
  n_iter: int
    Passes over the training dataset.
  random_state: int
    Random number generator seed for random weight initialization.

  Attributes
  ----------
  w_: 1d-array
    Weights after fitting.
  errors_: list
    Number of misclassifications (updates) in each epoch.

  """

  def __init__(self, eta=0.01, n_iter=50, random_state=1):
    self.eta = eta
    self.n_iter = n_iter
    self.random_state = random_state

  def fit(self, X, y):
    """
    Fit training data.

    Parameters
    ----------
    X : {array-like}, shape = [n_examples, n_features]
        Training vectors, where n_examples is the number of examples, 
        and n_features is the number of features.
    y : array-like, shape = [n_examples]
        Target values.

    Returns
    -------
    self : object

    """
    rgen = np.random.RandomState(self.random_state)
    self.w_ = rgen.normal(loc=0.0, scale=0.01, size=1 + X.shape[1])
    self.errors_ = []

    for _ in range(self.n_iter):
      errors = 0
      for xi, target in zip(X,y):
        update = self.eta * (target - self.predict(xi))
        self.w_[1:] += update * xi
        self.w_[0] += update
        errors += int(update != 0.0)
      self.errors_.append(errors)
    return self

  def net_input(self, X):
    """
    Calculate net input
    """
    return np.dot(X, self.w_[1:]) + self.w_[0]

  def predict(self, X):
    """
    Return class label after unit step
    """
    return np.where(self.net_input(X) >= 0.0, 1, -1)

# Loading the IRIS dataset to implement the perceptron
import os
import pandas as pd

s = os.path.join("https://archive.ics.uci.edu", "ml", "machine-learning-databases",
                 "iris", "iris.data")
print('URL:', s)

df = pd.read_csv(s, header=None, encoding='utf-8')
df.tail()

# We extract the first 100 class labels that correspond to the 50 Iris-setosa &
# 50 Iris-versicolor flowers and convert the class labels into the two integer
# class labels, 1 (versicolor) and -1 (setosa), that we assign to a vector y.
# Similarly we extract the first feature column (sepal length) and the third 
# feature column (petal length) of those 100 training examples and assign them 
# to a feature matrix X
import matplotlib.pyplot as plt

# select setosa and versicolor
y = df.iloc[0:100, 4].values
y = np.where(y == 'Iris-setosa', -1, 1)

# extract sepal length and petal length
X = df.iloc[0:100, [0, 2]].values

# plot the data
plt.scatter(X[:50, 0], X[:50, 1], color='red', marker='o', label='setosa')
plt.scatter(X[50:100, 0], X[50:100, 1], color='blue', marker='x', label='versicolor')
plt.xlabel('sepal length [cm]')
plt.ylabel('petal length [cm]')
plt.legend(loc='upper left')
plt.show()

"""We can see that a linear decision boundary should be sufficient to separate Setosa from Versicolor flowers. """

# Training our perceptron algorithm on the Iris data subset 
# Also, we will plot the misclassification error for each epoch to check whether
# the algorithm converged and found a decision boundary that separates the two
# Iris flower cases
ppn = Perceptron(eta=0.01, n_iter=10)
ppn.fit(X, y)
plt.plot(range(1, len(ppn.errors_) + 1), ppn.errors_, marker='o')
plt.xlabel("Epochs")
plt.ylabel("Number of updates")
plt.show()

"""As we can see, our perceptron converged after the sixth epoch. Lets implement a small convenience function to visualize the decision boundaries for two-dimensional datasets:"""

from matplotlib.colors import ListedColormap
def plot_decision_regions(X, y, classifier, resolution=0.02):

  # setup marker generator and color map
  markers = ('s', 'x', 'o', '^', 'v')
  colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')
  cmap = ListedColormap(colors[:len(np.unique(y))])
  
  # plot the decision surface
  x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
  x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
  xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution), 
                         np.arange(x2_min, x2_max, resolution))
  Z = classifier.predict(np.array([xx1.ravel(), xx2.ravel()]).T)
  Z = Z.reshape(xx1.shape)
  plt.contourf(xx1, xx2, Z, alpha=0.3, cmap=cmap)
  plt.xlim(xx1.min(), xx1.max())
  plt.ylim(xx2.min(), xx2.max())

  # plot class examples
  for idx, cl in enumerate(np.unique(y)):
    plt.scatter(x=X[y == cl, 0], y=X[y == cl, 1], 
                alpha=0.8, c=colors[idx], marker=markers[idx],
                label=cl, edgecolor='black')

plot_decision_regions(X, y, classifier=ppn)
plt.xlabel('Sepal Length [cm]')
plt.ylabel('Petal Length [cm]')
plt.legend(loc='upper left')
plt.show()

"""# An Object oriented AdaLiNe API"""

class AdalineGD(object):
  """
  ADAptive LInear NEuron classifier.

  Parameters
  ----------
  eta: float
    Learning rate (0.0<eta<=1.0)
  n_iter: int
    Passes over the training dataset.
  random_state: int
    Random number generator seed for random weight initialization.

  Attributes
  ----------
  w_: 1d-array
    Weights after fitting.
  cost_: list
    Sum-of-squares cost function value in each epoch.

  """

  def __init__(self, eta=0.01, n_iter=50, random_state=1):
    self.eta = eta
    self.n_iter = n_iter
    self.random_state = random_state

  def fit(self, X, y):
    """
    Fit training data.

    Parameters
    ----------
    X : {array-like}, shape = [n_examples, n_features]
        Training vectors, where n_examples is the number of examples, 
        and n_features is the number of features.
    y : array-like, shape = [n_examples]
        Target values.

    Returns
    -------
    self : object

    """
    rgen = np.random.RandomState(self.random_state)
    self.w_ = rgen.normal(loc=0.0, scale=0.01, size=1 + X.shape[1])
    self.cost_ = []

    for i in range(self.n_iter):
      net_input = self.net_input(X)
      output = self.activation(net_input)
      errors = (y - output)
      self.w_[1:] += self.eta * X.T.dot(errors)
      self.w_[0] += self.eta * errors.sum()
      cost = (errors**2).sum() / 2.0
      self.cost_.append(cost)
    return self

  def net_input(self, X):
    """
    Calculate net input
    """
    return np.dot(X, self.w_[1:]) + self.w_[0]

  def activation(self, X):
    """
    Compute linear activation
    """
    return X

  def predict(self, X):
    """
    Return class label after unit step
    """
    return np.where(self.activation(self.net_input(X)) >= 0.0, 1, -1)

# Plotting the cost against the number of epochs for the two different learning
# rates
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,4))
ada1 = AdalineGD(n_iter=10, eta=0.01).fit(X,y)
ax[0].plot(range(1, len(ada1.cost_) + 1), np.log10(ada1.cost_), marker='o')
ax[0].set_xlabel('Epochs')
ax[0].set_ylabel('log(Sum-squared-error)')
ax[0].set_title('Adaline - Learning rate 0.01')

ada2 = AdalineGD(n_iter=10, eta=0.0001).fit(X,y)
ax[1].plot(range(1, len(ada2.cost_) + 1), ada2.cost_, marker='o')
ax[1].set_xlabel('Epochs')
ax[1].set_ylabel('Sum-Squared-Error')
ax[1].set_title('Adaline - Learning rate 0.0001')

plt.show()

"""Gradient descent is one of the many algorithms that benefit from feature scaling. Here we will standardize our data meaning, shifting each feature to center around zero and obtaining a standard deviation of 1. """

X_std = np.copy(X)
X_std[:,0] = (X[:,0] - X[:,0].mean()) / X[:,0].std()
X_std[:,1] = (X[:,1] - X[:,1].mean()) / X[:,1].std()

# Training the Adaline again
ada_gd = AdalineGD(n_iter=15, eta=0.01)
ada_gd.fit(X_std, y)

plot_decision_regions(X_std, y, classifier=ada_gd)
plt.title('Adaline - Gradient Descent')
plt.xlabel('sepal length [standardized]')
plt.ylabel('petal length [standardized]')
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()

plt.plot(range(1,len(ada_gd.cost_) + 1), ada_gd.cost_, marker='o')
plt.xlabel('Epochs')
plt.ylabel('Sum-Squared-Error')
plt.tight_layout()
plt.show()

"""# An object oriented Adaline Stochastic Gradient Descent API"""

class AdalineSGD(object):
  """
  ADAptive LInear NEuron classifier.

  Parameters
  ----------
  eta: float
    Learning rate (0.0<eta<=1.0)
  n_iter: int
    Passes over the training dataset.
  shuffle: bool (default: True)
    Shuffles training data every epoch if True to prevent cycles.
  random_state: int
    Random number generator seed for random weight initialization.

  Attributes
  ----------
  w_: 1d-array
    Weights after fitting.
  cost_: list
    Sum-of-squares cost function value averaged over all
    training examples in each epoch.

  """

  def __init__(self, eta=0.01, n_iter=50, shuffle=True, random_state=None):
    self.eta = eta
    self.n_iter = n_iter
    self.w_initialized = False
    self.shuffle = shuffle
    self.random_state = random_state

  def fit(self, X, y):
    """
    Fit training data.

    Parameters
    ----------
    X : {array-like}, shape = [n_examples, n_features]
        Training vectors, where n_examples is the number of examples, 
        and n_features is the number of features.
    y : array-like, shape = [n_examples]
        Target values.

    Returns
    -------
    self : object

    """
    self._initialize_weights(X.shape[1])
    self.cost_ = []

    for i in range(self.n_iter):
      if self.shuffle:
        X, y = self._shuffle(X, y)
      cost = []
      for xi, target in zip(X, y):
        cost.append(self._update_weights(xi, target))
      avg_cost = sum(cost) / len(y)
      self.cost_.append(avg_cost)
    return self

  def partial_fit(self, X, y):
    """
    Fit training data without reinitializing the weights
    """
    if not self.w_initialized:
      self._initialize_weights(X.shape[1])
    if y.ravel().shape[0] > 1:
      for xi, target in zip(X, y):
        self._update_weights(xi, target)
    else:
      self._update_weights(X, y)
    return self

  def _shuffle(self, X, y):
    """
    Shuffle training data
    """
    r = self.rgen.permutation(len(y))
    return X[r], y[r]

  def _initialize_weights(self, m):
    """
    Initialize weights to small random numbers
    """
    self.rgen = np.random.RandomState(self.random_state)
    self.w_ = self.rgen.normal(loc=0.0, scale=0.01, size=1+m)
    self.w_initialized = True

  def _update_weights(self, xi, target):
    """
    Apply Adaline learning rule to update the weights
    """
    output = self.activation(self.net_input(xi))
    error = (target - output)
    self.w_[1:] += self.eta * xi.dot(error)
    self.w_[0] += self.eta * error
    cost = 0.5 * (error**2)
    return cost

  def net_input(self, X):
    """
    Calculate net input
    """
    return np.dot(X, self.w_[1:]) + self.w_[0]

  def activation(self, X):
    """
    Compute linear activation
    """
    return X

  def predict(self, X):
    """
    Return class label after unit step
    """
    return np.where(self.activation(self.net_input(X)) >= 0.0, 1, -1)

ada_sgd = AdalineSGD(n_iter=15, eta=0.01, random_state=1)
ada_sgd.fit(X_std, y)

plot_decision_regions(X_std, y, classifier=ada_sgd)
plt.title("Adaline - Stochastic Gradient Descent")
plt.xlabel("Sepal Length [standardized]")
plt.ylabel("Petal Length [standardized]")
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()

plt.plot(range(1, len(ada_sgd.cost_) + 1), ada_sgd.cost_, marker='o')
plt.xlabel("Epochs")
plt.ylabel("Average Cost")
plt.tight_layout()
plt.show()