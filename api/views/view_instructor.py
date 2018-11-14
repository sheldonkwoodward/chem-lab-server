from django.contrib.auth.models import ContentType, Group, Permission
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.status import HTTP_201_CREATED

from api import models, serializers
from api.authentication import TokenAuthentication
from api.models import Instructor


class InstructorLCView(ListCreateAPIView):
    """
    The list create view for instructors.
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (DjangoModelPermissions,)
    lookup_field = 'pk'
    serializer_class = serializers.InstructorSerializer

    def get_queryset(self):
        return Instructor.objects.all()

    def list(self, request, *args, **kwargs):
        response = super(InstructorLCView, self).list(request, *args, **kwargs)
        response.data = {
            'instructors': response.data,
        }
        return response

    def create(self, request, *args, **kwargs):
        response = super(InstructorLCView, self).create(request, *args, **kwargs)
        # create the instructor group if it does not exist
        group, created = Group.objects.get_or_create(name='Instructor')
        # do not modify permissions if the request fails
        if response.status_code is not HTTP_201_CREATED:
            return response
        if created:
            # get permissions for all instructor models
            content_types = [
                ContentType.objects.get_for_model(models.Course),
                ContentType.objects.get_for_model(models.LabGroup),
                ContentType.objects.get_for_model(models.Student),
                ContentType.objects.get_for_model(models.Assignment),
                ContentType.objects.get_for_model(models.Assignment),
                ContentType.objects.get_for_model(models.AssignmentTemplate),
                ContentType.objects.get_for_model(models.TaskTemplate)
            ]
            for ct in content_types:
                permissions = Permission.objects.filter(content_type=ct).all()
                for p in permissions:
                    group.permissions.add(p)
        # add new instructor to the instructor group
        group.user_set.add(request.data['user'])
        return response


class InstructorRUDView(RetrieveUpdateDestroyAPIView):
    """
    The retrieve update destroy view for instructors.
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permissions_classes = (DjangoModelPermissions,)
    lookup_field = 'pk'
    serializer_class = serializers.InstructorSerializer

    def get_queryset(self):
        return Instructor.objects.all()
