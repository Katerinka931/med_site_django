from django.contrib import admin
from MedApp.models import User, Photo, Patient


class PhotoInstanceInline(admin.TabularInline):
    model = Photo


class PatientInstanceInline(admin.TabularInline):
    model = Patient


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'display_role', 'email', 'phone')
    list_filter = ('role',)

    fieldsets = (
        ('Personal data', {
            'fields': ('last_name', 'first_name', 'middle_name', 'role',)
        }),
        ('Contacts', {
            'fields': ('email', 'phone')
        }),
        ('Program`s dates', {'fields': (('date_joined', 'last_login'),)}),
        ('User`s status', {'fields': ('is_superuser', 'is_active', 'is_staff')}),
        ('Authentication', {'fields': ('username', 'password',)})
    )
    inlines = [PatientInstanceInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'email', 'phone', 'display_doctor')
    fieldsets = (
        ('Personal data', {
            'fields': ('last_name', 'first_name', 'middle_name', 'date_of_birth')
        }),
        ('Contacts', {
            'fields': ('email', 'phone')
        }),
        ('Attending doctor', {'fields': ('doctor_number',)}),
    )
    inlines = [PhotoInstanceInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('photo', 'actual', 'date_of_creation', 'diagnosis', 'display_patient', 'date_of_research')
    list_filter = ('actual', 'date_of_creation', 'date_of_research')
    fields = ['photo', 'diagnosis', 'actual', 'date_of_creation', 'patient_number', 'date_of_research']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
