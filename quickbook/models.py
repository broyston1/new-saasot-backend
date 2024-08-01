from django.db import models

class QuickBooksToken(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    realm_id = models.CharField(max_length=255, null=True)
    # Add any additional fields you need to store

class QuickBooksData(models.Model):
    # Define your QuickBooks data model fields here
    pass