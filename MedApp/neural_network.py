import os

import numpy as np
import pandas as pd
from keras_preprocessing import image
from tensorflow import keras
from keras.preprocessing.image import ImageDataGenerator
import pydicom as dicom
from PIL import Image
from django.core.files.storage import FileSystemStorage

model = keras.models.load_model("D:/Desktop/Диплом/django+angular/med_site_django/KerasModel", custom_objects=None,
                                compile=True,
                                options=None)

train_generator = ImageDataGenerator(rescale=1. / 255).flow_from_directory(
    directory='D:/Desktop/Диплом/НИР/Workspace/dataset/archive/train',
    target_size=(224, 224),
    color_mode="grayscale",
    batch_size=32,
    class_mode="categorical",
    shuffle=True, seed=42)

test_generator = ImageDataGenerator(rescale=1. / 255).flow_from_directory(
    directory='D:/Desktop/Диплом/НИР/Workspace/dataset/archive/test',
    target_size=(224, 224),
    color_mode="grayscale",
    batch_size=1,
    class_mode=None,
    shuffle=False,
    seed=42)


class Neural_Network():
    def open_dicom(self, image_path, img_name):
        ds = dicom.read_file(image_path)
        file = ds.pixel_array

        # save as jpg
        new_image = file.astype(float)
        scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
        scaled_image = np.uint8(scaled_image)
        final_image = Image.fromarray(scaled_image)

        jpg_path = 'D:/Desktop/Диплом/django+angular/med_site_django/MedApp/temp_storage/' + img_name + '.jpg'

        final_image.save(jpg_path)
        result = self.predict_image(jpg_path)
        os.remove(jpg_path)  # todo set?

        return result

    def jpg_to_dicom(self, path, img_name, dcm_name): # todo change
        im = Image.open(path + img_name + '.jpeg')  # here jpeg or jpg

        file_path = os.path.join(path, '1')
        ds = dicom.dcmread(file_path, force=True)

        if im.mode == 'L':
            np_image = np.array(im.getdata(), dtype=np.uint8)
            ds.Rows = im.height
            ds.Columns = im.width
            ds.PhotometricInterpretation = "MONOCHROME1"
            ds.SamplesPerPixel = 1
            ds.BitsStored = 8
            ds.BitsAllocated = 8
            ds.HighBit = 7
            ds.PixelRepresentation = 0
            ds.PixelData = np_image.tobytes()
            ds.save_as(dcm_name)

        if im.mode == 'RGBA':
            np_image = np.array(im.getdata(), dtype=np.uint8)[:, :3]
            ds.Rows = im.height
            ds.Columns = im.width
            ds.PhotometricInterpretation = "RGB"
            ds.SamplesPerPixel = 3
            ds.BitsStored = 8
            ds.BitsAllocated = 8
            ds.HighBit = 7
            ds.PixelRepresentation = 0
            ds.PixelData = np_image.tobytes()
            ds.save_as(dcm_name)

    def get_diagnosys(self, prediction):
        switcher = {
            "PNEUMONIA": "Пневмония",
            "NORMAL": "Патологий не обнаружено",
            "TURBERCULOSIS": "Туберкулез",
            "COVID19": "Covid-19",
        }
        return switcher.get(prediction)

    def predict_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224), grayscale=True)
        img_arr = image.img_to_array(img)
        img_arr = np.expand_dims(img_arr, axis=0)
        pred = model.predict(img_arr)

        # predict image
        predicted = np.argmax(pred, axis=1)
        labels = (train_generator.class_indices)
        labels = dict((v, k) for k, v in labels.items())
        predictions = [labels[k] for k in predicted]

        return self.get_diagnosys(predictions[0])

    def get_statistic(self):  # result = 79,7%
        # Predict Output
        STEP_SIZE_TEST = test_generator.n // test_generator.batch_size
        test_generator.reset()
        pred = model.predict(test_generator,
                             steps=STEP_SIZE_TEST,
                             verbose=1)

        predicted_class_indices = np.argmax(pred, axis=1)

        labels = (train_generator.class_indices)
        labels = dict((v, k) for k, v in labels.items())
        predictions = [labels[k] for k in predicted_class_indices]

        current_idx = 0
        count_accurate = 0
        Actual = []
        for i in predictions:
            string = test_generator.filenames[current_idx]
            substr = '\\'
            actual = string[:string.find(substr)]
            Actual.append(actual)
            pred = predictions[current_idx]
            if actual == pred:
                count_accurate += 1
            current_idx += 1
        acc = count_accurate / 771
        print(f"The accuracy on predicted the test images is {round(acc * 100, 2)}%.")

    def save_to_file(self, predictions, name_of_file):  # "results.csv"
        results = pd.DataFrame({"Filename": name_of_file,
                                "Predictions": predictions})
        results.to_csv(name_of_file, index=False)
