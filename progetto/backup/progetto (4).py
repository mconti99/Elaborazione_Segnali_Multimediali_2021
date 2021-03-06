# -*- coding: utf-8 -*-
"""progetto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TY1C3oP5nXt67tdqQNYbJlOB36L2brRP

# Preparazione dei dati

## Import librerie e mount Google Drive

Viene effettuato il mounting della cartella associata all'account Google Drive, che contiene il dataset di immagini opportunamente diviso in 3 sotto-cartelle: ***train*** per le immagini di addestramento della rete, ***validation*** per la fase di validazione e ***test*** per il test.

Vengono importate le principali librerie e funzioni che saranno utilizzate per il progetto.
"""

from google.colab import drive
drive.mount('/content/drive')
import keras
import matplotlib.pyplot as plt
import numpy as np
import skimage.io as io
import tensorflow as tf
from skimage.transform import resize
from tensorflow import convert_to_tensor

"""## Caricamento dataset

Attraverso l'uso di *ImageDataGenerator*, vengono caricate in maniera automatica le immagini di addestramento, validazione e test. Si noti che viene effettuata la tecnica della **data augmentation** sulle immagini di training, in particolare applicando una rotazione random da -15 a 15 gradi, un ridimensionamento con fattore moltiplicativo random nel range [0.8, 1.2] e riflessione orizzontale random.

Per tutto il dataset, inoltre, è applicata una normalizzazione nel range [0, 1] e un ridimensionamento a 256x256 pixel. La dimensione della *batch* per le immagini di training e validazione è stata individuata sperimentalmente ed è pari a 32, mentre le immagini di test sono state raggruppate in *batch* da 8 immagini ciascuno.
"""

batch_size = 32
img_width, img_height = 256, 256

from keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale = 1. / 255,zoom_range = 0.2,horizontal_flip = True, rotation_range=5)
train_generator = train_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/train',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

val_datagen = ImageDataGenerator(rescale=1. / 255)
val_generator = val_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/validation',target_size=(img_width, img_height),batch_size=batch_size,class_mode='categorical')

test_datagen = ImageDataGenerator(rescale=1. / 255)
test_generator = test_datagen.flow_from_directory('/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test',target_size=(img_width, img_height),batch_size=10,class_mode='categorical')

"""# Addestramento della rete neurale

## Creazione architettura

Viene definita l'architettura della rete neurale attraverso la tecnica del **fine-tuning**, sfruttando la rete *ResNet152V2*, 
pre-addestrata sul dataset ImageNet, una raccolta di circa 14 milioni di immagini annotate manualmente in diverse categorie. I parametri della parte convolutiva di ResNet152V2 non sono modificati durante il training. Questa scelta dipende dalla somiglianza del dataset utilizzato con ImageNet che contiene tutte le classi presenti.

Oltre alla rete base, vengono aggiunti 3 strati **Fully-Connected**, che compongono il classificatore, di cui i primi due con funzione di attivazione non lineare *ReLU* e l'ultimo con la funzione *Softmax*, che normalizza l'uscita per ottenere valori non negativi e a somma unitaria. In questo modo, si ha come risultato finale un vettore di 10 elementi, ognuno dei quali rappresenta la probabilità che l'immagine in ingresso appartenga alla classe i-esima.

Infine, la rete neurale è stata compilata con la loss function *CategoricalCrossentropy* e l'ottimizzatore *Adam*. Per quanto riguarda il **learning rate** della loss function, è stato selezionato il valore di default.
"""

def create_model():
  base_model = keras.applications.ResNet152V2(include_top=False, weights="imagenet", input_shape=(img_width, img_height, 3))#fine tuning
  
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

"""## Training rete

La neural network è stata addestrata con il metodo *fit_generator*, sfruttando i generatori **train_generator** e **val_generator** definiti durante la fase di caricamento del dataset. Al fine di ottenere le migliori prestazioni possibili dalla rete, è stato scelto un numero di *epoche* pari a 50.
"""

network.fit_generator(train_generator, validation_data=val_generator, epochs=50,verbose=True)

network.load_weights("/content/drive/MyDrive/pesi_progetto_resnet")

network.save_weights("/content/drive/MyDrive/pesi_progetto_resnet")

"""# Valutazione delle prestazioni

Viene definita una lista di 10 stringhe, che rappresentano le classi usate per la classificazione del dataset, ed un *dictionary* che consente di passare facilmente da label a classi e viceversa
"""

classes = ['Cane','Cavallo','Elefante','Farfalla', 'Gallina', 'Gatto', 'Mucca', 'Pecora', 'Ragno', 'Scoiattolo']

classes_dictionary = {
  'cane' : np.array([[1,0,0,0,0,0,0,0,0,0]]),
  'cavallo' : np.array([[0,1,0,0,0,0,0,0,0,0]]),
  'elefante' : np.array([[0,0,1,0,0,0,0,0,0,0]]),
  'farfalla' : np.array([[0,0,0,1,0,0,0,0,0,0]]),
  'gallina' : np.array([[0,0,0,0,1,0,0,0,0,0]]),
  'gatto' : np.array([[0,0,0,0,0,1,0,0,0,0]]),
  'mucca' : np.array([[0,0,0,0,0,0,1,0,0,0]]),
  'pecora' : np.array([[0,0,0,0,0,0,0,1,0,0]]),
  'ragno' : np.array([[0,0,0,0,0,0,0,0,1,0]]),
  'scoiattolo' : np.array([[0,0,0,0,0,0,0,0,0,1]])
}

"""Viene effettuato il **test** della rete neurale con un batch di 8 immagini. Dopo aver calcolato l'array di label predetto della rete e quello reale, sono state valutate le prestazioni della CNN in termini di accuratezza.

In particolare, è stata elaborata la ***matrice di confusione***, una matrice 10x10 che permette di capire quante immagini di test sono state classificate bene e quante invece sono state assegnate alla classe sbagliata. 
"""

imgs = next(test_generator)

predictions = network.predict(imgs[0])
p = np.argmax(predictions,1)
l = np.argmax(imgs[1],1)
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(l, p)
print(cm)

accuracy = np.mean(p==l)
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

"""Testando la rete sull'intero Testset di oltre 4000 immagini si ottiene una accuracy del circa 96% e la seguente confusion matrix: 

$ C_{m,n} =
 \begin{pmatrix}
  709 & 4 & 2 & 5 & 0 & 7 & 14 & 3 & 4 & 1 \\
  1 & 388 & 0 & 0 & 0 & 0 & 8 & 2 & 0 & 0 \\
  0 & 1 & 215 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\
  2 & 1 & 0 & 315 & 0 & 0 & 0 & 0 & 6 & 0 \\
  5 & 3 & 0 & 4 & 453 & 0 & 9 & 0 & 2 & 0 \\
  9 & 2 & 3 & 0 & 0 & 230 & 5 & 1 & 1 & 8 \\
  1 & 0 & 1 & 0 & 0 & 0 & 272 & 6 & 0 & 0 \\
  5 & 1 & 1 & 0 & 0 & 2 & 20 & 244 & 0 & 0 \\
  1 & 3 & 0 & 2 & 1 & 0 & 1 & 0 & 726 & 0 \\
  0 & 0 & 1 & 0 & 0 & 2 & 0 & 0 & 0 & 286 \\
 \end{pmatrix}$

# Attacco con la tecnica FGSM

Dopo aver allenato la rete, si palssa all'attacco! Si vuole applicare una perturbazione all'immagine di ingresso tale che la differenza visiva con l'immagine di partenza sia **minima**, ma allo stesso tempo la loss function diventi **grande**, portando quindi la rete neurale a classificare male le immagini.

Al fine di costruire questa perturbazione si è utilizzata la tecnica del FGSM:

$\eta = \epsilon * sign(\nabla_{x}J(\theta,y,x)) $

la perturbazione è dunque pari al gradiente della Lossfunction $J(\theta,y,x)$ rispetto all'immagine di ingresso $x$.

## Attacco non target

Viene definita la funzione di attacco non target. Inizialmente, sia l'immagine in ingresso che l'array di label ad essa associato sono convertiti in tensori. Attraverso il metodo *watch* di **GradientTape**, si inizializza il calcolo del gradiente, in modo da assicurarsi che l'immagine in ingresso venga tracciata da GradientTape.

Dopo aver calcolato la *loss function*, viene elaborato il gradiente della funzione di perdita rispetto all'ingresso e la perturbazione da applicare all'immagine.
"""

def non_targeted_attack(input_image, input_label, model,e=0.01, loss_function = tf.keras.losses.CategoricalCrossentropy()):

  input_image = convert_to_tensor(input_image)
  input_label = convert_to_tensor(input_label)

  with tf.GradientTape() as g:
    g.watch(input_image) 
    prediction = model(input_image) 
    loss = loss_function(input_label, prediction)
    
  gradient = g.gradient(loss, input_image)
  perturbation = e*np.sign(gradient.numpy())

  return perturbation

"""### Metodo iterativo

Il metodo iterativo si basa sull'attaccare la rete neurale per un determinato numero di volte, pari ad *iterations*, sommando ad ogni ciclo la perturbazione generata dall'attacco all'immagine in ingresso. L'immagine perturbata viene quindi sottoposta al successivo attacco, che genererà una nuova perturbazione $\eta$.

Si noti che viene effettuata un'operazione di *clipping* sull'immagine in modo tale che la perturbazione non sia mai maggiore di $|\epsilon|$. Inoltre, alla fine delle iterazioni viene specificata un ulteriore *clipping* dell'immagine in modo che rimanga nel range [0,1].
"""

def iterative_attack(attack, input_image, input_label, model, iterations, e, loss_function=tf.keras.losses.CategoricalCrossentropy()):
  fake_img = input_image.copy()
  for i in range(iterations):
    n = attack(fake_img, input_label, model, e, loss_function)
    fake_img += n
    fake_img = np.clip(fake_img, input_image-e, input_image+e)

  fake_img = np.clip(fake_img, 0, 1)
  return fake_img

"""Testiamo a questo punto l'attacco non target su una generica immagine del test set:"""

imgs = next(test_generator)

x_true = imgs[0]
orig_img = x_true[0:1].copy()
fake_img = iterative_attack(non_targeted_attack, orig_img, imgs[1][0:1],network,10, 0.01)

pred = network.predict(orig_img)
fake_pred = network.predict(fake_img)

plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(orig_img[0]); plt.subplot(122); plt.bar(range(10), pred[0]); plt.xticks(np.arange(10), classes);
plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(fake_img[0]); plt.subplot(122); plt.bar(range(10), fake_pred[0]); plt.xticks(np.arange(10), classes);

diff = fake_img[0]-orig_img[0]

plt.figure(figsize=(15,5));plt.imshow((diff-np.min(diff))/(np.max(diff)-np.min(diff))); plt.xlabel("Immagine differenza (a seguito di un enachment)")

print("Le due immagini differiscono di una quantità al massimo pari a: {}".format(np.max(np.abs(fake_img[0] - orig_img[0]))))

"""Testiamo in conclusione le perfromance su un intero batch di 32 immagini prima e dopo l'attacco: """

imgs = next(test_generator)
x_true = imgs[0][0:10]
lables = imgs[1][0:10]

x_fake = iterative_attack(non_targeted_attack, x_true.copy(), lables, network, 10, 0.01)
prediction = network.predict(x_true)
prediction_fake = network.predict(x_fake)

accuracy = np.mean(np.argmax(lables,1) == np.argmax(prediction,1))
accuracy_fake = np.mean(np.argmax(lables,1) == np.argmax(prediction_fake,1))

print("La accuracy prima dell'attacco è pari a : {}%, quella dopo l'attacco è invece pari a: {}%".format(accuracy*100,accuracy_fake*100))

acc = list()
fake_acc = list()

for i in range(400):
  imgs = next(test_generator)
  
  x_true = imgs[0]
  lables = imgs[1]

  x_fake = iterative_attack(non_targeted_attack, x_true.copy(), lables, network, 10, 0.01)
  prediction = network.predict(x_true)
  prediction_fake = network.predict(x_fake)

  accuracy = np.mean(np.argmax(lables,1) == np.argmax(prediction,1))
  accuracy_fake = np.mean(np.argmax(lables,1) == np.argmax(prediction_fake,1))

  acc.append(accuracy)
  acc_fake.append(accuracy_fake)

acc = np.mean(acc)
fake_acc = np.mean(fake_acc)

"""## Attacco target

Nell'attacco **target**, le immagini vengono perturbate in modo da essere classificate erroneamente come appartenenti ad una specifica classe $y_{t}$ scelta dall'attaccante. 

Al fine di realizzare l'attacco target utilizziamo una variante del *FSGM*, che invece di andare a costruire la perturbazione al fine di aumentare la loss $J(\theta,y,x)$, costruisce una perturbazione che minimizzi la $J(\theta,y_{t},x)$.
La perturbazione sarà dunque calcolata come: $\eta = -\epsilon * sign(\nabla_{x}J(\theta,y_{t},x)) $

Viene quindi definita la funzione di attacco che, a differenza di quella non target, calcola la loss function a partire da $y_{t}$. Si osservi inoltre che ora la perturbazione è l'inverso della perturbazione generata dall'attacco non target.
"""

def targeted_attack(input_image, target_label, model,e, loss_function = tf.keras.losses.CategoricalCrossentropy()):
  input_image = convert_to_tensor(input_image)
  target_label = convert_to_tensor(target_label)

  with tf.GradientTape() as g:
    g.watch(input_image) #inizializzo per fare il gradiente
    prediction = model(input_image) 
    loss = loss_function(target_label, prediction)

  gradient = g.gradient(loss, input_image)#calcola il gradiente della loss rispetto all'ingresso x
  perturbation = -e*np.sign(gradient.numpy())
  return perturbation

"""Viene usata la funzione di attacco target su un immagine del test set. La classe target è "*gatto*", indicata come parametro di ingresso della funzione *iterative_attack*.

Dopo aver predetto l'array di label dell'immagine originale e quello dell'immagine perturbata, le due immagini vengono visualizzate a video e viene aggiunto un grafico a barre che mostra chiaramente come sia cambiata la classe predetta dalla rete neurale a seguito dell'attacco.
"""

orig_img = x_true[0:1].copy()
fake_img = iterative_attack(targeted_attack, orig_img, classes_dictionary['gatto'],network,20, 0.02)

pred = network.predict(orig_img)
fake_pred = network.predict(fake_img)

plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(orig_img[0]); plt.subplot(122); plt.bar(range(10), pred[0]); plt.xticks(np.arange(10), classes);
plt.figure(figsize=(30,10));plt.subplot(121); plt.imshow(fake_img[0]); plt.subplot(122); plt.bar(range(10), fake_pred[0]); plt.xticks(np.arange(10), classes);

diff = fake_img[0]-orig_img[0]

plt.figure(figsize=(15,5));plt.subplot(121); plt.imshow((diff-np.min(diff))/(np.max(diff)-np.min(diff))); plt.xlabel("Immagine differenza (a seguito di un enachment)")

print("Le due immagini differiscono di una quantità al massimo pari a: {}".format(np.max(np.abs(fake_img[0] - orig_img[0]))))

"""Si è poi testato l'attacco target su cinque coppie di classi a scelta per verificarne l'efficacia. I risultati sono nel complesso positivi:"""

cane = io.imread("/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/cane/7.jpg") # -> gatto
scoiattolo = io.imread("/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/scoiattolo/6.jpg") # -> elefante
mucca = io.imread("/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/mucca/1.jpg") # -> ragno
farfalla = io.imread("/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/gallina/6.jpg") # -> farfalla
cavallo = io.imread("/content/drive/MyDrive/dataset.zip (Unzipped Files)/dataset/test/cavallo/1.jpg") # -> gallina

immagini = list()
immagini.append(cane)
immagini.append(scoiattolo)
immagini.append(mucca)
immagini.append(farfalla)
immagini.append(cavallo)

for i in range(len(immagini)):
  immagini[i] = resize(immagini[i], (img_width, img_height,3))

immagini = np.stack(immagini)
predizioni = network.predict(immagini)

labels = list()
labels.append(classes_dictionary['gatto'])
labels.append(classes_dictionary['elefante'])
labels.append(classes_dictionary['ragno'])
labels.append(classes_dictionary['farfalla'])
labels.append(classes_dictionary['gallina'])
labels = np.concatenate(labels, 0)

esempi_avversari = iterative_attack(targeted_attack, immagini, labels, network, 10, 0.01)

predizioni_attacco = network.predict(esempi_avversari)

for i in range(len(immagini)):
  plt.figure(figsize=(30,10))
  plt.subplot(141); plt.imshow(immagini[i])
  plt.subplot(142); plt.bar(range(10), predizioni[i]); plt.xticks(np.arange(10), classes);
  plt.subplot(143); plt.imshow(esempi_avversari[i])
  plt.subplot(144); plt.bar(range(10), predizioni_attacco[i]); plt.xticks(np.arange(10), classes);

"""# Attacco black box

Gli attacchi black box prevedono di costruire perdurbazioni avversarie per una rete neurale della quale non si conosce la struttura interna. Una tecnica untilizzata è quella di progettare un attacco per una rete surrogata allenata ad hoc sullo stesso training set della rete target.

## Definizione ed allenamento del modello "black box"
"""

def create_blackbox_model():
  base_model = keras.applications.VGG19(include_top=False, weights="imagenet", input_shape=(img_width, img_height, 3))#fine tuning
  
  for layer in base_model.layers[:-3]:
    layer.trainable = False

  model = keras.models.Sequential()
  model.add(base_model)
  model.add(keras.layers.Flatten())
  model.add(keras.layers.Dense(1024, activation='relu'))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dense(512, activation='relu'))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dense(250, activation='relu'))
  model.add(keras.layers.BatchNormalization())
  model.add(keras.layers.Dense(10, activation='softmax')) 

  model.compile(loss=keras.losses.CategoricalCrossentropy(), optimizer=keras.optimizers.Adam() ,metrics=['accuracy'])

  return model

bb_network = create_blackbox_model()
bb_network.summary()

bb_network.fit_generator(train_generator, validation_data=val_generator, epochs=15,verbose=True)

bb_network.save_weights("/content/drive/MyDrive/pesi_progetto_vggnet")

"""##Creazione degli esempi avversari per la rete surrogata

Testiamo prima la tecnica non target, costruiamo alcuni esempi avversari per la rete surrogata e verifichiamone l'efficacia nel far sbagliare la rete black box:
"""

imgs = next(test_generator)

x_true = imgs[0]
orig_img = x_true[0:1].copy()
fake_img = iterative_attack(non_targeted_attack, orig_img, imgs[1][0:1],network,10, 0.01)

pred = bb_network.predict(orig_img)
fake_pred = bb_network.predict(fake_img)

plt.figure(figsize=(30,10))
plt.subplot(121); plt.imshow(orig_img[0])
plt.subplot(122); plt.bar(range(10), pred[0]); plt.xticks(np.arange(10), classes);

plt.figure(figsize=(30,10))
plt.subplot(121); plt.imshow(fake_img[0])
plt.subplot(122); plt.bar(range(10), fake_pred[0]); plt.xticks(np.arange(10), classes);

"""A questo punto, testiamo gli esempi avversari costruiti precedentemente tramite il FGSM targeted per la rete surrogata, e verifichiamo la loro efficacia contro quella blackbox: """

predizioni_modello_bb = bb_network.predict(esempi_avversari)

for i in range(len(immagini)):
  plt.figure(figsize=(30,10))
  plt.subplot(121); plt.imshow(esempi_avversari[i])
  plt.subplot(122); plt.bar(range(10), predizioni_modello_bb[i]); plt.xticks(np.arange(10), classes);

"""# Vecchio modello"""

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
print(res)