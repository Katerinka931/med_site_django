import os
from datetime import datetime

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from MedApp.models import Doctor, Patient, Photo, UserRole
from MedApp.dto import DoctorDTO, PatientDTO, DoctorWithPatientsDTO, PhotoDTO
from MedApp.neural_network import Neural_Network, save_file


class MainListClass(APIView):
    def get(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)
        people = ListOfObjects.get_list_of_people_to_main_page(pk, user.role)
        return JsonResponse({'message': 'Список', 'people': people}, safe=False)

    def delete(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)
        people = ListOfObjects.get_list_of_people_to_main_page(pk, user.role)
        remove_id = request.GET.get("remove")

        if remove_id is not None:
            remove_person(remove_id, user.role, 'user')
            people = ListOfObjects.get_list_of_people_to_main_page(pk, user.role)
            return JsonResponse(
                {'message': 'Удаление успешно', 'people': people}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {'message': 'Не выбран удаляемый элемент', 'people': people},
                status=status.HTTP_204_NO_CONTENT)


class PatientsListClass(APIView):
    def get(self, request):
        patients = ListOfObjects.get_patients_list(Patient.objects.all().order_by('last_name'))
        return JsonResponse({'message': '', 'people': patients}, safe=False)

    def delete(self, request):
        pk = request.user.id
        doctor = Doctor.objects.get(id=pk)
        remove_id = request.GET.get("remove")
        if remove_id is not None:
            remove_person(remove_id, doctor.role, 'pat')
            return JsonResponse({'message': 'Удаление успешно'}, safe=False)
        else:
            return JsonResponse({'message': 'Не выбран удаляемый элемент'}, status=status.HTTP_204_NO_CONTENT)


class ProfileClass(APIView):
    @staticmethod
    def parse_password_request(request):
        data = JSONParser().parse(request)
        password = data['password']
        new_password = data['new_password']
        new_password_repeat = data['new_password_repeat']

        return password, new_password, new_password_repeat

    @staticmethod
    def parse_edit_request(request):
        data = JSONParser().parse(request)
        lastname = data['last_name']
        firstname = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        login = data['login']
        return lastname, firstname, middle_name, email, phone, login

    def get(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)
        transfer_object = DoctorDTO(user)
        return JsonResponse({'user': vars(transfer_object)}, safe=False)

    def post(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)
        password, new_password, new_password_repeat = ProfileClass.parse_password_request(request)
        usr = authenticate(username=user.login, password=password)

        if usr is not None:
            if new_password == new_password_repeat:
                if password == new_password:
                    return JsonResponse({'message': 'Старый и новый пароли совпадают'}, status=status.HTTP_409_CONFLICT)
                else:
                    usr.set_password(new_password)
                    usr.save()
                    return JsonResponse({'message': 'Пароль успешно изменен'})
            else:
                return JsonResponse({'message': 'Пароли не совпадают'}, status=status.HTTP_409_CONFLICT)
        else:
            return JsonResponse({'message': 'Неверно введен старый пароль'}, status=status.HTTP_409_CONFLICT)

    def put(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)
        transfer_object = DoctorDTO(user)
        lastname, firstname, middle_name, email, phone, login = ProfileClass.parse_edit_request(request)

        if Doctor.objects.filter(email=email).exclude(pk=user.pk):
            return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует',
                                 'user': vars(transfer_object)}, safe=False)
        else:
            if Doctor.objects.filter(login=login).exclude(pk=user.pk):
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует', 'user': vars(transfer_object)},
                    safe=False)
            else:
                user.create_or_edit_doctor(lastname, firstname, middle_name, email, phone, login, user.role)
                transfer_object = DoctorDTO(user)
                return JsonResponse({'message': 'Редактирование успешно', 'user': vars(transfer_object)},
                                    safe=False)


class CreateUserClass(APIView):
    @staticmethod
    def parse_request(request):
        data = JSONParser().parse(request)
        role = [e.name for e in UserRole if e.value == data['role'].lower()][0]
        last_name = data['last_name']
        first_name = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        login = data['login']
        password = data['password']
        password_repeat = data['password_repeat']
        return role, last_name, first_name, middle_name, email, phone, login, password, password_repeat

    def get(self, request):
        return JsonResponse({'roles': [e.value for e in UserRole if e.name != UserRole.ADMIN.name]})

    def post(self, request):
        doc = Doctor()
        try:
            role, last_name, first_name, middle_name, email, phone, login, password, password_repeat = CreateUserClass.parse_request(
                request)
            try:
                int(phone)
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                    status=status.HTTP_409_CONFLICT)
        except Exception:
            return JsonResponse({'message': 'Все поля должны быть заполнены'},
                                status=status.HTTP_409_CONFLICT)

        if password_repeat == password:
            if Doctor.objects.filter(email=email):
                return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует'},
                                    status=status.HTTP_409_CONFLICT)
            else:
                try:
                    create_auth_user(login, email, password, first_name, last_name)
                    doc.create_or_edit_doctor(last_name, first_name, middle_name, email, phone, login, role)
                    return JsonResponse({'message': 'Пользователь успешно создан'}, status=status.HTTP_200_OK)
                except Exception:
                    return JsonResponse(
                        {'message': 'Пользователь с таким логином уже существует'},
                        status=status.HTTP_409_CONFLICT)
        else:
            return JsonResponse({'message': 'Пароли не совпадают'},
                                status=status.HTTP_403_FORBIDDEN)


class EditUserClass(APIView):
    @staticmethod
    def parse_request(request):
        data = JSONParser().parse(request)
        role = [e.name for e in UserRole if e.value == data['role'].lower()][0]
        lastname = data['last_name']
        firstname = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        login = data['login']
        return role, lastname, firstname, middle_name, email, phone, login

    def get(self, request, usr):
        doctor = Doctor.objects.get(id=usr)
        transfer_object = DoctorDTO(doctor)
        return JsonResponse(
            {'user': vars(transfer_object), 'roles': [e.value for e in UserRole if e.name != UserRole.ADMIN.name]})

    def put(self, request, usr):
        doctor = Doctor.objects.get(id=usr)
        role, lastname, firstname, middle_name, email, phone, login = EditUserClass.parse_request(request)
        try:
            int(phone)
        except ValueError:
            return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                status=status.HTTP_409_CONFLICT)

        if Doctor.objects.filter(email=email).exclude(pk=doctor.pk):
            return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует'},
                                safe=False, status=status.HTTP_409_CONFLICT)
        else:
            try:
                doctor.create_or_edit_doctor(lastname, firstname, middle_name, email, phone, login, role)
                return JsonResponse({'message': 'Редактирование успешно'}, safe=False)
            except Exception:
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует'},
                    safe=False, status=status.HTTP_409_CONFLICT)


class DoctorsInfoClass(APIView):
    def get(self, request, usr):
        doctor = Doctor.objects.get(pk=usr)
        patients = ListOfObjects.get_users_patients(doctor)
        doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)

        return JsonResponse({'user': vars(doctor_transfer_object)}, safe=False)

    def delete(self, request, usr):
        remove_id = request.GET.get("remove")
        doctor = Doctor.objects.get(pk=usr)
        patients = ListOfObjects.get_users_patients(doctor)
        doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)

        if remove_id is not None:
            remove_person(remove_id, doctor.role, 'pat')
            return JsonResponse({'message': 'Удаление успешно', 'user': vars(doctor_transfer_object)}, safe=False)
        else:
            return JsonResponse({'message': 'Не выбран удаляемый элемент', 'user': vars(doctor_transfer_object)},
                                status=status.HTTP_204_NO_CONTENT)


class CreatePatientClass(APIView):
    @staticmethod
    def parse_request(request):
        data = JSONParser().parse(request)
        last_name = data['last_name']
        first_name = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        date_of_birth = data['date_of_birth']
        doctor_number = data['doctor_number']
        return last_name, first_name, middle_name, email, phone, date_of_birth, doctor_number

    def get(self, request):
        doctors = ListOfObjects.get_doctors_list(
            Doctor.objects.all().exclude(role=UserRole.ADMIN.name).exclude(role=UserRole.OPERATOR.name).order_by(
                'last_name'))
        return JsonResponse({'message': '', 'doctors': doctors}, safe=False)

    def post(self, request):
        pk = request.user.id
        patient = Patient()
        try:
            last_name, first_name, middle_name, email, phone, date_of_birth, doc_number = CreatePatientClass.parse_request(
                request)
            try:
                int(phone)
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                    status=status.HTTP_409_CONFLICT)

            if Doctor.objects.get(pk=pk).role == UserRole.DOCTOR.name:
                doctor_number = pk
            else:
                doctor_number = doc_number
        except Exception:
            return JsonResponse({'message': 'Все поля должны быть заполнены'},
                                status=status.HTTP_409_CONFLICT)

        if Patient.objects.filter(email=email):
            return JsonResponse(
                {'message': 'Пациент с таким адресом электронной почты уже существует'}, safe=False)
        else:
            patient.create_patient(last_name, first_name, middle_name, email, phone, date_of_birth, doctor_number)
            return JsonResponse({'message': 'Пациент успешно создан'}, safe=False)


class EditPatientClass(APIView):
    @staticmethod
    def parse_request(request):
        data = JSONParser().parse(request)
        last_name = data['last_name']
        first_name = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        date_of_birth = data['patient']['date_of_birth']
        diagnosis = data['diagnosis']
        doc_number = data['patient']['doctor_number']
        return last_name, first_name, middle_name, email, phone, date_of_birth, diagnosis, doc_number

    def get(self, request, pat):
        patient = Patient.objects.get(pk=pat)
        patients_doctor = Doctor.objects.get(pk=patient.doctor_number_id)
        patient_transfer = PatientDTO(patient, patients_doctor)
        doctors = ListOfObjects.get_doctors_list(
            Doctor.objects.all().exclude(role=UserRole.ADMIN.name).exclude(role=UserRole.OPERATOR.name).order_by(
                'last_name'))

        try:
            photo = Photo.objects.filter(patient_number_id=pat).get(actual=1)
            file = photo.convert_image(photo.photo)
            photo_transfer = PhotoDTO(photo, file)
        except Exception:
            photo_transfer = "Изображение еще не загружено"  # todo another response delete photo? и в ангуляре соответственно
            return JsonResponse(
                {'message': 'Изображение еще не загружено', 'patient': vars(patient_transfer), 'photo': photo_transfer,
                 'doctors': doctors},
                safe=False)

        return JsonResponse(
            {'message': '', 'patient': vars(patient_transfer), 'photo': vars(photo_transfer), 'doctors': doctors},
            safe=False)

    def put(self, request, pat):
        pk = request.user.id
        patient = Patient.objects.get(pk=pat)

        photos_instances = Photo.objects.filter(patient_number_id=pat)
        photo = photos_instances.get(actual=1) if photos_instances else Photo()

        try:
            lastname, firstname, middle_name, email, phone, date_of_birth, diagnosis, doc_number \
                = EditPatientClass.parse_request(request)
            try:
                int(phone)
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'}, status=status.HTTP_409_CONFLICT)

            doctor_number = pk if Doctor.objects.get(pk=pk).role == UserRole.DOCTOR.name else doc_number
        except Exception:
            return JsonResponse({'message': 'Все поля должны быть заполнены'}, status=status.HTTP_409_CONFLICT)

        if Patient.objects.filter(email=email).exclude(pk=pat):
            return JsonResponse({'message': 'Пациент с таким адресом электронной почты уже существует'}, safe=False,
                                status=status.HTTP_409_CONFLICT)
        else:
            try:
                patient.create_patient(lastname, firstname, middle_name, email, phone, date_of_birth, doctor_number)
                photo.diagnosis = diagnosis
                photo.save()
                return JsonResponse({'message': 'Редактирование успешно'}, safe=False)
            except Exception:
                return JsonResponse({'message': 'Неверно введена дата рождения'}, safe=False,
                                    status=status.HTTP_409_CONFLICT)


class PatientsInfoClass(APIView):
    def get(self, request, pat):
        patient = Patient.objects.get(pk=pat)
        patients_doctor = Doctor.objects.get(pk=patient.doctor_number_id)
        photos_request = request.GET.get("photo")
        photo_objects = Photo.objects.filter(patient_number_id=pat)
        if photos_request == '1':

            photos = ListOfObjects.get_photos_list(photo_objects)
            return JsonResponse({'message': '', 'photos': photos},
                                safe=False)
        else:
            patient_transfer = PatientDTO(patient, patients_doctor)
            try:
                photo = Photo.objects.filter(patient_number_id=pat).get(actual=1)
                file = photo.convert_image(photo.photo)
                photo_transfer = PhotoDTO(photo, file)
                return JsonResponse({'message': '', 'patient': vars(patient_transfer), 'photo': vars(photo_transfer)},
                                    safe=False)
            except Exception:
                photo_transfer = "Изображение еще не загружено"
                return JsonResponse({'message': '', 'patient': vars(patient_transfer), 'photo': photo_transfer},
                                    safe=False)

    def delete(self, request, pat):
        photo_id = request.GET.get('id')
        photo_objects = Photo.objects.filter(patient_number_id=pat)
        deleted_photo = photo_objects.get(pk=photo_id)
        path = deleted_photo.photo
        deleted_photo.delete()
        os.remove(path)

        list_of_photos = ListOfObjects.get_photos_list(photo_objects)
        if len(list_of_photos) > 0:
            new_actual_photo_id = list_of_photos[0]['id']
            Photo.objects.filter(pk=new_actual_photo_id).update(actual=1)

        return JsonResponse({'message': 'Фото удалено'}, safe=False)


class LoadImageClass(GenericViewSet):
    neural_network_instance_var = Neural_Network()
    photo_object_var = Photo()

    @staticmethod
    def parse_save_request(request):
        custom_diagnosis = request.POST.get('custom_diagnosis')
        diagnosis = request.POST.get('diagnosis')

        if custom_diagnosis is not None:
            diagnosis += '. ' + custom_diagnosis

        patient_id = request.POST.get('pat_id')
        return diagnosis, patient_id

    @staticmethod
    def parse_file_data(request):
        img = request.FILES['file']
        fs, filename, file_url = save_file(img)  # сохранение дикома

        try:
            final_image, jpg_path = LoadImageClass.neural_network_instance_var.dicom_to_jpg(file_url, filename)
        except Exception:
            raise Exception()
        finally:
            fs.delete(filename)

        final_image.save(jpg_path)  # сохранение изо
        fs.delete(filename)  # удаление дикома ?????????????????????????????????

        return jpg_path, file_url

    def get(self, request):
        pk = request.user.id
        user = Doctor.objects.get(pk=pk)

        patients = ListOfObjects.get_patients_list(
            Patient.objects.all()) if user.role == UserRole.CHIEF.name else ListOfObjects.get_patients_list(
            Patient.objects.filter(doctor_number_id=pk))

        return JsonResponse({'message': '', 'patients': patients}, safe=False)

    def post_predict(self, request):
        try:
            jpg_path, file_url = LoadImageClass.parse_file_data(request)
        except Exception:
            return JsonResponse({'message': 'Неверный тип файла: загрузите .dcm'}, status=status.HTTP_409_CONFLICT)

        result = LoadImageClass.neural_network_instance_var.predict_image(jpg_path)
        file = LoadImageClass.photo_object_var.convert_image(jpg_path)
        os.remove(jpg_path)
        return JsonResponse({'message': result, 'file': file})

    def post_save(self, request):
        date = datetime.fromtimestamp(int(request.POST['date'][0:10]))  # дата создания дикома

        try:
            jpg_path, file_url = LoadImageClass.parse_file_data(request)
        except Exception:
            return JsonResponse({'message': 'Неверный тип файла: загрузите .dcm'}, status=status.HTTP_409_CONFLICT)

        diagnosis, patient_id = LoadImageClass.parse_save_request(request)
        patient = Patient.objects.get(pk=patient_id)
        photos_instances = Photo.objects.filter(patient_number=patient_id)

        if photos_instances:
            current_photo = photos_instances.get(actual=1)  # проверка фото по дате (является ли новым)
            if current_photo.date_of_creation.timestamp() > date.timestamp():
                return JsonResponse({'message': 'Фото сделано раньше, чем актуальный вариант.'})
        try:
            LoadImageClass.photo_object_var.save_photo(patient, file_url, diagnosis, date)
            patient.save()
        except Exception:
            os.remove(jpg_path)
            return JsonResponse({'message': 'Фото с таким именем уже есть в хранилище и в базе данных. '})

        return JsonResponse({'message': 'Данные сохранены'})


# ----------------------- additional classes -----------------------#
class ListOfObjects:
    @staticmethod
    def get_patients_list(patients_queryset):
        """
        Method converts queryset of patients to the list
        :param patients_queryset: queryset of patients from database
        :return: list of patients
        """
        patients = list()
        for patient in patients_queryset:
            patients.append({'id': patient.pk, 'first_name': patient.first_name, 'last_name': patient.last_name,
                             'middle_name': patient.middle_name, 'date_of_birth': patient.date_of_birth,
                             'email': patient.email, 'phone': patient.phone})
        return patients

    @staticmethod
    def get_doctors_list(doctors_queryset):
        """
        Method converts queryset of doctors to the list
        :param doctors_queryset: queryset of doctors from database
        :return: list of doctors
        """
        doctors = list()
        for doctor in doctors_queryset:
            doctors.append(
                {'id': doctor.pk, 'role': doctor.role, 'login': doctor.login, 'email': doctor.email,
                 'phone': doctor.phone,
                 'first_name': doctor.first_name, 'last_name': doctor.last_name, 'middle_name': doctor.middle_name})
        return doctors

    @staticmethod
    def get_list_of_people_to_main_page(pk, user_role):
        """
        Method checks user`s role and creates a list from queryset according to the role
        :param pk: identifier of the user
        :param user_role:
        :return: list of people according to user`s role
        """
        if user_role == UserRole.ADMIN.name:
            people = ListOfObjects.get_doctors_list(Doctor.objects.all().exclude(pk=pk).order_by('last_name'))
        elif user_role == UserRole.CHIEF.name:
            people = ListOfObjects.get_doctors_list(
                Doctor.objects.filter(role=UserRole.DOCTOR.name).order_by('last_name'))
        elif user_role == UserRole.OPERATOR.name:
            people = ListOfObjects.get_patients_list(Patient.objects.all().order_by('last_name'))
        else:
            people = ListOfObjects.get_patients_list(Patient.objects.filter(doctor_number_id=pk).order_by('last_name'))
        return people

    @staticmethod
    def get_users_patients(doctor):
        """
        :param doctor: user
        :return: list of patients
        """
        return ListOfObjects.get_patients_list(
            Patient.objects.all().order_by('last_name')) if doctor.role == UserRole.OPERATOR.name \
            else ListOfObjects.get_patients_list(Patient.objects.filter(doctor_number=doctor.pk).order_by('last_name'))

    @staticmethod
    def get_photos_list(photo_queryset):

        photos = list()
        for photo in photo_queryset:
            file = photo.convert_image(photo.photo)
            photos.append({'id': photo.pk, 'photo': file, 'diagnosis': photo.diagnosis,
                           'date': photo.date_of_creation.strftime('%d.%m.%Y, %H:%M:%S')})
        return photos


# ----------------------- additional functions to change-----------------------#
def remove_person(remove_id, user_role, deleted_person_type):
    if (user_role == UserRole.ADMIN.name or user_role == UserRole.CHIEF.name) and deleted_person_type == 'user':
        doctor = Doctor()
        doctor.remove_doctor(remove_id)
    else:
        patient = Patient()
        patient.remove_patient(remove_id)


def create_auth_user(login, email, password, firstname, lastname):
    user = User.objects.create_user(login, email, password)
    user.first_name = firstname
    user.last_name = lastname
    user.save()


@api_view(['POST'])
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Вы вышли из системы'}, status=status.HTTP_200_OK)
