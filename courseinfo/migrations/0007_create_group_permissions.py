from __future__ import unicode_literals
from itertools import chain

from django.db import migrations


def populate_permissions_lists(apps):
    permission_class = apps.get_model('auth', 'Permission')

    instructor_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                             content_type__model='instructor')

    student_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                          content_type__model='student')

    period_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                                  content_type__model='period')

    year_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                                  content_type__model='year')

    semester_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                           content_type__model='semester')

    course_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                         content_type__model='course')

    section_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                          content_type__model='section')

    registration_permissions = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                               content_type__model='registration')

    perm_view_instructor = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                           content_type__model='instructor',
                                                           codename='view_instructor')

    perm_view_student = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                        content_type__model='student',
                                                        codename='view_student')

    perm_view_period = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                               content_type__model='period',
                                                               codename='view_period')

    perm_view_year = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                               content_type__model='year',
                                                               codename='view_year')

    perm_view_semester = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                         content_type__model='semester',
                                                         codename='view_semester')

    perm_view_course = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                       content_type__model='course',
                                                       codename='view_course')

    perm_view_section = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                        content_type__model='section',
                                                        codename='view_section')

    perm_view_registration = permission_class.objects.filter(content_type__app_label='courseinfo',
                                                             content_type__model='registration',
                                                             codename='view_registration')

    ci_user_permissions = chain(perm_view_instructor,
                                perm_view_period,
                                perm_view_year,
                                perm_view_student,
                                perm_view_semester,
                                perm_view_course,
                                perm_view_section,
                                perm_view_registration)

    ci_scheduler_permissions = chain(instructor_permissions,
                                     period_permissions,
                                     year_permissions,
                                     semester_permissions,
                                     course_permissions,
                                     section_permissions,
                                     perm_view_student,
                                     perm_view_registration)

    ci_registrar_permissions = chain(student_permissions,
                                     registration_permissions,
                                     perm_view_instructor,
                                     perm_view_period,
                                     perm_view_year,
                                     perm_view_course,
                                     perm_view_semester,
                                     perm_view_section)

    my_groups_initialization_list = [
        {
            "name": "ci_user",
            "permissions_list": ci_user_permissions,
        },
        {
            "name": "ci_scheduler",
            "permissions_list": ci_scheduler_permissions,
        },
        {
            "name": "ci_registrar",
            "permissions_list": ci_registrar_permissions,
        },
    ]
    return my_groups_initialization_list


def add_group_permissions_data(apps, schema_editor):
    groups_initialization_list = populate_permissions_lists(apps)

    group_model_class = apps.get_model('auth', 'Group')
    for group in groups_initialization_list:
        if group['permissions_list'] is not None:
            group_object = group_model_class.objects.get(
                name=group['name']
            )
            group_object.permissions.set(group['permissions_list'])
            group_object.save()


def remove_group_permissions_data(apps, schema_editor):
    groups_initialization_list = populate_permissions_lists(apps)

    group_model_class = apps.get_model('auth', 'Group')
    for group in groups_initialization_list:
        if group['permissions_list'] is not None:
            group_object = group_model_class.objects.get(
                name=group['name']
            )
            list_of_permissions = group['permissions_list']
            for permission in list_of_permissions:
                group_object.permissions.remove(permission)
                group_object.save()


class Migration(migrations.Migration):
    dependencies = [
        ('courseinfo', '0006_create_groups'),
    ]

    operations = [
        migrations.RunPython(
            add_group_permissions_data,
            remove_group_permissions_data
        )
    ]
