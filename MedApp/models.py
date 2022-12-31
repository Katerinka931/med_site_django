import os
from enum import Enum

from django.db import models
from django.contrib.auth.models import User
import base64


class UserRole(Enum):
    DOCTOR = 'врач'
    CHIEF = 'главный врач'
    OPERATOR = 'оператор'
    ADMIN = 'администратор'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    # print([e.value for e in UserRole])
    # print([e.name for e in UserRole])

class Doctor(models.Model):
    role = models.CharField(max_length=100)
    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=20, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Last name: {self.last_name} \n First name: {self.first_name} \n Middle name: {self.middle_name} \n Role: {self.role} \n Login: {self.login} \n Email: {self.email} \n Phone {self.phone}"

    def create_or_edit_doctor(self, lastname, firstname, middle_name, email, phone, login, role):
        doctor = Doctor() if self.pk is None else self
        doctor.role = role
        doctor.last_name = lastname
        doctor.first_name = firstname
        doctor.middle_name = middle_name
        doctor.email = email
        doctor.phone = phone
        doctor.login = login
        doctor.save()

    def remove_doctor(self, pk):
        remove_doctor = Doctor.objects.get(pk=pk)
        User.objects.get(username=remove_doctor.login).delete()
        remove_doctor.delete()


class Patient(models.Model):
    doctor_number = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateField()

    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"Last name: {self.last_name} \n First name: {self.first_name} \n Middle name: {self.middle_name} \n Date of birth: {self.date_of_birth} \n Doctor: {self.doctor_number} \n Email: {self.email} \n Phone {self.phone}"

    def create_patient(self, lastname, firstname, middle_name, email, phone, date, doctor_number):
        patient = Patient() if self.id is None else self
        patient.last_name = lastname
        patient.first_name = firstname
        patient.middle_name = middle_name
        patient.email = email
        patient.phone = phone
        patient.date_of_birth = date
        patient.doctor_number_id = doctor_number
        patient.save()

    def remove_patient(self, pk):
        Patient.objects.get(pk=pk).delete()


class Photo(models.Model):
    patient_number = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True)
    photo = models.CharField(max_length=100, unique=True)  # null = true!
    actual = models.CharField(max_length=5)
    diagnosis = models.CharField(max_length=10000, null=True)
    date_of_creation = models.DateTimeField(null=True)

    # todo еще одно поле в бд для сохранения пути к дикому? возможно стоит! или называть оба файла одинаково, в бд хранить только имя, а при извлечении сделать метод,
    #  который получает или диком, или жпег

    class Meta:
        ordering = ["patient_number_id", "-date_of_creation"]

    def __str__(self):
        return f"Photo name: {self.photo} \n Actual: {self.actual} \n Diagnosis: {self.diagnosis} \n Date of creation: {self.date_of_creation} \n Patient: {self.patient_number}"

    def convert_image(self, jpg_path):
        with open(jpg_path, "rb") as image:
            f = image.read()
            b = bytearray(f)
        b64 = base64.b64encode(b)
        return b64.decode('utf-8')

    def get_absolute_photo_path(self, name):
        return os.getcwd() + '/temp_storage/' + name


    # todo change savings as previous classes
    def save_photo(self, patient, loaded_file, diagnosis, date):
        photo = Photo()
        # todo .jpeg?
        photo.photo = loaded_file + '.jpeg'

        Photo.objects.filter(patient_number_id=patient.pk).update(actual=0)  # делаем все предыдущие неактуальными
        photo.diagnosis = diagnosis
        photo.actual = 1
        photo.patient_number = patient
        photo.date_of_creation = date
        photo.save()
