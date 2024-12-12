from django.db import models

from core.models.models_base import BaseModel


class StoredFile(BaseModel):
    """
    Models to store uploaded files.
    Fields:
        filename: File name.
        upload_date: Upload date/time.
    """
    filename = models.CharField(max_length=255, unique=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
