from MedApp.models import User, Patient, Photo
from datetime import datetime


class DoctorDTO(object):
    def __init__(self, doctor: User):
        self.id = doctor.id
        self.role = User.get_role_in_russian(doctor.role)
        self.login = doctor.username
        self.email = doctor.email
        self.phone = doctor.phone
        self.first_name = doctor.first_name
        self.last_name = doctor.last_name
        self.middle_name = doctor.middle_name


class DoctorWithPatientsDTO(object):
    def __init__(self, doctor: User, patients: list):
        self.id = doctor.id
        self.role = User.get_role_in_russian(doctor.role)
        self.login = doctor.username
        self.email = doctor.email
        self.phone = doctor.phone
        self.first_name = doctor.first_name
        self.last_name = doctor.last_name
        self.middle_name = doctor.middle_name

        if patients is not None:
            self.patients = patients


class PatientDTO(object):
    def __init__(self, patient: Patient, doctor: User):
        self.id = patient.id
        self.first_name = patient.first_name
        self.last_name = patient.last_name
        self.middle_name = patient.middle_name
        self.date_of_birth = patient.date_of_birth
        self.email = patient.email
        self.phone = patient.phone
        self.doctor = {
            'id': doctor.id,
            'role': User.get_role_in_russian(doctor.role),
            'email': doctor.email,
            'phone': doctor.phone,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'middle_name': doctor.middle_name
        }


class PhotoDTO(object):
    def __init__(self, photo: Photo, file):
        self.id = photo.id
        self.actual = photo.actual
        self.diagnosis = photo.diagnosis
        self.patient = photo.patient_number_id
        self.photo = file
        self.date_of_creation = datetime.timestamp(photo.date_of_creation)
        self.date_of_research = photo.date_of_research
        self.researcher = photo.researcher
