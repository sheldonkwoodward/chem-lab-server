from django.contrib.auth.models import Permission, User
from django.conf import settings
from rest_framework import status
from api import permissions
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
import json
from pytz import timezone
from api.models import Course, Instructor, LabGroup, Assignment, AssignmentTemplate, TaskTemplate, AssignmentEntry, Student, TaskEntry

class TaskEntryLCTest(APITestCase):
    """
    Test cases for list and create requests on AssignmentLCView.
    """
    def setUp(self):
        self.instructor_username = 'instructor'
        self.student_username = 'student'
        self.password = 'test'
        self.instructor_user = User.objects.create_user(username=self.instructor_username, password=self.password)
        self.student_user = User.objects.create_user(username=self.student_username, password=self.password)
        self.instructor_user.groups.add(permissions.get_or_create_instructor_permissions())
        self.student_user.groups.add(permissions.get_or_create_student_permissions())
        self.client.login(username=self.student_username, password=self.password)
        # populate test database
        self.instructor = Instructor(user=self.instructor_user, wwuid='9994141')
        self.instructor.save()
        self.course = Course(name='Bounty Hunting 101')
        self.course.save()
        self.lab_group = LabGroup(course=self.course, instructor=self.instructor, term='before', enroll_key='4')
        self.lab_group.save()
        self.template = AssignmentTemplate(course=self.course, name='Royalty Kidnapping Section A')
        self.template.save()
        self.assignment = Assignment(assignment_template=self.template,
                                     labgroup=self.lab_group,
                                     open_date=datetime.now(timezone(settings.TIME_ZONE)),
                                     close_date=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=1))
        self.assignment.save()
        self.task_template = TaskTemplate(assignment_template=self.template,
                                          name='test name 1',
                                          description='test summary 1',
                                          image_urls='test image 1',
                                          points=23,
                                          attempts_allowed=3,
                                          text_input='test input',
                                          numeric_input='23',
                                          multiple_choice='text',
                                          numeric_accuracy=2)
        self.task_template.save()
        self.student = Student(user=self.student_user, labgroup=self.lab_group, wwuid='12345')
        self.student.save()
        self.assignment_entry = AssignmentEntry(student=self.student, assignment=self.assignment)
        self.assignment_entry.save()
        # retrieve the view
        self.view_name = 'api:task-entry-lc'

    def test_task_entry_create(self):
        """
        Tests that a task entry is properly created.
        """
        # request
        request_body = {
            'task_template': self.task_template.id,
            'assignment_entry': self.assignment_entry.id,
            'attempts': 2,
            'passed': True,
        }
        task_entry = TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=2,
                               passed=True)
        task_entry.save()
        task_one = TaskEntry.objects.first()
        response = self.client.post(reverse(self.view_name, args=[self.task_template.id]), request_body)
        response_body = json.loads(response.content.decode('utf-8'))
        # test database
        self.assertEqual(task_one.assignment_entry.id, request_body['assignment_entry'])
        self.assertEqual(task_one.task_template.id, request_body['task_template'])
        self.assertEqual(task_one.attempts, request_body['attempts'])
        self.assertEqual(task_one.passed, request_body['passed'])
        # test response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_body['task_template'], request_body['task_template'])
        self.assertEqual(response_body['assignment_entry'], request_body['assignment_entry'])
        self.assertEqual(response_body['attempts'], request_body['attempts'])
        self.assertEqual(response_body['passed'], request_body['passed'])

    def test_task_entry_list(self):
        """
        Tests that Task Entries are properly listed.
        """
        # add assignments to database
        TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=3, passed=True).save()
        TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=4, passed=True).save()
        # request
        response = self.client.get(reverse(self.view_name, args=[self.task_template.id]))
        response_body = json.loads(response.content.decode('utf-8'))
        # test response
        task_entries = TaskEntry.objects.all()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_body['task_entry'][0]['pk'], task_entries[0].id)
        self.assertEqual(response_body['task_entry'][0]['task_template'], task_entries[0].task_template.id)
        self.assertEqual(response_body['task_entry'][0]['assignment_entry'], task_entries[0].assignment_entry.id)
        self.assertEqual(response_body['task_entry'][0]['attempts'], task_entries[0].attempts)
        self.assertEqual(response_body['task_entry'][0]['passed'], task_entries[0].passed)

class TaskEntryRUDTest(APITestCase):
    """
    Test cases for retrieve, update, and destroy requests on CourseRUDView.
    """
    def setUp(self):
        self.instructor_username = 'instructor'
        self.student_username = 'student'
        self.password = 'test'
        self.instructor_user = User.objects.create_user(username=self.instructor_username, password=self.password)
        self.student_user = User.objects.create_user(username=self.student_username, password=self.password)
        self.instructor_user.groups.add(permissions.get_or_create_instructor_permissions())
        self.student_user.groups.add(permissions.get_or_create_student_permissions())
        self.client.login(username=self.student_username, password=self.password)
        # populate test database
        self.instructor = Instructor(user=self.instructor_user, wwuid='9994141')
        self.instructor.save()
        self.course = Course(name='Bounty Hunting 101')
        self.course.save()
        self.lab_group = LabGroup(course=self.course, instructor=self.instructor, term='before', enroll_key='4')
        self.lab_group.save()
        self.template = AssignmentTemplate(course=self.course, name='Royalty Kidnapping Section A')
        self.template.save()
        self.assignment = Assignment(assignment_template=self.template,
                                     labgroup=self.lab_group,
                                     open_date=datetime.now(timezone(settings.TIME_ZONE)),
                                     close_date=datetime.now(timezone(settings.TIME_ZONE)) + timedelta(days=1))
        self.assignment.save()
        self.task_template = TaskTemplate(assignment_template=self.template,
                                          name='test name 1',
                                          description='test summary 1',
                                          image_urls='test image 1',
                                          points=23,
                                          attempts_allowed=3,
                                          text_input='test input',
                                          numeric_input='23',
                                          multiple_choice='text',
                                          numeric_accuracy=2)
        self.task_template.save()
        self.task_template_2 = TaskTemplate(assignment_template=self.template,
                                            name='test name 1',
                                            description='test summary 1',
                                            image_urls='test image 1',
                                            points=23,
                                            attempts_allowed=3,
                                            text_input='test input',
                                            numeric_input='23',
                                            multiple_choice='text',
                                            numeric_accuracy=2)
        self.task_template_2.save()
        self.student = Student(user=self.student_user, labgroup=self.lab_group, wwuid='12345')
        self.student.save()
        self.assignment_entry = AssignmentEntry(student=self.student, assignment=self.assignment)
        self.assignment_entry.save()
        self.assignment_entry_2 = AssignmentEntry(student=self.student, assignment=self.assignment)
        self.assignment_entry_2.save()
        # add tasks to the database
        self.task_1 = TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=1, passed=True)
        self.task_1.save()
        self.task_2 = TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=2, passed=True)
        self.task_2.save()
        self.task_3 = TaskEntry(assignment_entry=self.assignment_entry, task_template=self.task_template, attempts=3, passed=True)
        self.task_3.save()
        # retrieve the view
        self.view_name = 'api:task-entry-rud'

    def test_task_entry_retrieve(self):
        """
        Tests that a task entry is properly retrieved.
        """
        # request
        response = self.client.get(reverse(self.view_name, args=[self.task_1.id, self.task_2.id]))
        response_body = json.loads(response.content.decode('utf-8'))
        # test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_body['pk'], self.task_1.id)
        self.assertEqual(response_body['assignment_entry'], self.task_1.assignment_entry.id)
        self.assertEqual(response_body['task_template'], self.task_1.task_template.id)
        self.assertEqual(response_body['attempts'], self.task_1.attempts)
        self.assertEqual(response_body['passed'], self.task_1.passed)

    def test_task_entry_update(self):
        """
        Tests that a task entry is properly updated.
        """
        # modify values
        request_body = {
            'task_template': self.task_template_2.id,
            'assignment_entry': self.assignment_entry_2.id,
            'attempts': 10,
            'passed': False,
        }
        # request
        response = self.client.put(reverse(self.view_name, args=[self.task_2.id, self.task_2.id]), request_body)
        response_body = json.loads(response.content.decode('utf-8'))
        # test database
        task_change = TaskEntry.objects.get(id=self.task_2.id)
        self.assertEqual(task_change.id, self.task_2.id)
        self.assertEqual(task_change.task_template.id, request_body['task_template'])
        self.assertEqual(task_change.assignment_entry.id, request_body['assignment_entry'])
        self.assertEqual(task_change.attempts, request_body['attempts'])
        self.assertEqual(task_change.passed, request_body['passed'])
        # test response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_body['pk'], self.task_2.id)
        self.assertEqual(response_body['assignment_entry'], request_body['task_template'])
        self.assertEqual(response_body['task_template'], request_body['assignment_entry'])
        self.assertEqual(response_body['attempts'], request_body['attempts'])
        self.assertEqual(response_body['passed'], request_body['passed'])

    def test_task_entry_destroy(self):
        """
        Tests that a task entry is properly destroyed.
        """
        # request
        response = self.client.delete(reverse(self.view_name, args=[self.task_2.id, self.task_2.id]))
        # test database
        task_entries = TaskEntry.objects.all()
        self.assertTrue(self.task_1 in task_entries)
        self.assertTrue(self.task_2 not in task_entries)
        self.assertTrue(self.task_3 in task_entries)
        # test response
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
























