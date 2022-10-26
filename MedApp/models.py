from django.db import models
from django.contrib.auth.models import User


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

    diagnosys = models.CharField(max_length=10000, null=True)

    def create_patient(self, lastname, firstname, middlename, email, phone, date, doctor_number, diagnosys):
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
        patient.diagnosys = diagnosys
        patient.save()

    def remove_patient(self, id):
        Patient.objects.get(pk=id).delete()


class Photo(models.Model):
    patient_number = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True)
    photo = models.CharField(max_length=100)
    number_of_instance = models.CharField(max_length=10)
    actual = models.CharField(max_length=5)

    def save_photo(self, patient_id, loaded_file):
        photo = Photo()
        photo.photo = loaded_file
        # photo.number_of_instance
        # photo.actual
        photo.patient_number = 18#patient_id
        photo.save()
