import os
import re

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from core.models import StoredFile
from core.scripts_runner import run_script, parse_line_to_dict
from core.serializers import StoredFileSerializer, UserDataSerializer


class UploadFileViewSet(viewsets.ViewSet):
    """
    ViewSet for uploading files.
    """
    @swagger_auto_schema(
        operation_summary="Upload (or replace) a file",
        manual_parameters=[
            openapi.Parameter('filename', openapi.IN_QUERY, description="Name of the file to send", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            201: "File created",
            204: "File replaced",
            400: "Invalid filename or missing filename param"
        }
    )
    @action(detail=False, methods=['put'], url_path='upload-file')
    def upload_file(self, request):
        """        
        Upload or replace a file.
        File name passed via query param 'filename'.
        """
        filename = request.query_params.get('filename', None)
        if not filename:
            return Response({"detail": "filename query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^[A-Za-z0-9._-]+$', filename):
            return Response({"detail": "Invalid filename. Allowed chars: A-Z, a-z, 0-9, -, _, ."},
                            status=status.HTTP_400_BAD_REQUEST)

        file_content = request.body
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        file_exists = os.path.exists(file_path)

        with open(file_path, 'wb') as f:
            f.write(file_content)

        if not file_exists:
            StoredFile.objects.create(filename=filename)
            return Response({"detail": "File created"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "File replaced"}, status=status.HTTP_204_NO_CONTENT)


class ListFilesViewSet(viewsets.ViewSet):
    """
    ViewSet to list stored files.
    """
    @swagger_auto_schema(
        operation_summary="List stored files",
        responses={200: StoredFileSerializer(many=True)}
    )
    def list(self, request):
        """
        Returns the list of stored files.
        """
        files = StoredFile.objects.alive().order_by('filename')
        serializer = StoredFileSerializer(files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MaxMinSizeViewSet(viewsets.ViewSet):
    """
    ViewSet to get user with larger or smaller size.
    """
    @swagger_auto_schema(
        operation_summary="Get user with largest/smallest size",
        manual_parameters=[
            openapi.Parameter('filename', openapi.IN_QUERY, description="Name of the stored file to process", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('min', openapi.IN_QUERY, description="Defines whether to get the smallest size (any value)", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: UserDataSerializer()}
    )
    def list(self, request):
        """
        Returns the user record with largest size, or smallest size if 'min' parameter is provided.
        """
        filename = request.query_params.get('filename', None)
        min_param = request.query_params.get('min', None)

        if not filename:
            return Response({"detail": "filename query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return Response({"detail": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        args = [file_path]
        if min_param is not None:
            args.append('-min')

        output, error = run_script('max-min-size.sh', args)
        if error or not output:
            return Response({"detail": "Error running script"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = parse_line_to_dict(output)
        return Response(data, status=status.HTTP_200_OK)


class OrderByUsernameViewSet(viewsets.ViewSet):
    """
    ViewSet to get the list of users ordered by username.
    """
    @swagger_auto_schema(
        operation_summary="Get list of users ordered by username",
        manual_parameters=[
            openapi.Parameter('filename', openapi.IN_QUERY, description="Name of the stored file to process", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('desc', openapi.IN_QUERY, description="Sort descending (any value)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('username', openapi.IN_QUERY, description="Filter by substring in username", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: UserDataSerializer(many=True)}
    )
    def list(self, request):
        """
        Returns the list of users ordered by username (asc or desc),
        with option to filter by username.
        """
        filename = request.query_params.get('filename', None)
        desc = request.query_params.get('desc', None)
        filter_username = request.query_params.get('username', None)

        if not filename:
            return Response({"detail": "filename query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return Response({"detail": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        args = [file_path]
        if desc is not None:
            args.append('-desc')

        output, error = run_script('order-by-username.sh', args)
        if error or not output:
            return Response({"detail": "Error running script"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        lines = output.split('\n')
        data_list = [parse_line_to_dict(line) for line in lines if line.strip()]

        if filter_username:
            data_list = [d for d in data_list if filter_username in d['username']]

        return Response(data_list, status=status.HTTP_200_OK)


class BetweenMsgsViewSet(viewsets.ViewSet):
    """
    ViewSet to obtain list of users among a range of message quantity.
    """
    @swagger_auto_schema(
        operation_summary="Get users with number of messages between range",
        manual_parameters=[
            openapi.Parameter('filename', openapi.IN_QUERY, description="Name of the stored file to process", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('low', openapi.IN_QUERY, description="Lower limit", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('high', openapi.IN_QUERY, description="Upper limit", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('username', openapi.IN_QUERY, description="Filter by substring in username", type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: UserDataSerializer(many=True)}
    )
    def list(self, request):
        """
        Returns the list of users whose number of messages (INBOX) is between 'low' and 'high'.
        You can filter by username substring.
        """
        filename = request.query_params.get('filename', None)
        low = request.query_params.get('low', None)
        high = request.query_params.get('high', None)
        filter_username = request.query_params.get('username', None)

        if not filename or low is None or high is None:
            return Response({"detail": "filename, low and high query params are required"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            low_val = int(low)
            high_val = int(high)
        except ValueError:
            return Response({"detail": "low and high must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            return Response({"detail": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        args = [file_path, str(low_val), str(high_val)]
        output, error = run_script('between-msgs.sh', args)
        if error:
            return Response({"detail": "Error running script"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not output.strip():
            return Response([], status=status.HTTP_200_OK)

        lines = output.strip().split('\n')
        data_list = [parse_line_to_dict(line) for line in lines if line.strip()]

        if filter_username:
            data_list = [d for d in data_list if filter_username in d['username']]

        return Response(data_list, status=status.HTTP_200_OK)