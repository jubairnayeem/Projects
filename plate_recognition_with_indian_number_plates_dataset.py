# -*- coding: utf-8 -*-
"""Plate Recognition with Indian Number Plates Dataset.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w-Ehn2QFJammhV5fabBdKJZI4rKgga40

# License Plate Detection on Indian Number Plates Dataset. Link of the dataset is given below.
"""

# Importing necessary libraries
import pandas as pd
import urllib
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import os
import time
from PIL import Image

from keras.applications.vgg16 import VGG16
from keras.layers import Flatten, Dense, Conv2D, MaxPooling2D, Input, Dropout
from keras.models import Model, Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam

for dirname, _, filenames in os.walk('/colab/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

"""## Reading the data. I found the dataset in Kaggle named as Indian Number Plates.json.
The two main elements of the data are content and annotation. Content contains links to the images and annotation contains some information about the respected image.
"""

df = pd.read_json("https://raw.githubusercontent.com/sayakpaul/Vehicle-Number-Plate-Detection/master/Indian_Number_plates.json", lines=True)
df.head()

os.mkdir("Indian Number Plates")

"""A simple scirpt to download and save all images to a directory while recording annotation information to a dictionary. The informations recorded contains image_width, image_height, x and y coordinates of top left cornet and x and y coordinates of bottom right corner of the bounding box ([top_x, top_y, bottom_x, bottom_y)"""

dataset = dict()
dataset["image_name"] = list()
dataset["image_width"] = list()
dataset["image_height"] = list()
dataset["top_x"] = list()
dataset["top_y"] = list()
dataset["bottom_x"] = list()
dataset["bottom_y"] = list()

counter = 0
for index, row in df.iterrows():
    img = urllib.request.urlopen(row["content"])
    img = Image.open(img)
    img = img.convert('RGB')
    img.save("Indian Number Plates/licensed_car{}.jpeg".format(counter), "JPEG")
    
    dataset["image_name"].append("licensed_car{}".format(counter))
    
    data = row["annotation"]
    
    dataset["image_width"].append(data[0]["imageWidth"])
    dataset["image_height"].append(data[0]["imageHeight"])
    dataset["top_x"].append(data[0]["points"][0]["x"])
    dataset["top_y"].append(data[0]["points"][0]["y"])
    dataset["bottom_x"].append(data[0]["points"][1]["x"])
    dataset["bottom_y"].append(data[0]["points"][1]["y"])
    
    counter += 1
print("Downloaded {} car images.".format(counter))

# DataFrame object from the dictionary
df = pd.DataFrame(dataset)
df.head()

# converting it to csv for simplicity
df.to_csv('indian_license_plates.csv', index=False)

df = pd.read_csv("indian_license_plates.csv")
df['image_name'] = df['image_name'] + '.jpeg'
df.drop(['image_width', 'image_height'], axis=1, inplace=True)
df.head()

"""Here I have selected five random records from the dataframe for a later visual inspection of predictions. """

lucky_test_samples = np.random.randint(0, len(df), 5)
reduced_df = df.drop(lucky_test_samples, axis=0)

# Viewing sample image
WIDTH = 224
HEIGHT = 224
CHANNEL = 3

def show_img(index):
  image = cv2.imread('Indian Number Plates/' + df['image_name'].iloc[index])
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  image = cv2.resize(image, dsize=(WIDTH, HEIGHT))

  tx = int(df['top_x'].iloc[index] * WIDTH)
  ty = int(df['top_y'].iloc[index] * HEIGHT)
  bx = int(df['bottom_x'].iloc[index] * WIDTH)
  by = int(df['bottom_y'].iloc[index] * HEIGHT)

  image = cv2.rectangle(image, (tx, ty), (bx, by), (0, 0, 255), 1)
  plt.imshow(image)
  plt.show()

show_img(5)

"""I have created an ImageDataGenerator object to load batches of images to memory. I also splitted the data into two with a batch size of 32 images where training consists of 80% of the data and the rest is validation(20%)"""

datagen = ImageDataGenerator(rescale=1.0/255.0, validation_split=0.1)

train_generator = datagen.flow_from_dataframe(
    reduced_df, 
    directory='Indian Number Plates/',
    x_col='image_name', 
    y_col=['top_x', 'top_y', 'bottom_x', 'bottom_y'],
    target_size=(WIDTH, HEIGHT),
    batch_size=32,
    class_mode='other',
    subset='training'
)

validation_generator = datagen.flow_from_dataframe(
    reduced_df,
    directory='Indian Number Plates/',
    x_col='image_name',
    y_col=['top_x', 'top_y', 'bottom_x', 'bottom_y'],
    target_size=(WIDTH, HEIGHT),
    batch_size=32,
    class_mode='other',
    subset='validation'
)

model = Sequential()
model.add(VGG16(weights='imagenet', include_top=False, input_shape=(HEIGHT, WIDTH, CHANNEL)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(4, activation='sigmoid'))

model.layers[-6].trainable = False

model.summary()

"""Here we find the minimum amount of step count to cover all the batches, using the following equation: 
  
  **Step size = Number of Elements / Batch Size**
"""

STEP_SIZE_TRAIN = int(np.ceil(train_generator.n / train_generator.batch_size))
STEP_SIZE_VAL = int(np.ceil(validation_generator.n / validation_generator.batch_size))

print('Train step size:', STEP_SIZE_TRAIN)
print('Validation step size:', STEP_SIZE_VAL)

adam = Adam(lr=0.0005)
model.compile(optimizer=adam, loss='mse')

history = model.fit_generator(train_generator, 
                              steps_per_epoch=STEP_SIZE_TRAIN,
                              validation_data=validation_generator,
                              validation_steps=STEP_SIZE_VAL,
                              epochs=30)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

model.evaluate(validation_generator, steps=STEP_SIZE_VAL)

# Inspection of the five samples
for idx, row in df.iloc[lucky_test_samples].iterrows():    
    img = cv2.resize(cv2.imread("Indian Number Plates/" + row[0]) / 255.0, dsize=(WIDTH, HEIGHT))
    y_hat = model.predict(img.reshape(1, WIDTH, HEIGHT, 3)).reshape(-1) * WIDTH
    
    xt, yt = y_hat[0], y_hat[1]
    xb, yb = y_hat[2], y_hat[3]
    
    img = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2RGB)
    image = cv2.rectangle(img, (xt, yt), (xb, yb), (0, 0, 255), 1)
    plt.imshow(image)
    plt.show()