from django import forms

from . import models


class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = [
            'title',
            'description',
            'order',
            'total_questions',
        ]


class TrueFalseQuestionForm(forms.ModelForm):
    class Meta:
        model = models.TrueFalseQuestion
        fields = [
            'order',
            'question_type',
            'prompt',
        ]


class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = models.MultipleChoiceQuestion
        fields = [
            'order',
            'question_type',
            'prompt',
            'shuffle_answers',
        ]


class UserInputQuestionForm(forms.ModelForm):
    class Meta:
        model = models.UserInputQuestion
        fields = [
            'order',
            'question_type',
            'prompt',
        ]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = [
            'order',
            'text',
            'correct',
        ]


# take quiz forms
class TakeQuestion(forms.Form):
    pass


AnswerFormSet = forms.modelformset_factory(
    models.Answer,
    form=AnswerForm,
    extra=2,
)


AnswerInlineFormSet = forms.inlineformset_factory(
    models.Question,
    models.Answer,
    extra=2,
    fields=('order', 'text', 'correct'),
    formset=AnswerFormSet,
    min_num=1,
)
