from django.db import models
from django_lifecycle import LifecycleModelMixin
from django.utils import timezone

class Base_content(LifecycleModelMixin,models.Model):
    status_choice = (
        (True,"Active"),
        (False,"Pending")
    )
    created_on = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True,choices=status_choice,blank=True)
    
    class Meta:
        abstract = True
