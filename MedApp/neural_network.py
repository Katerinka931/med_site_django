import os
from enum import Enum

import numpy as np
import pandas as pd
from django.core.files.storage import FileSystemStorage
from keras.api.keras.preprocessing import image
from tensorflow import keras
import pydicom as dicom
import pydicom.uid
from PIL import Image

storage_path = os.getcwd() + '/temp_storage/'

model = keras.models.load_model(os.getcwd() + "/KerasModel", custom_objects=None,
                                compile=True,
                                options=None)


def save_file(file):
    fs = FileSystemStorage(location=storage_path)
    filename = fs.save(file.name, file)
    file_url = fs.path(filename)
    return fs, filename, file_url


class Disease(Enum):
    PNEUMONIA = 'Пневмония'
    NORMAL = 'Патологий не обнаружено'
    COVID19 = 'Covid-19'
    TURBERCULOSIS = 'Туберкулез'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class NeuralNetwork():
    def dicom_to_jpg(self, image_path, img_name):
        ds = dicom.read_file(image_path, force=True)
        ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        file = ds.pixel_array

        new_image = file.astype(float)
        scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
        scaled_image = np.uint8(scaled_image)
        final_image = Image.fromarray(scaled_image)

        jpg_path = storage_path + img_name + '.jpeg'
        return final_image, jpg_path

    def jpg_to_dicom(self, path, img_name, dcm_name):
        im = Image.open(path + img_name + '.jpeg').convert('L')

        file_path = os.path.join(path, img_name + '.jpeg')
        ds = dicom.dcmread(file_path, force=True)

        ds.Rows = im.height
        ds.Columns = im.width
        ds.PhotometricInterpretation = "MONOCHROME1"
        ds.SamplesPerPixel = 1
        ds.BitsStored = 8
        ds.BitsAllocated = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = np.array(im.getdata(), dtype=np.uint8).tobytes()
        ds.save_as(dcm_name)

    def predict_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224), grayscale=True)
        img_arr = image.img_to_array(img)
        img_arr = np.expand_dims(img_arr, axis=0)

        pred = model.predict(img_arr)
        predicted = np.argmax(pred, axis=1)
        labels = {'COVID19': 0, 'NORMAL': 1, 'PNEUMONIA': 2, 'TURBERCULOSIS': 3}
        labels = dict((v, k) for k, v in labels.items())
        predictions = [labels[k] for k in predicted]
        return [e.value for e in Disease if e.name == predictions[0]][0]

    def save_to_file(self, prediction, name_of_file):  # "results.csv"
        results = pd.DataFrame({"Filename": name_of_file,
                                "Predictions": prediction})
        results.to_csv(name_of_file, index=False)
