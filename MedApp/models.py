from django.db import models
from django.contrib.auth.models import User
import base64

class Doctor(models.Model):
    role = models.CharField(max_length=100)
    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=20, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True)

    def create_or_edit_doctor(self, lastname, firstname, middlename, email, phone, login, role):
        if self.pk == None:
            doctor = Doctor()
        else:
            doctor = self

        doctor.role = role
        doctor.last_name = lastname
        doctor.first_name = firstname
        doctor.middle_name = middlename
        doctor.email = email
        doctor.phone = phone
        doctor.login = login
        doctor.save()


    def remove_doctor(self, id):
        remove_doctor = Doctor.objects.get(pk=id)
        User.objects.get(username=remove_doctor.login).delete()
        remove_doctor.delete()


    def edit_doctor(self, id):
        doctor = Doctor.objects.get(pk=id)


class Patient(models.Model):
    doctor_number = models.ForeignKey(Doctor, on_delete=models.CASCADE, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateField()

    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)

    def create_patient(self, lastname, firstname, middlename, email, phone, date, doctor_number):
        if self.id == None:
            patient = Patient()
        else:
            patient = self

        patient.last_name = lastname
        patient.first_name = firstname
        patient.middle_name = middlename
        patient.email = email
        patient.phone = phone
        patient.date_of_birth = date
        patient.doctor_number_id = doctor_number
        patient.save()

    def remove_patient(self, id):
        Patient.objects.get(pk=id).delete()


class Photo(models.Model):
    patient_number = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True)
    photo = models.CharField(max_length=100, unique=True)
    actual = models.CharField(max_length=5)
    diagnosys = models.CharField(max_length=10000, null=True)
    date_of_creation = models.DateField(null=True)

    # еще одно поле в бд для сохранения пути к дикому? возможно стоит!

    def save_photo(self, patient, loaded_file, diagnosys):
        photo = Photo()
        photo.photo = loaded_file + '.jpeg'

        Photo.objects.filter(patient_number_id=patient.pk).update(actual=0) # делаем все предыдущие неактуальными
        photo.diagnosys = diagnosys
        photo.actual = 1
        photo.patient_number = patient
        photo.save()

    def convert_image(self, jpg_path):
        with open(jpg_path, "rb") as image:
            f = image.read()
            b = bytearray(f)
        b64 = base64.b64encode(b)
        return b64.decode('utf-8')
