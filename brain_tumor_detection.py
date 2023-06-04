# -*- coding: utf-8 -*-
"""Brain Tumor Detection

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o6O0G4SnBv0GopZ5AkOaOh3H2-HfCTUC
"""

import warnings
warnings.filterwarnings('ignore')

!unzip /content/archive.zip

import numpy as np
import matplotlib.pyplot as plt
import os
import math
import shutil
import glob

# count the number of images in the respective classes Brain tumor - 1 , Healthy - 0
ROOT_DIR = "/content/brain_tumor_dataset"
number_of_images = {}
# list dir will give what is present in that particular folder
for dir in os.listdir(ROOT_DIR):
  number_of_images[dir] = len(os.listdir(os.path.join(ROOT_DIR , dir))) # without len it will show every image

number_of_images.items()

"""# split the data such as
* 70 % for train data
* 15 % for validation
* 15 % for testing

"""

# function to split the data according to our need
def dataFolder(p , split):
  if not os.path.exists("./"+p):
    os.mkdir("./"+p)

    for dir in os.listdir(ROOT_DIR):
      os.makedirs("./"+p+"/"+dir)
      for img in np.random.choice(a = os.listdir(os.path.join(ROOT_DIR, dir)) , 
                                size = (math.floor(split*number_of_images[dir])-2) ,
                                replace=False):
        O = os.path.join(ROOT_DIR,dir,img) # path
        D = os.path.join("./"+p,dir)
        shutil.copy(O,D)
        os.remove(O)
  else:
    print(f"{p} folder already exist ")

dataFolder("train" , 0.7)

dataFolder("val", 0.15)

dataFolder("test", 0.15)

"""# Model Build"""

from keras.layers import Conv2D , MaxPool2D , Dropout , Flatten , Dense , BatchNormalization , GlobalAvgPool2D
from keras.models import Sequential , Model , load_model
from keras.preprocessing.image import ImageDataGenerator
import keras
from keras.applications.mobilenet import MobileNet
from keras.applications.mobilenet import preprocess_input

"""# Using Transfer Learning to increse the accuracy

--> without transfer learning the accuracy was very low
--> we used mobile net architechture to increse our accuracy
"""

# CNN Model

#model = Sequential()
#model.add(Conv2D(filters=8, kernel_size=(3, 3), activation='relu', input_shape=(224, 224, 3), padding='same'))

#model.add(Conv2D(filters=16, kernel_size=(3, 3), activation='relu'))
#model.add(MaxPool2D(pool_size=(2, 2)))

#model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu'))
#model.add(MaxPool2D(pool_size=(2, 2)))

#model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
#model.add(MaxPool2D(pool_size=(2, 2)))

#model.add(Dropout(rate=0.25))

#model.add(Flatten())
#model.add(Dense(units=32, activation='relu'))
#model.add(Dropout(rate=0.25))
#model.add(Dense(units=1, activation='sigmoid'))

#model.summary()

base_model = MobileNet(input_shape=(224,224,3) , include_top = False)

for layer  in base_model.layers:
  layer.trainable = False

"""# Adding of Flatten and Dense layer to our prebuild model"""

x = base_model.output
x = Flatten()(x)

# Add Dense layer
x = Dense(units=1, activation='sigmoid')(x)

# Assign the output of new layers to the base_model output
output = x

# Create the new model
model = Model(inputs=base_model.input, outputs=output)

# Print the model summary
model.summary()

"""# Compiling the model with default optimiser"""

model.compile(optimizer='rmsprop', loss= keras.losses.binary_crossentropy , metrics=['accuracy'])

"""# Preparing Data using Data Generator

"""

def preprocessingImages(path):
    image_data = ImageDataGenerator(
        zoom_range=0.2,
        shear_range=0.2,
        preprocessing_function=preprocess_input,
        horizontal_flip=True
    )
    image_generator = image_data.flow_from_directory(
        directory=path,
        target_size=(224, 224),
        batch_size=32,
        class_mode='binary'
    )
    return image_generator

path = "/content/train"
train_data = preprocessingImages(path)

path = "/content/test"
test_data = preprocessingImages(path)

path = "/content/val"
val_data = preprocessingImages(path)

# Early stopping and model check point

from keras.callbacks import ModelCheckpoint , EarlyStopping

# Early stopping

es = EarlyStopping(monitor = "val_accuracy" , min_delta = 0.01, patience = 3 , verbose = 1)

# model check point

mc = ModelCheckpoint(monitor = "val_accuracy" , filepath="./bestmodel.h5" , verbose = 1 ,save_best_only= True)

cd  =[es,mc]

"""#Model Training"""

hs = model.fit_generator(train_data,
                         steps_per_epoch=len(train_data),
                         epochs=30,
                         validation_data=val_data,
                         validation_steps=len(val_data),
                         callbacks=cd)

# Model Graphical Interpretation

h = hs.history
h.keys()

import matplotlib.pyplot as plt

plt.plot(h['accuracy'])
plt.plot(h['val_accuracy'] , c ='red')

plt.title("Accuracy VS Val Accuracy")
plt.show()

import matplotlib.pyplot as plt

plt.plot(h['loss'])
plt.plot(h['val_loss'] , c ='red')

plt.title("Loss VS Val Loss")
plt.show()

# load the best fit model

model = load_model("/content/bestmodel.h5")

acc = model.evaluate_generator(test_data)[1]
print(f"Model accuracy : {acc*100} % ")

train_data.class_indices

from tensorflow.keras.preprocessing import image

# prediction of the images

path = "/content/train/no/17 no.jpg"
sample_img = image.load_img(path, target_size=(224, 224))
sample_input = np.expand_dims(image.img_to_array(sample_img), axis=0)
sample_input = preprocess_input(sample_input)

sample_pred = model.predict(sample_input)

if sample_pred[0] < 0.5:
    print("The MRI scan is of a healthy brain.")
else:
    print("The MRI scan is of a brain tumor.")
# Displaying the image
plt.imshow(sample_img)
plt.title("Input Image")
plt.show()

# prediction of the images

path = "/content/brain_tumor_dataset/yes/Y243.JPG"
sample_img = image.load_img(path, target_size=(224, 224))
sample_input = np.expand_dims(image.img_to_array(sample_img), axis=0)
sample_input = preprocess_input(sample_input)

sample_pred = model.predict(sample_input)

if sample_pred[0] < 0.5:
    print("The MRI scan is of a healthy brain.")
else:
    print("The MRI scan is of a brain tumor.")
# Displaying the image
plt.imshow(sample_img)
plt.title("Input Image")
plt.show()