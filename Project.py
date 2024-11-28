# -*- coding: utf-8 -*-
"""Project

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ap5jNSmrS3CcDAce6pGm7Ypflqjvs1zU
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import os
import random
import tensorflow
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout
from keras.layers import Conv2D,MaxPooling2D, ZeroPadding2D
from keras import regularizers
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import ResNet50
from keras.layers import GlobalAveragePooling2D
from keras.models import Model
from tensorflow.keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ModelCheckpoint

train_dir = '/content/drive/MyDrive/dataset/train'
test_dir = '/content/drive/MyDrive/dataset/test'

trainDataGen=ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
 )

testDataGen=ImageDataGenerator(rescale=1./255)

trainGen=trainDataGen.flow_from_directory(
    train_dir,
    target_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    subset='training')

valGen=trainDataGen.flow_from_directory(
    train_dir,
    target_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    subset='validation')

testGen=testDataGen.flow_from_directory(
    test_dir,
    target_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=1)

def create_resnet50_model():
    base_model_resnet = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    x_resnet = base_model_resnet.output
    x_resnet = GlobalAveragePooling2D()(x_resnet)
    x_resnet = Dense(1024, activation='relu')(x_resnet)
    x_resnet = Dropout(0.5)(x_resnet)
    predictions_resnet = Dense(12, activation='softmax')(x_resnet)
    resnet_model = Model(inputs=base_model_resnet.input, outputs=predictions_resnet)

    return resnet_model

def train_resnet50_model(model, trainGen, valGen, epochs=20, learning_rate=0.001, batch_size=32):

    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True, mode='min')

    for layer in model.layers:
        layer.trainable = False
    model.layers[-4].trainable = True

    model.compile(optimizer=Adam(learning_rate=learning_rate), loss='categorical_crossentropy', metrics=['accuracy'])
    history_resnet = model.fit(trainGen, validation_data=valGen, epochs=epochs, batch_size=batch_size, callbacks=[early_stopping, checkpoint])

    for layer in model.layers:
        layer.trainable = True

    model.compile(optimizer=Adam(learning_rate=learning_rate / 10), loss='categorical_crossentropy', metrics=['accuracy'])
    history_resnet_fine = model.fit(trainGen, validation_data=valGen, epochs=epochs, batch_size=batch_size, callbacks=[early_stopping, checkpoint])

    return history_resnet, history_resnet_fine


learning_rates = [0.001]
batch_sizes = [32]
epoch_counts = [10]

for lr in learning_rates:
    for bs in batch_sizes:
        for ep in epoch_counts:
            print(f"Training with learning_rate={lr}, batch_size={bs}, epochs={ep}")
            resnet_model = create_resnet50_model()
            history_resnet, history_resnet_fine = train_resnet50_model(resnet_model, trainGen, valGen, epochs=ep, learning_rate=lr, batch_size=bs)

loss, accuracy = resnet_model.evaluate(testGen)
print(f"Test Loss: {loss}")
print(f"Test Accuracy: {accuracy}")

def plot_training_history(history):

    acc = history[0].history['accuracy']
    val_acc = history[0].history['val_accuracy']
    loss = history[0].history['loss']
    val_loss = history[0].history['val_loss']

    acc_fine = history[1].history['accuracy']
    val_acc_fine = history[1].history['val_accuracy']
    loss_fine = history[1].history['loss']
    val_loss_fine = history[1].history['val_loss']

    epochs_range = range(len(acc) + len(acc_fine))


    acc += acc_fine
    val_acc += val_acc_fine
    loss += loss_fine
    val_loss += val_loss_fine

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    plt.subplot(2, 1, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')

    plt.show()

plot_training_history([history_resnet, history_resnet_fine])