from django.db import models

class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    nome_completo = models.CharField(max_length=255)
    idade = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    exame = models.ImageField(upload_to='exames/')

    def __str__(self):
        return self.nome_completo
