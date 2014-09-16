from django.db import models

# Create your models here.
class Review(models.Model):
    """
    A review of a location
    """
    text = models.CharField(max_length=5000)
    grade = models.IntegerField(null=True)


class Property(models.Model):
    """
    A physical location belonging to a Customer organization, stores its reviews
    """
    #  Instance fields
    name = models.CharField(max_length=100)
    reviews = models.ManyToManyField(Review, null=True)

