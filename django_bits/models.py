from django.db import models

class File(models.Model):
    path = models.TextField(max_length=5000,
                            unique=True,
                            help_text="Full path of the file.")
    location = models.CharField(max_length=50,
                                blank=True,
                                help_text="A code specifying on which chunk of "
                                          "storage the file resides - e.g "
                                          "'LONDON_PROJECTS'")
    size = models.BigIntegerField()




