from django.db import models


class Category(models.Model):
    id              = models.BigAutoField(primary_key=True)
    name            = models.CharField(max_length=50, null=True)
    description     = models.TextField(null=True, blank=True)

    class Meta:
        ordering    = ['id']

    def __str__(self):
        txt = '{\n'
        txt += 'ID \t: {},\n'.format(str(self.id))
        txt += 'NAME \t: {},\n'.format(str(self.name))
        txt += 'DESCRIPTION \t: {},\n'.format(str(self.description))
        txt += '}\n'
        return txt