from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import *
from MedApp.models import Doctor, Patient
from MedApp.dto import DoctorDTO, PatientDTO, DoctorWithPatientsDTO
from MedApp.neural_network import Neural_Network


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

    patients = get_patients(doctor)
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
            try:
                user.create_or_edit_doctor(lastname, firstname, middlename, email, phone, login)
                transfer_object = DoctorDTO(user)
                return JsonResponse({'message': 'Редактирование успешно', 'user': vars(transfer_object)},
                                    safe=False)
            except Exception:
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует', 'user': vars(transfer_object)},
                    safe=False)

    if request.method == 'GET':
        return JsonResponse({'user': vars(transfer_object)}, safe=False)


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def create_user(request):
    data = JSONParser().parse(request)
    doc = Doctor()

    if request.method == 'POST':
        last_name = data['last_name']
        first_name = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        login = data['login']
        password = data['password']
        password_repeat = data['password_repeat']

        if password_repeat == password:
            if Doctor.objects.filter(email=email):
                return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует'},
                                    status=status.HTTP_409_CONFLICT)
            else:
                try:
                    create_auth_user(login, email, password, first_name, last_name)
                    doc.create_or_edit_doctor(last_name, first_name, middle_name, email, phone, login)
                    return JsonResponse({'message': 'Пользователь успешно создан'}, status=status.HTTP_200_OK)
                except Exception:
                    return JsonResponse(
                        {'message': 'Пользователь с таким логином уже существует'},
                        status=status.HTTP_409_CONFLICT)
        else:
            return JsonResponse({'message': 'Пароли не совпадают'},
                                status=status.HTTP_403_FORBIDDEN)

    return JsonResponse({'message': ''}, safe=False)


# todo set here edit_user
# todo set here doctors_info
@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def create_patient(request):
    pk = request.user.id
    data = JSONParser().parse(request)
    patient = Patient()

    if request.method == 'POST':
        last_name = data['last_name']
        first_name = data['first_name']
        middle_name = data['middle_name']
        email = data['email']
        phone = data['phone']
        date_of_birth = data['date_of_birth']
        diagnosys = data['diagnosys']
        if Doctor.objects.get(pk=pk).role == 'DOCTOR':
            doctor_number = pk
        else:
            doctor_number = data['doctor_number']

        if Patient.objects.filter(email=email):
            return JsonResponse(
                {'message': 'Пациент с таким адресом электронной почты уже существует'}, safe=False)
        else:
            patient.create_patient(last_name, first_name, middle_name, email, phone, date_of_birth, doctor_number,
                                   diagnosys)
            return JsonResponse({'message': 'Пациент успешно создан'}, safe=False)


# todo set here edit_patient
# todo set here patients_info

# todo set here load_image


# ----------------------- new additional functions -----------------------#
def get_patients_list(patients_queryset):
    patients = list()
    for patient in patients_queryset:
        patients.append({'id': patient.pk, 'first_name': patient.first_name, 'last_name': patient.last_name,
                         'middle_name': patient.middle_name, 'date_of_birth': patient.date_of_birth,
                         'email': patient.email, 'phone': patient.phone, 'diagnosys': patient.diagnosys})
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
    if user_role == 'ADMIN' or user_role == 'CHIEF':
        people = get_doctors_list(Doctor.objects.all().exclude(pk=pk))
    else:
        people = get_patients_list(Patient.objects.filter(doctor_number_id=pk))
    return people


def get_patients(doctor):
    return get_patients_list(Patient.objects.all()) if doctor.role == 'OPERATOR' else get_patients_list(
        Patient.objects.filter(doctor_number=doctor.pk))


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


###################### old version ######################


@api_view(['GET', 'POST'])
def edit_user(request, usr):
    pk = request.user.id

    admin = Doctor.objects.get(id=pk)
    doctor = Doctor.objects.get(id=usr)

    if request.method == 'GET':
        return JsonResponse({'message': ''})

    if request.method == 'POST':
        lastname = request.POST.get('last_name')
        firstname = request.POST.get('first_name')
        middlename = request.POST.get('middle_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        login = request.POST.get('login')

        if Doctor.objects.filter(email=email).exclude(pk=doctor.pk):
            return JsonResponse({'message': 'Пользователь с таким адресом электронной почты уже существует'},
                                safe=False)
        else:
            try:
                doctor.create_or_edit_doctor(lastname, firstname, middlename, email, phone, login)
                return JsonResponse({'message': 'Редактирование успешно'},
                                    safe=False)
            except Exception:
                return JsonResponse(
                    {'message': 'Пользователь с таким логином уже существует'},
                    safe=False)


@api_view(['GET', 'POST'])
def edit_patient(request, pat):
    pk = request.user.id
    patient = Patient.objects.get(pk=pat)

    # if см create patient
    doctor = Doctor.objects.get(pk=pk)

    if request.method == 'POST':
        try:

            return  # save_patient(request, doctor, patient, None, transfer_object)
        except Exception:
            return JsonResponse(
                {'message': 'Невозможно редактировать несуществующего пациента'}, safe=False)


@api_view(['GET', 'DELETE'])
def doctors_info(request, doc):
    pk = request.user.id

    remove_id = request.GET.get("remove")
    admin = Doctor.objects.get(id=pk)
    doctor = Doctor.objects.get(pk=doc)

    if request.method == 'GET':
        patients = get_patients(doctor)
        doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)

        return JsonResponse(
            {'message': '', 'doctor': vars(doctor_transfer_object)}, safe=False)

    if request.method == 'DELETE':
        if remove_id != None:
            remove_person(remove_id, admin.role, 'pat')

            patients, doctors = get_patients(doctor)
            doctor_transfer_object = DoctorWithPatientsDTO(doctor, patients)
            return JsonResponse({'message': 'Удаление успешно', 'doctor': vars(doctor_transfer_object)}, safe=False)


@api_view(['GET', 'POST'])
def patients_info(request, pat):
    patient = Patient.objects.get(pk=pat)
    patients_doctor = Doctor.objects.get(pk=patient.doctor_number_id)
    patient_transfer = PatientDTO(patient, patients_doctor)

    if request.method == 'GET':
        return JsonResponse({'message': '', 'patient': vars(patient_transfer)}, safe=False)

    if request.method == 'POST':
        # изменить фото! как - понятия не имею. передавать в качестве параметра фото? путь к фото? что вообще ... помогите...
        return JsonResponse({'message': '', 'patient': vars(patient_transfer)}, safe=False)  # this delete maybe


@permission_classes([IsAuthenticated, ])
@api_view(['GET', 'POST'])
def load_image(request):
    processing = Neural_Network()
    result = None

    if request.method == 'POST':
        img = request.FILES['file']
        # todo возможно это как-то иначе переделать? чтобы не сохранялось? ну, пока так
        # сохраняем на файловой системе???
        fs = FileSystemStorage(location='D:/Desktop/django+angular/med_site_django/MedApp/temp_storage')
        filename = fs.save(img.name, img)  # здесь будет сохраняться диком?
        file_url = fs.path(filename)
        result = processing.predict_image(file_url)
        # result = processing.open_dicom(file_url, filename)
        fs.delete(filename)
        # acc = processing.get_statistic()

        return JsonResponse({'result': result})

    return JsonResponse({})


@api_view(['POST'])
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Вы вышли из системы'}, status=status.HTTP_200_OK)


# delete this additional function
def save_patient(request, doctor, patient, another_doctor_id, transfer_object):
    id = doctor.pk

    lastname = request.POST['last_name']
    firstname = request.POST['first_name']
    middlename = request.POST['middle_name']
    email = request.POST['email']
    phone = request.POST['phone']
    date_of_birth = request.POST['date_of_birth']
    diagnosys = request.POST.get('diagnosys')

    if Patient.objects.filter(email=email).exclude(pk=patient.pk):
        return JsonResponse(
            {'message': 'Пациент с таким адресом электронной почты уже существует', 'user': vars(transfer_object)},
            safe=False)
    else:
        if another_doctor_id != None:
            id = another_doctor_id

        patient.create_patient(lastname, firstname, middlename, email, phone, date_of_birth, id, diagnosys)
        return JsonResponse({'message': 'message'}, safe=False)
