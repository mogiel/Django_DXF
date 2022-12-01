from django.db import models

# Create your models here.


class concreteStrengthClass(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    fck = models.IntegerField(max_length=3)
    fck_cube = models.IntegerField(max_length=3)
    fcm = models.IntegerField(max_length=3)
    fctm = models.FloatField(max_length=3)
    fctk0_05 = models.FloatField(max_length=3)
    fctk0_95 = models.FloatField(max_length=3)
    Ectm = models.IntegerField(max_length=2)
    ec1 = models.FloatField(max_length=3)
    ecu1 = models.FloatField(max_length=3)
    ec2 = models.FloatField(max_length=3)
    ecu2 = models.FloatField(max_length=3)
    n = models.FloatField(max_length=3)
    ec3 = models.FloatField(max_length=3)
    ecu3 = models.FloatField(max_length=3)

    class Meta:
        db_table = "concrete_strength_class"
