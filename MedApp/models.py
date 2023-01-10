import os
import base64

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ADMIN = 1
    CHIEF = 2
    DOCTOR = 3
    OPERATOR = 4

    ROLE_CHOICES = (
        (ADMIN, 'администратор'),
        (CHIEF, 'главный врач'),
        (DOCTOR, 'врач'),
        (OPERATOR, 'оператор'),
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, null=True)
    middle_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Last name: {self.last_name} \n First name: {self.first_name} \n Middle name: {self.middle_name} \n Role: {self.role} \n Login: {self.username} \n Email: {self.email} \n Phone {self.phone}"


    @staticmethod
    def get_name_roles():
        return ['ADMIN', 'CHIEF', 'DOCTOR', 'OPERATOR'] #TODO delete


    @staticmethod
    def index_to_role_for_old_model(index):  # todo temp in token serializer remove when roles will correct
        if index == 1:
            role_to_send = 'ADMIN'
        elif index == 2:
            role_to_send = 'CHIEF'
        elif index == 3:
            role_to_send = 'DOCTOR'
        else:
            role_to_send = 'OPERATOR'
        return role_to_send

    @staticmethod
    def get_role_in_russian(index):
        return [role[1] for role in User.ROLE_CHOICES if role[0] == index][0]


    @staticmethod
    def get_allowed_roles(*roles):
        all_roles = [role for role in User.ROLE_CHOICES]
        if len(roles) != 0:
            for role in roles:
                for item in all_roles:
                    if role == item[0]:
                        all_roles.remove(item)

        new_l = [role_name[1] for role_name in all_roles]
        return new_l

    def create_or_edit_user(self, flag, login, email, password, firstname, lastname, middlename, phone, role):
        if flag:
            user = User.objects.create_user(login, email, password)
        else:
            user = self
        user.first_name = firstname
        user.last_name = lastname
        user.middle_name = middlename
        user.phone = phone
        user.role = role
        user.save()

    def remove_doctor(self, pk):
        remove_doctor = User.objects.get(pk=pk)
        User.objects.get(username=remove_doctor.login).delete()
        remove_doctor.delete()


class Patient(models.Model):
    doctor_number = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

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
    photo = models.CharField(max_length=100, unique=True, null=True)  # null = true!
    actual = models.CharField(max_length=5)
    diagnosis = models.CharField(max_length=10000, null=True)
    date_of_creation = models.DateTimeField(null=True)

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

    @staticmethod
    def get_absolute_file_path(name, *ext):
        path = os.getcwd() + '/temp_storage/' + name
        return path + ext[0] if len(ext) > 0 else path

    @staticmethod
    def create_photo(patient, filename, diagnosis, date):
        photo = Photo()
        photo.photo = filename

        Photo.objects.filter(patient_number_id=patient.pk).update(actual=0)
        photo.diagnosis = diagnosis
        photo.actual = 1
        photo.patient_number = patient
        photo.date_of_creation = date
        photo.save()
