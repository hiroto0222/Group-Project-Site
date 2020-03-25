from django.contrib import admin

from . import models

# Register your models here.
class StepInline(admin.StackedInline):
    model = models.Text


class CourseAdmin(admin.ModelAdmin):
    inlines = [StepInline, ]


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Text)
admin.site.register(models.Quiz)
admin.site.register(models.MultipleChoiceQuestion)
admin.site.register(models.TrueFalseQuestion)
admin.site.register(models.Answer)
