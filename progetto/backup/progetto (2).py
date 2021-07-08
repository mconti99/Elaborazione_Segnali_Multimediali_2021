# -*- coding: utf-8 -*-
"""progetto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TY1C3oP5nXt67tdqQNYbJlOB36L2brRP
"""

from google.colab import drive
drive.mount('/content/drive')

import keras
import matplotlib.pyplot as plt
import numpy as np
import skimage.io as io

batch_size = 32 #da scegliere
img_width, img_height = 256, 256

from keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale = 1. / 255,zoom_range = 0.2,horizontal_flip = True, rotation_range=15)
train_generator = train_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/train',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

val_datagen = ImageDataGenerator(rescale=1. / 255)
val_generator = val_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/validation',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

test_datagen = ImageDataGenerator(rescale=1. / 255)
test_generator = test_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test',target_size=(img_width, img_height),batch_size=8,class_mode='categorical')

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

  model.compile(loss=keras.losses.CategoricalCrossentropy(from_logits=False), optimizer=keras.optimizers.Adam() ,metrics=['accuracy'])

  return model

def create_model():
  base_model = keras.applications.ResNet152V2(include_top=False, weights="imagenet", input_shape=(img_width, img_height, 3))
  
  for layer in base_model.layers:
    layer.trainable = False

  model = keras.models.Sequential()
  model.add(base_model)
  model.add(keras.layers.Flatten())
  model.add(keras.layers.Dense(2048, activation='relu'))
  model.add(keras.layers.Dense(512, activation='relu'))
  model.add(keras.layers.Dense(10, activation='softmax')) 

  model.compile(loss=keras.losses.CategoricalCrossentropy(), optimizer=keras.optimizers.Adam() ,metrics=['accuracy'])

  return model

network= create_model()
network.summary()

#nb_train_samples = 1608
#nb_val_samples = 404
network.fit_generator(train_generator, validation_data=val_generator, epochs=50,verbose=True)#, steps_per_epoch=nb_train_samples // batch_size,validation_steps=nb_val_samples // batch_size)

classes = ['Bear', 'Cat', 'Chicken', 'Cow', 'Deer', 'Dog', 'Duck', 'Eagle', 'Elephant', 'Human', 'Lion', 'Monkey', 'Mouse', 'Panda', 'Pig', 'Pigeon', 'Rabbit', 'Sheep', 'Tiger', 'Wolf']

classes = ['Cane','Cavallo','Elefante','Farfalla', 'Gallina', 'Gatto', 'Mucca', 'Pecora', 'Ragno', 'Scoiattolo']

img=np.float32(io.imread('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/gatto/0.jpg'))
img=img/255
from skimage.transform import resize
img=resize(img, (img_width, img_height))
img=np.reshape(img, (1, img_width, img_height, 3))
pred=network.predict(img)
plt.figure(figsize=(20,10))
plt.subplot(122);plt.bar(np.arange(10), pred[0])
plt.xticks(np.arange(10), classes)
print(classes[np.argmax(pred)])
plt.subplot(121);plt.imshow(img[0])
plt.show()

network.load_weights("/content/drive/MyDrive/pesi_progetto_resnet")

network.save_weights("/content/drive/MyDrive/pesi_progetto_resnet")

imgs = next(test_generator)


predictions = network.predict(imgs[0])
p = np.argmax(predictions,1)
l = np.argmax(imgs[1],1)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(l, p)
print(cm)

accuracy = np.sum(p==l)/np.sum(p==p)
print(accuracy)

a = np.int64(p==l)
mistakes = list()
for i in range(len(a)):
  if(a[i]!= True):
    mistakes.append((imgs[0][i],predictions[i]))

for i in mistakes:
  plt.figure(figsize=(30,10))
  plt.title(classes[np.argmax(i[1])])
  plt.subplot(121);plt.imshow(i[0])
  plt.subplot(122);plt.bar(np.arange(10), i[1]); plt.xticks(np.arange(10), classes)

!pip install foolbox==3.3.1
from foolbox.models import TensorFlowModel
model_foolbox = TensorFlowModel(network, bounds=(0,1))
from foolbox.attacks import FGSM
attack = FGSM()

imgs = next(test_generator)

x_true = imgs[0]
y_true = imgs[1]
y_pred = network.predict(x_true)
acc = np.mean((np.argmax(y_true,-1)==np.argmax(y_pred,-1)))
print("Accuracy iniziale:")
print(acc)

from tensorflow import convert_to_tensor
preclip, x_advs, res = attack(
    model_foolbox,convert_to_tensor(x_true),
    convert_to_tensor(np.argmax(y_true,-1)), 
    epsilons=0.05)
x_advs = x_advs.numpy()

y_pred_adv = network.predict(x_advs)
acc = np.mean((np.argmax(y_pred_adv,-1)==np.argmax(y_true,-1)))
print("Accuracy dopo l'attacco")
print(acc)

import tensorflow as tf
from tensorflow import convert_to_tensor

def create_adversarial_pattern(input_image, input_label, model, loss_object=tf.keras.losses.CategoricalCrossentropy()):
  input_imag = convert_to_tensor(input_image)
  input_label = convert_to_tensor(input_label)

  with tf.GradientTape() as tape:
    tape.watch(input_image) #inizializzo per fare il gradiente
    prediction = model.predict(input_image) 
    loss = loss_object(input_label, prediction)

  gradient = tape.gradient(loss, input_image)#calcola il gradiente della loss rispetto all'ingresso x
  perturbation = np.sign(gradient.numpy())
  return perturbation

orig_img = x_true[0:1].copy()
fake_img = x_true[0:1].copy()

epislon = 0.01

for i in range(100):
  n = create_adversarial_pattern(fake_img, y_true[0:1], network)
  fake_img += epsilon * n
plt.imshow(fake_img[0])

pred = network.predict(orig_img)
fake_pred = network.predict(fake_img)
plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(orig_img[0]); plt.subplot(122); plt.bar(range(10), pred[0]); plt.xticks(np.arange(10), classes);
plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(fake_img[0]); plt.subplot(122); plt.bar(range(10), fake_pred[0]); plt.xticks(np.arange(10), classes);