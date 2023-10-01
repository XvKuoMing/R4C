from django.db import models
from .utils import re_validator


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=False, null=False)
    model = models.CharField(max_length=2, blank=False, null=False, validators=[re_validator('model')])
    version = models.CharField(max_length=2, blank=False, null=False, validators=[re_validator('version')])
    created = models.DateTimeField(blank=False, null=False)
