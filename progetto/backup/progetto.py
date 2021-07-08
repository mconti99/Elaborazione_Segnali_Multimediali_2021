# -*- coding: utf-8 -*-
"""progetto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TY1C3oP5nXt67tdqQNYbJlOB36L2brRP
"""

import keras
import matplotlib.pyplot as plt
import numpy as np
import skimage.io as io

from google.colab import drive
drive.mount('/content/drive')

batch_size=16#da scegliere
img_width, img_height = 256, 256

from keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale = 1. / 255,zoom_range = 0.2,horizontal_flip = True, rotation_range=5)
train_generator = train_datagen.flow_from_directory('/content/drive/MyDrive/dataset/train',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

val_datagen = ImageDataGenerator(rescale=1. / 255)
val_generator = val_datagen.flow_from_directory('/content/drive/MyDrive/dataset/validation',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

test_datagen = ImageDataGenerator(rescale=1. / 255)
test_generator = test_datagen.flow_from_directory('/content/drive/MyDrive/dataset/test',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

def create_model():
  model = keras.models.Sequential() 
  model.add(keras.layers.Conv2D(filters = 128, kernel_size=(5,5), padding='same', activation='relu', input_shape=(img_width, img_height, 3)))
  model.add(keras.layers.MaxPooling2D(2,2))
  model.add(keras.layers.Conv2D(filters = 128, kernel_size=(5,5), padding='same', activation='relu'))
  model.add(keras.layers.MaxPooling2D(2,2))
  model.add(keras.layers.Conv2D(filters = 256, kernel_size=(5,5), padding='same', activation='relu'))
  model.add(keras.layers.MaxPooling2D(2,2))
  model.add(keras.layers.Conv2D(filters = 256, kernel_size=(5,5), padding='same', activation='relu'))
  model.add(keras.layers.MaxPooling2D(2,2))
  model.add(keras.layers.Conv2D(filters = 512, kernel_size=(3,3), padding='same', activation='relu'))
  model.add(keras.layers.Flatten())
  model.add(keras.layers.Dense(2048, activation='relu'))
  model.add(keras.layers.Dense(512, activation='relu'))
  model.add(keras.layers.Dense(20, activation='softmax'))

  model.compile(loss=keras.losses.categorical_crossentropy, optimizer=keras.optimizers.Adam(learning_rate=0.001),metrics=['accuracy'])
  return model

network= create_model()
network.summary()

network.fit_generator(train_generator, validation_data=val_generator, epochs=50,verbose=True )

img=np.float32(io.imread('/content/drive/MyDrive/dataset/test/HumanHead/10.jpg'))
img=img/255
from skimage.transform import resize
img=resize(img, (img_width, img_height))
img=np.reshape(img, (1, img_width, img_height, 3))
pred=network.predict(img)
print(pred)
plt.figure()
plt.bar(np.arange(20), pred[0])
plt.show()

!nvidia-smi