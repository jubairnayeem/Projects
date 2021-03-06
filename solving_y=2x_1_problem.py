# -*- coding: utf-8 -*-
"""Solving Y=2x-1_problem.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I2fNJrXwbW8VPgPHaJ6Ghmkilnq8yXut
"""

import tensorflow as tf
import numpy as np
from tensorflow import keras

"""Now, we create the simplest possible neural network that has 1 layer. That layer consists of 1 neuron and the input shape is 1 value."""

model = tf.keras.Sequential([keras.layers.Dense(units=1, input_shape=[1])])
model.compile(optimizer='sgd', loss='mean_squared_error')

"""Now we provide the model with data"""

xs = np.array([-1.0, 0.0, 1.0, 2.0, 3.0, 4.0], dtype=float)
ys = np.array([-2.0, 1.0, 4.0, 7.0, 10.0, 13.0], dtype=float)

"""Now we turn to training the network"""

model.fit(xs, ys, epochs=500)

"""Finally we evaluate our model by using the predict method on new data"""

print(model.predict([10.0]))