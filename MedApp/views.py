import os

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import *
from MedApp.models import Doctor, Patient, Photo
from MedApp.dto import DoctorDTO, PatientDTO, DoctorWithPatientsDTO, PhotoDTO
from MedApp.neural_network import Neural_Network, save_file


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'DELETE'])
def main(request):
    pk = request.user.id
    remove_id = request.GET.get("remove")

    user = Doctor.objects.get(pk=pk)
    people = get_list_of_people(pk, user.role)

    if request.method == 'GET':
        return JsonResponse({'message': 'Список', 'people': people}, safe=False)

    if request.method == 'DELETE':
        if remove_id != None:
            remove_person(remove_id, user.role, 'user')
            people = get_list_of_people(pk, user.role)
            return JsonResponse(
                {'message': 'Удаление успешно', 'people': people}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {'message': 'Не выбран удаляемый элемент', 'people': people},
                status=status.HTTP_204_NO_CONTENT)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'DELETE'])
def patients_list(request):
    pk = request.user.id
    doctor = Doctor.objects.get(id=pk)

    patients = get_patients_list(Patient.objects.all().order_by('last_name'))
    remove_id = request.GET.get("remove")

    if request.method == 'DELETE':
        if remove_id != None:
            remove_person(remove_id, doctor.role, 'pat')
            return JsonResponse({'message': 'Удаление успешно'}, safe=False)

    if request.method == 'GET':
        return JsonResponse({'message': '', 'people': patients}, safe=False)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST', 'PUT'])
def profile(request):
    pk = request.user.id
    user = Doctor.objects.get(pk=pk)
    transfer_object = DoctorDTO(user)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        password = data['password']
        new_password = data['new_password']
        new_password_repeat = data['new_password_repeat']

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

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        lastname = data['last_name']
        firstname = data['first_name']
        middlename = data['middle_name']
        email = data['email']
        phone = data['phone']
        login = data['login']

        if Doctor.objects.filter(email=email).exclude(pk=user.pk):
            return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует',
                                 'user': vars(transfer_object)}, safe=False)
        else:
            if Doctor.objects.filter(login=login).exclude(pk=user.pk):
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует', 'user': vars(transfer_object)},
                    safe=False)
            else:
                user.create_or_edit_doctor(lastname, firstname, middlename, email, phone, login, user.role)
                transfer_object = DoctorDTO(user)
                return JsonResponse({'message': 'Редактирование успешно', 'user': vars(transfer_object)},
                                    safe=False)

    if request.method == 'GET':
        return JsonResponse({'user': vars(transfer_object)}, safe=False)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def create_user(request):
    data = JSONParser().parse(request)
    doc = Doctor()

    if request.method == 'POST':
        try:
            role = define_role(data['role'].lower())
            last_name = data['last_name']
            first_name = data['first_name']
            middle_name = data['middle_name']
            email = data['email']
            phone = data['phone']
            try:
                int(data['phone'])
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                    status=status.HTTP_409_CONFLICT)

            login = data['login']
            password = data['password']
            password_repeat = data['password_repeat']
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

    return JsonResponse({'message': ''}, safe=False)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'PUT'])
def edit_user(request, usr):
    doctor = Doctor.objects.get(id=usr)
    transfer_object = DoctorDTO(doctor)

    if request.method == 'GET':
        return JsonResponse({'user': vars(transfer_object)})

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        role = define_role(data['role'].lower())
        lastname = data['last_name']
        firstname = data['first_name']
        middlename = data['middle_name']
        email = data['email']
        phone = data['phone']
        try:
            int(data['phone'])
        except ValueError:
            return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                status=status.HTTP_409_CONFLICT)
        login = data['login']

        if Doctor.objects.filter(email=email).exclude(pk=doctor.pk):
            return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует'},
                                safe=False, status=status.HTTP_409_CONFLICT)
        else:
            try:
                doctor.create_or_edit_doctor(lastname, firstname, middlename, email, phone, login, role)
                return JsonResponse({'message': 'Редактирование успешно'}, safe=False)
            except Exception:
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует'},
                    safe=False, status=status.HTTP_409_CONFLICT)


@api_view(['GET', 'DELETE'])
def doctors_info(request, usr):
    remove_id = request.GET.get("remove")
    doctor = Doctor.objects.get(pk=usr)

    if request.method == 'GET':
        patients = get_patients(doctor)
        doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)

        return JsonResponse(
            {'user': vars(doctor_transfer_object)}, safe=False)

    if request.method == 'DELETE':
        if remove_id != None:
            remove_person(remove_id, doctor.role, 'pat')

            patients = get_patients(doctor)
            doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)
            return JsonResponse({'message': 'Удаление успешно', 'user': vars(doctor_transfer_object)}, safe=False)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def create_patient(request):
    pk = request.user.id
    patient = Patient()

    if request.method == 'GET':
        doctors = get_doctors_list(
            Doctor.objects.all().exclude(role='ADMIN').exclude(role='OPERATOR').order_by('last_name'))
        return JsonResponse({'message': '', 'doctors': doctors}, safe=False)

    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            last_name = data['last_name']
            first_name = data['first_name']
            middle_name = data['middle_name']
            email = data['email']
            phone = data['phone']
            try:
                int(data['phone'])
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'},
                                    status=status.HTTP_409_CONFLICT)
            date_of_birth = data['date_of_birth']
            if Doctor.objects.get(pk=pk).role == 'DOCTOR':
                doctor_number = pk
            else:
                doctor_number = data['doctor_number']
        except Exception:
            return JsonResponse({'message': 'Все поля должны быть заполнены'},
                                status=status.HTTP_409_CONFLICT)

        if Patient.objects.filter(email=email):
            return JsonResponse(
                {'message': 'Пациент с таким адресом электронной почты уже существует'}, safe=False)
        else:
            patient.create_patient(last_name, first_name, middle_name, email, phone, date_of_birth, doctor_number)
            return JsonResponse({'message': 'Пациент успешно создан'}, safe=False)


@api_view(['GET', 'PUT'])
def edit_patient(request, pat):
    pk = request.user.id
    patient = Patient.objects.get(pk=pat)
    patients_doctor = Doctor.objects.get(pk=patient.doctor_number_id)
    patient_transfer = PatientDTO(patient, patients_doctor)
    doctors = get_doctors_list(
        Doctor.objects.all().exclude(role='ADMIN').exclude(role='OPERATOR').order_by('last_name'))

    try:
        photo = Photo.objects.filter(patient_number_id=pat).get(actual=1)
        file = photo.convert_image(photo.photo)
        photo_transfer = PhotoDTO(photo, file)
    except Exception:
        photo_transfer = "Изображение еще не загружено"
        return JsonResponse({'message': '', 'patient': vars(patient_transfer), 'photo': photo_transfer},
                            safe=False)

    if request.method == 'GET':
        return JsonResponse({'message': '', 'patient': vars(patient_transfer), 'photo': vars(photo_transfer), 'doctors': doctors}, safe=False)

    if request.method == 'PUT':
        try:
            data = JSONParser().parse(request)
            lastname = data['patient']['last_name']
            firstname = data['patient']['first_name']
            middlename = data['patient']['middle_name']
            email = data['patient']['email']
            phone = data['patient']['phone']
            try:
                int(phone)
            except ValueError:
                return JsonResponse({'message': 'Некорректный ввод номера телефона'}, status=status.HTTP_409_CONFLICT)

            date_of_birth = data['patient']['date_of_birth']
            diagnosys = data['diagnosys']

            if Doctor.objects.get(pk=pk).role == 'DOCTOR':
                doctor_number = pk
            else:
                doctor_number = data['patient']['doctor_number']
        except Exception:
            return JsonResponse({'message': 'Все поля должны быть заполнены'},
                                status=status.HTTP_409_CONFLICT)

        if Patient.objects.filter(email=email).exclude(pk=pat):
            return JsonResponse(
                {'message': 'Пациент с таким адресом электронной почты уже существует'}, safe=False,
                status=status.HTTP_409_CONFLICT)
        else:
            try:
                patient.create_patient(lastname, firstname, middlename, email, phone, date_of_birth, doctor_number)
                photo.diagnosys = diagnosys
                photo.save()
                return JsonResponse({'message': 'Редактирование успешно'}, safe=False)
            except Exception:
                return JsonResponse({'message': 'Неверно введена дата рождения'}, safe=False,
                                    status=status.HTTP_409_CONFLICT)


def get_photos_list(photo_queryset):
    photos = list()
    for photo in photo_queryset:
        file = photo.convert_image(photo.photo)
        photos.append({'id': photo.pk, 'photo': file, 'diagnosys': photo.diagnosys})
    return photos


@api_view(['GET', 'POST'])
def patients_info(request, pat):
    patient = Patient.objects.get(pk=pat)
    patients_doctor = Doctor.objects.get(pk=patient.doctor_number_id)
    if request.method == 'GET':
        photos_request = request.GET.get("photo")
        if photos_request == '1':
            photo_objects = Photo.objects.filter(patient_number_id=pat)  # .order_by('') по дате создания
            photos = get_photos_list(photo_objects)
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


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def load_image(request):
    act = request.GET.get('act')
    patients = get_patients_list(Patient.objects.all().order_by('last_name'))

    processing = Neural_Network()
    photo_object = Photo()

    if request.method == 'POST':
        img = request.FILES['file']
        fs, filename, file_url = save_file(img)  # сохранение дикома

        try:
            final_image, jpg_path = processing.dicom_to_jpg(file_url, filename)
        except Exception:
            return JsonResponse({'message': 'Неверный тип файла: загрузите .dcm'}, status=status.HTTP_409_CONFLICT)

        final_image.save(jpg_path)  # сохранение изо
        fs.delete(filename)  # удаление дикома

        if act == 'save':
            custom_diagnosys = request.POST.get('custom_diagnosys')
            diagnosys = request.POST.get('diagnosys')
            if custom_diagnosys != None:
                diagnosys += '. ' + custom_diagnosys
            patient_id = request.POST.get('pat_id')

            patient = Patient.objects.get(pk=patient_id)
            patient.diagnosys = diagnosys

            try:
                photo_object.save_photo(patient, file_url, diagnosys)
                patient.save()
            except Exception:
                return JsonResponse({'message': 'Фото с таким именем уже есть в хранилище и в базе данных'})

            return JsonResponse({'message': 'Данные сохранены'})
        else:
            result = processing.predict_image(jpg_path)
            file = photo_object.convert_image(jpg_path)
            os.remove(jpg_path)
            return JsonResponse({'message': result, 'file': file})

    return JsonResponse({'message': '', 'patients': patients}, safe=False)


# ----------------------- new additional functions -----------------------#
def get_patients_list(patients_queryset):
    patients = list()
    for patient in patients_queryset:
        patients.append({'id': patient.pk, 'first_name': patient.first_name, 'last_name': patient.last_name,
                         'middle_name': patient.middle_name, 'date_of_birth': patient.date_of_birth,
                         'email': patient.email, 'phone': patient.phone})
    return patients


def get_doctors_list(doctors_queryset):
    doctors = list()
    for doctor in doctors_queryset:
        doctors.append(
            {'id': doctor.pk, 'role': doctor.role, 'login': doctor.login, 'email': doctor.email,
             'phone': doctor.phone,
             'first_name': doctor.first_name, 'last_name': doctor.last_name, 'middle_name': doctor.middle_name})
    return doctors


def get_list_of_people(pk, user_role):
    if user_role == 'ADMIN':
        people = get_doctors_list(Doctor.objects.all().exclude(pk=pk).order_by('last_name'))
    elif user_role == 'CHIEF':
        people = get_doctors_list(Doctor.objects.filter(role='DOCTOR').order_by('last_name'))
    elif user_role == 'OPERATOR':
        people = get_patients_list(Patient.objects.all().order_by('last_name'))
    else:
        people = get_patients_list(Patient.objects.filter(doctor_number_id=pk).order_by('last_name'))
    return people


def get_patients(doctor):
    return get_patients_list(
        Patient.objects.all().order_by('last_name')) if doctor.role == 'OPERATOR' else get_patients_list(
        Patient.objects.filter(doctor_number=doctor.pk).order_by('last_name'))


def remove_person(remove_id, user_role, deleted_person_type):
    if (user_role == 'ADMIN' or user_role == 'CHIEF') and deleted_person_type == 'user':
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


def define_role(role):
    switcher = {
        "врач": 'DOCTOR',
        "главный врач": 'CHIEF',
        "оператор": 'OPERATOR',
    }
    return switcher.get(role)


@api_view(['POST'])
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Вы вышли из системы'}, status=status.HTTP_200_OK)

# todo all desires

# todo исправлять! диагноз теперь относится к конкретной фотографии!

#  1. История фотографий.
#       1) указание даты создания файла (dicom) !!

#   2) удаление инстанса фото
#  при удалении фото настроить внешний вид данных


#  2. отображать в ангуляре процесс загрузки и обработки изображения чтобы пользователь не нервничал

#  3. выход logout
#    - запрет возврата назад (см вк)

#  4. сделать кнопку преобразования в диком и сохранения где-нибудь. по сути - кнопку скачивания,
#  в которой преобразуется jpeg в диком

#  5. масштабирование изучить и сделать

# оператор не должен просматривать диагнозы, только персональные данные

