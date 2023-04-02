import os

from MedApp.models import Photo, Patient, User
from MedApp.neural_network import NeuralNetwork, save_file


class ParsingAndEditUtils:
    @staticmethod
    def parse_and_save_images(img, flag):

        if flag:
            try:
                ph = Photo.objects.get(photo=img)
            except Exception:
                ph = Photo.objects.none()

            if ph:
                raise ValueError

        fs, filename, file_url = save_file(img)  # сохранение dcm

        try:
            final_image, jpg_path = NeuralNetwork.convert_dicom_to_jpg(file_url, filename)
        except Exception:
            ParsingAndEditUtils.remove_images(filename)
            raise Exception()
        final_image.save(jpg_path)  # сохранение jpeg
        return filename

    @staticmethod
    def remove_images(filename):
        os.remove(Photo.get_absolute_file_path(filename))
        os.remove(Photo.get_absolute_file_path(filename, '.jpeg'))

    @staticmethod
    def remove_person(remove_id, user_role, deleted_person_type):
        if (user_role == User.ADMIN or user_role == User.CHIEF) and deleted_person_type == 'user':
            doctor = User()
            doctor.remove_user(remove_id)
        else:
            patient = Patient()
            patient.remove_patient(remove_id)


class CheckingUtils:
    @staticmethod
    def check_phone(phone):
        try:
            int(phone)
            return True
        except ValueError:
            return False