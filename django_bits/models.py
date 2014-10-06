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

    created = models.DateTimeField(help_text="Creation time and date for the "
                                             "file.")

    last_modified = models.DateTimeField(help_text="Last time this file was "
                                                   "modified.")

    last_accessed = models.DateTimeField(help_text="Last time this file was "
                                                   "accessed.")

    record_modified = models.DateTimeField(auto_now=True,
                                           help_text="Last time this record "
                                                     "was modified")

class LookupType(models.Model):

    name = models.CharField(max_length=100,
                            help_text="The nature of the file detail (e.g "
                                      "'project number'.")

class FileDetail(models.Model):

    file_id = models.ForeignKey(File)
    type_id = models.ForeignKey(LookupType)
    detail = models.TextField(max_length=500,
                              help_text="The data held by the detail. For "
                                        "example, if the detail was a "
                                        "Project Number, this field could "
                                        "contain the string '600548'")


