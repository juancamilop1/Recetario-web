from django.db import models


class Receta(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    ingredientes = models.TextField()
    preparacion = models.TextField()

    def __str__(self):
        return self.nombre


class Opcion(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    opcion_texto = models.CharField(max_length=200)
    votos = models.IntegerField(default=0)

    def __str__(self):
        return self.opcion_texto
