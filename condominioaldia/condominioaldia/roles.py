from rolepermissions.roles import AbstractUserRole
#https://django-role-permissions.readthedocs.io/en/stable/index.html

class Condo(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }

class Resident(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }


class Renter(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }

class AppAdmin(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }