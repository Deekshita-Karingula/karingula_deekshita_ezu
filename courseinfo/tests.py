from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from .forms import InstructorForm, StudentForm, SemesterForm, CourseForm, SectionForm
from .models import Period, Year, Semester, Course, Instructor, Student, Section, Registration
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.test import Client
from .views import StudentDelete, InstructorDelete, StudentList


# MODEL TESTING
class YearOrderingTest(TestCase):
    def test_year_ordering(self):
        # Create years
        Year.objects.bulk_create([
            Year(year=2023),
            Year(year=2021),
            Year(year=2022)
        ])
        ordered_years = Year.objects.all().order_by('year')
        self.assertEqual(list(ordered_years.values_list('year', flat=True)), [2021, 2022, 2023])


class Period_Ordering_Test(TestCase):
    def test_ordering(self):
        Period.objects.bulk_create([
            Period(period_sequence=4, period_name='Winter'),
            Period(period_sequence=1, period_name='Spring'),
            Period(period_sequence=2, period_name='Summer'),
            Period(period_sequence=3, period_name='Fall'),
        ])
        ordered_periods = Period.objects.all().order_by('period_sequence')
        self.assertEqual(list(ordered_periods.values_list('period_name', flat=True)),
                         ['Spring', 'Summer', 'Fall', 'Winter'])


class InstructorUniquenessTest(TestCase):
    def test_uniqueness(self):
        Instructor.objects.create(first_name='Swiftwind', last_name='Hoson')
        with self.assertRaises(IntegrityError):
            Instructor.objects.create(first_name='Swiftwind', last_name='Hoson')


class StudentUniquenessTest(TestCase):
    def test_uniqueness(self):
        Student.objects.create(first_name='Bluesky', last_name='Fly')
        with self.assertRaises(IntegrityError):
            Student.objects.create(first_name='Bluesky', last_name='Fly')


class CourseUniquenessTest(TestCase):
    def test_uniqueness(self):
        Course.objects.create(course_number='IS452', course_name='Database Designing')
        with self.assertRaises(IntegrityError):
            Course.objects.create(course_number='IS452', course_name='Database Designing')


class SemesterUniquenessTest(TestCase):
    def test_uniqueness(self):
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        Semester.objects.create(year=year_2023, period=spring_period)
        with self.assertRaises(IntegrityError):
            Semester.objects.create(year=year_2023, period=spring_period)


class SectionUniquenessTest(TestCase):
    def test_uniqueness(self):
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        instructor = Instructor.objects.create(first_name='John', last_name='Doe')
        Section.objects.create(section_name='Section A', semester=semester, course=course, instructor=instructor)
        with self.assertRaises(IntegrityError):
            Section.objects.create(section_name='Section A', semester=semester, course=course, instructor=instructor)


class RegistrationUniquenessTest(TestCase):
    def test_uniqueness(self):
        student = Student.objects.create(first_name='John', last_name='Doe')
        instructor = Instructor.objects.create(first_name='Jane', last_name='Smith')
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        year_2023, _ = Year.objects.get_or_create(year=2023)
        spring_period, _ = Period.objects.get_or_create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        section = Section.objects.create(section_name='Section A', course=course, instructor=instructor,
                                         semester=semester)
        Registration.objects.create(section=section, student=student)
        with self.assertRaises(IntegrityError):
            Registration.objects.create(section=section, student=student)


# VIEW TESTING
class EmptyTemplateTests(TestCase):
    # Test response with no registrations
    def test_registration_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_registration_list_urlpattern'))
        self.assertEqual(response.status_code, 302)

    # Test response with no sections
    def test_section_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_section_list_urlpattern'))
        self.assertEqual(response.status_code, 302)

    def test_semester_list_view_empty(self):
        response = self.client.get(reverse('courseinfo_semester_list_urlpattern'))
        self.assertEqual(response.status_code, 302)


# TEMPLATE TESTING
class PopulatedTemplateTests(TestCase):
    # Initialize to avoid "unresolved attribute reference" error
    year, period, semester, course, instructor, student, section = None, None, None, None, None, None, None
    # Populate our database for these template tests
    @classmethod
    def setUpTestData(cls):
        cls.instructor = Instructor.objects.create(first_name="Henry", last_name="Gerard", disambiguator="Harvard")
        cls.student = Student.objects.create(first_name="Harvey", last_name="Specter", disambiguator="New York")
        cls.year = Year.objects.create(year=2024)
        cls.period = Period.objects.create(period_sequence=1, period_name="Spring")
        cls.semester = Semester.objects.create(year=cls.year, period=cls.period)
        cls.course = Course.objects.create(course_number="IS439",
                                           course_name="Web Development Using Application Frameworks")
        cls.section = Section.objects.create(section_name="AOG/AOU",
                                             semester=cls.semester,
                                             course=cls.course,
                                             instructor=cls.instructor)
        cls.registration = Registration.objects.create(student=cls.student,
                                                       section=cls.section)


# URL TESTING
class TestURLs(TestCase):
    # Tests for Instructor

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_instructor_detail_url(self):
        # Assuming 'instructor_detail_url' is the URL name for the view being tested
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    # Test the instructor detail page with an invalid instructor PK
    def test_instructor_detail_invalid_pk(self):
        invalid_pk = 999
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern', kwargs={'pk': invalid_pk}))
        self.assertEqual(response.status_code, 403)

    # Test the instructor detail page when there are no sections
    def test_instructor_detail_no_sections(self):
        instructor = Instructor.objects.create(first_name='John', last_name='Doe')
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern', kwargs={'pk': instructor.pk}))
        self.assertEqual(response.status_code, 403)

    # Tests for section

    def test_section_detail_url(self):
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        instructor = Instructor.objects.create(first_name='John', last_name='Doe')
        section = Section.objects.create(section_name='Section A', course=course, instructor=instructor, semester=semester)
        response = self.client.get(reverse('courseinfo_section_detail_urlpattern', kwargs={'pk': section.pk}))

    # Test the instructor list page when there are no instructors
    def test_section_list_no_sections(self):
        response = self.client.get(reverse('courseinfo_section_list_urlpattern'))
        self.assertEqual(response.status_code, 403)

    # Test the instructor detail page with an invalid instructor PK
    def test_section_detail_invalid_pk(self):
        invalid_pk = 999
        response = self.client.get(reverse('courseinfo_section_detail_urlpattern', kwargs={'pk': invalid_pk}))
        self.assertEqual(response.status_code, 403)

    # Test the section detail page when there are no student registrations
    def test_section_detail_no_registrations(self):
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        instructor = Instructor.objects.create(first_name='John', last_name='Doe')
        section = Section.objects.create(section_name='Section A', course=course, instructor=instructor,
                                         semester=semester)
        response = self.client.get(reverse('courseinfo_section_detail_urlpattern', kwargs={'pk': section.pk}))

    # Tests for courses

    def test_course_detail_url(self):
        course = Course.objects.create(course_number='IS452', course_name='Database Designing')
        response = self.client.get(reverse('courseinfo_course_detail_urlpattern', kwargs={'pk': course.pk}))
        self.assertEqual(response.status_code, 403)

    # Test the course detail page with an invalid course PK
    def test_course_detail_invalid_pk(self):
        invalid_pk = 999
        response = self.client.get(reverse('courseinfo_course_detail_urlpattern', kwargs={'pk': invalid_pk}))
        self.assertEqual(response.status_code, 403)

    # Tests for semester

    def test_semester_detail_url(self):
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        response = self.client.get(reverse('courseinfo_semester_detail_urlpattern', kwargs={'pk': semester.pk}))
        self.assertEqual(response.status_code, 403)

    # Test the course detail page with an invalid course PK
    def test_semester_detail_invalid_pk(self):
        invalid_pk = 999
        response = self.client.get(reverse('courseinfo_semester_detail_urlpattern', kwargs={'pk': invalid_pk}))
        self.assertEqual(response.status_code, 403)

    def test_semester_detail_no_sections(self):
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        response = self.client.get(reverse('courseinfo_semester_detail_urlpattern', kwargs={'pk': semester.pk}))
        self.assertEqual(response.status_code, 403)

    # Tests for student

    def test_student_detail_url(self):
        student = Student.objects.create(first_name='Bluesky', last_name='Fly')
        response = self.client.get(reverse('courseinfo_student_detail_urlpattern', kwargs={'pk': student.pk}))
        self.assertEqual(response.status_code, 403)

    # Test the course detail page with an invalid course PK
    def test_student_detail_invalid_pk(self):
        invalid_pk = 999
        response = self.client.get(reverse('courseinfo_student_detail_urlpattern', kwargs={'pk': invalid_pk}))
        self.assertEqual(response.status_code, 403)


# FORM TESTING
class TestInstructorTemplates(TestCase):
    def setUp(self):
        # Creating required related objects
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        instructor = Instructor.objects.create(first_name="John", last_name="Doe")

        # Creating Section instance
        self.section1 = Section.objects.create(
            section_name="Section 1",
            semester=semester,
            course=course,
            instructor=instructor
        )

    def test_instructor_refuse_delete_template(self):
        response = self.client.get(reverse('courseinfo_instructor_delete_urlpattern', args=[self.section1.instructor.pk]))
        self.assertTemplateUsed(response, 'courseinfo/base.html')
        self.assertContains(response, 'Error Deleting Instructor')
        self.assertContains(response, f'You may not delete instructor {self.section1.instructor}.')
        self.assertContains(response, f'<a href="{self.section1.get_absolute_url()}">{self.section1}</a>')
        self.assertContains(response, reverse('courseinfo_instructor_list_urlpattern'))


class TestSectionTemplates(TestCase):
    def setUp(self):
        # Creating required related objects
        year_2023 = Year.objects.create(year=2023)
        spring_period = Period.objects.create(period_sequence=1, period_name='Spring')
        semester = Semester.objects.create(year=year_2023, period=spring_period)
        course = Course.objects.create(course_number='CS101', course_name='Introduction to Computer Science')
        instructor = Instructor.objects.create(first_name="John", last_name="Doe")

        # Creating Section instance
        self.section1 = Section.objects.create(
            section_name="Section 1",
            semester=semester,
            course=course,
            instructor=instructor
        )

        # Creating related registrations
        student1 = Student.objects.create(first_name="Alice", last_name="Smith")
        student2 = Student.objects.create(first_name="Bob", last_name="Jones")

        self.registration1 = Registration.objects.create(
            student=student1,
            section=self.section1
        )

        self.registration2 = Registration.objects.create(
            student=student2,
            section=self.section1
        )

    def test_section_refuse_delete_template(self):
        response = self.client.get(reverse('courseinfo_section_delete_urlpattern', args=[self.section1.pk]))
        self.assertTemplateUsed(response, 'courseinfo/base.html')
        self.assertContains(response, 'Error Deleting Section')
        self.assertContains(response, f'You may not delete section {self.section1}.')
        self.assertContains(response, f'<a href="{self.registration1.get_absolute_url()}">{self.registration1}</a>')
        self.assertContains(response, f'<a href="{self.registration2.get_absolute_url()}">{self.registration2}</a>')
        self.assertContains(response, reverse('courseinfo_section_list_urlpattern'))


# Test cases for Pagination Assignment

class InstructorFormTest(TestCase):
    def test_clean_first_name(self):
        form_data = {'first_name': ' Kevin ', 'last_name': 'Trainor', 'disambiguator': ''}
        form = InstructorForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'Kevin')

    def test_clean_last_name(self):
        form_data = {'first_name': ' Kevin ', 'last_name': 'Trainor', 'disambiguator': ''}
        form = InstructorForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['last_name'], 'Trainor')


class StudentFormTest(TestCase):
    def test_clean_student_first_name(self):
        form_data = {'first_name': ' John ', 'last_name': 'Doe', 'disambiguator': '001'}
        form = StudentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'John')

    def test_clean_last_name(self):
        form_data = {'first_name': ' John ', 'last_name': ' Doe ', 'disambiguator': '002'}
        form = StudentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['last_name'], 'Doe')


class SemesterFormTest(TestCase):
    def setUp(self):
        self.year = Year.objects.create(year=2023)
        self.period = Period.objects.create(period_sequence=1, period_name='Spring')

    def test_semester_form_valid(self):
        form_data = {
            'year': self.year.pk,
            'period': self.period.pk,
        }
        form = SemesterForm(data=form_data)

        # Assert that the form is valid, save the data and check if instances exists
        self.assertTrue(form.is_valid())
        semester_instance = form.save()
        self.assertIsNotNone(semester_instance)
        self.assertEqual(semester_instance.period, self.period)


class CourseFormTest(TestCase):
    def test_clean_course_number(self):
        form_data = {'course_number': ' IS460 ', 'course_name': 'Web Application Development'}
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['course_number'], 'IS460')

    def test_clean_course_name(self):
        form_data = {'course_number': ' IS460 ', 'course_name': 'Web Application Development'}
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['course_name'], 'Web Application Development')


class SectionFormTest(TestCase):
    def setUp(self):
        self.year = Year.objects.create(year=2023)
        self.period = Period.objects.create(period_sequence=1, period_name='Spring')
        self.semester = Semester.objects.create(year=self.year, period=self.period)
        self.course = Course.objects.create(course_number='C101', course_name='Introduction to Programming')
        self.instructor = Instructor.objects.create(first_name='John', last_name='Doe')

    def test_clean_section_name(self):
        form_data = {
            'section_name': 'Test_Name',
            'semester': self.semester.pk,
            'course': self.course.pk,
            'instructor': self.instructor.pk
        }

        form = SectionForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['section_name'], 'Test_Name')


# Tests for "Coding Assignment: Generic Class-Based Views"

class StudentPaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 50 instructor objects
        for i in range(50):
            Student.objects.create(first_name=f"First {i + 1}", last_name=f"Last {i + 1}")

    def test_pagination(self):
        client = Client()

        # Make a request to the instructor list view
        response = client.get(reverse('courseinfo_student_list_urlpattern'))
        self.assertEqual(response.status_code, 302)


class InstructorPaginationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 50 instructor objects
        for i in range(50):
            Instructor.objects.create(first_name=f"First {i + 1}", last_name=f"Last {i + 1}")

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_pagination(self):
        # Make a request to the instructor list view
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 403)

# test for Authentication and Authorization assignment - 04/14/2024


class InstructorListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.permission = Permission.objects.get(name='Can view instructor')

    def test_authenticated_user_can_access_list_view(self):
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_has_permission_to_access_list_view(self):
        self.user.user_permissions.add(self.permission)
        response = self.client.get(reverse('courseinfo_instructor_list_urlpattern'))
        self.assertEqual(response.status_code, 200)


class InstructorDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        self.instructor = Instructor.objects.create(first_name='John', last_name='Doe')

    def test_authenticated_user_can_access_detail_view(self):
        response = self.client.get(reverse('courseinfo_instructor_detail_urlpattern', kwargs={'pk': self.instructor.pk}))
        self.assertEqual(response.status_code, 403)


class AuthenticationAuthorizationTestCase(TestCase):
    def setUp(self):
        # Create a test user with specific roles
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin_user = User.objects.create_user(username='adminuser', password='admin123')
        self.admin_user.is_staff = True
        self.admin_user.save()

    def test_valid_login(self):
        # Test valid login credentials
        response = self.client.post(reverse('login_urlpattern'), {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)  # Redirects to homepage upon successful login
        self.assertTrue('_auth_user_id' in self.client.session)  # User is authenticated

    def test_invalid_login(self):
        # Test invalid login credentials
        response = self.client.post(reverse('login_urlpattern'), {'username': 'invaliduser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  # Login page is rendered again
        self.assertFalse('_auth_user_id' in self.client.session)  # User is not authenticated

    def test_authorized_access(self):
        # Test authorized access to restricted resource
        self.client.login(username='tester', password='{iSchoolUI}')
        response = self.client.get(reverse('login_urlpattern'))
        self.assertEqual(response.status_code, 200)  # Access granted for authenticated user

    def test_admin_access(self):
        # Test access for admin user
        self.client.login(username='adminuser', password='admin123')
        response = self.client.get(reverse('about_urlpattern'))
        self.assertEqual(response.status_code, 200)  # Access granted for admin user


