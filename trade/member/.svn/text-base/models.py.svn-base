
from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, unique= True)
    profile = models.ForeignKey("UserProfile", unique=True, related_name="member_list")
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=200)
    accept_terms = models.BooleanField(default=False)
    create_time = models.DateTimeField("created on", auto_now_add=True)
    update_time = models.DateTimeField("last updated on", auto_now=True)

    def __unicode__(self):
        return u"%s (%s)" % (self.user.username, self.email)


GENDER_OPTIONS = (("F", "Femenino"),("M", "Masculino"))

class UserProfile(models.Model):
    province = models.CharField("Provincia", max_length=100, null=True)
    city = models.CharField("Ciudad", max_length=100, null=True)
    address = models.CharField("Direccion", max_length=100, null=True)
    postal_code = models.CharField("Codigo Postal", max_length=100, null=True)
    telephone = models.CharField("Telefono", max_length=100, null=True)
    cell_phone = models.CharField("Celular", max_length=100, null=True)
    #age = models.IntegerField("Edad", default= 0)
    #birth_date = models.DateTimeField("Fecha de Nacimiento", null=True, blank=True)
    #gender = models.CharField("Sexo", choices = GENDER_OPTIONS, max_length=10, null=True)
