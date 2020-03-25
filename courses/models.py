from django.urls import reverse
from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(default='', max_length=100)
    course_length = models.CharField(default='', max_length=100)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Step(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ['order', ]

    def __str__(self):
        return self.title


class Text(Step):
    # Text class inheritance of Step
    video_name = models.CharField(blank=True, max_length=500, default='')
    video_file = models.FileField(blank=True, upload_to='videos/', null=True, verbose_name="")
    content = models.TextField(blank=True, default='')

    def get_absolute_url(self):
        return reverse('courses:text detail view', kwargs={
                       'course_pk': self.course_id,
                       'step_pk': self.id,
                       })


class Quiz(Step):
    # Quiz class inheritance of Step
    description = models.TextField(default='')
    total_questions = models.IntegerField(default=4)
    times_taken = models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name_plural = "Quizzes"

    def get_absolute_url(self):
        return reverse('courses:quiz detail view', kwargs={
                       'course_pk': self.course_id,
                       'quiz_pk': self.id
                       })


class Question(models.Model):
    multiplechoicequestion = 'MCQ'
    truefalsequestion = 'TFQ'
    userinputquestion = 'UIQ'
    QUESTION_TYPES = [
        (multiplechoicequestion, 'Multiple Choice Question'),
        (truefalsequestion, 'True False Question'),
        (userinputquestion, 'User Input Question'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    prompt = models.TextField()
    question_type = models.CharField(
        max_length=3,
        choices=QUESTION_TYPES,
        default=multiplechoicequestion,
    )

    class Meta:
        ordering = ['order', ]

    def get_absolute_url(self):
        return self.quiz.get_absolute_url()

    def __str__(self):
        return self.prompt


class MultipleChoiceQuestion(Question):
    # MultipleChoiceQuestion class inheritance of Question
    shuffle_answers = models.BooleanField(default=False)


class TrueFalseQuestion(Question):
    # TrueFalseQuestion class inheritance of Question
    pass


class UserInputQuestion(Question):
    # UserInputQuestion class inheritance of Question
    pass


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    text = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', ]

    def __str__(self):
        return self.text


# QuizTaker class
class QuizTaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    correct_answers = models.IntegerField(default=0)
    your_answers = dict()  # dictionary with user answers as keys and correctness as values
    completed = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' quiz_id: ' + str(self.quiz.id)
