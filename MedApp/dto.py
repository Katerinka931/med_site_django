from MedApp.models import Doctor, Patient, Photo


class DoctorDTO(object):
    def __init__(self, doctor: Doctor):
        self.id = doctor.id
        self.role = doctor.role
        self.login = doctor.login
        self.email = doctor.email
        self.phone = doctor.phone
        self.first_name = doctor.first_name
        self.last_name = doctor.last_name
        self.middle_name = doctor.middle_name


class DoctorWithPatientsDTO(object):
    def __init__(self, doctor: Doctor, patients: list):
        self.id = doctor.id
        self.role = doctor.role
        self.login = doctor.login
        self.email = doctor.email
        self.phone = doctor.phone
        self.first_name = doctor.first_name
        self.last_name = doctor.last_name
        self.middle_name = doctor.middle_name

        if patients is not None:
            self.patients = patients


class PatientDTO(object):
    def __init__(self, patient: Patient, doctor: Doctor):
        self.id = patient.id
        self.first_name = patient.first_name
        self.last_name = patient.last_name
        self.middle_name = patient.middle_name
        self.date_of_birth = patient.date_of_birth
        self.email = patient.email
        self.phone = patient.phone
        self.diagnosys = patient.diagnosys
        self.doctor = {
            'id': doctor.id,
            'role': doctor.role,
            'login': doctor.login,
            'email': doctor.email,
            'phone': doctor.phone,
            'first_name': doctor.first_name,
            'last_name': doctor.last_name,
            'middle_name': doctor.middle_name
        }

class PhotoDTO(object):
    def __init__(self, photo: Photo):
        self.id = photo.id
        self.actual = photo.actual
        self.number_of_instance = photo.number_of_instance
        self.patient = photo.patient_number_id
        self.photo = photo.photo


