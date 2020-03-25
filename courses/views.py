from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned

from . import forms
from . import models

# Create your views here.
def course_list(request):
    courses = models.Course.objects.filter(
        published=True
    ).annotate(total_steps=Count('text', distinct=True) + Count('quiz', distinct=True))
    total = courses.aggregate(total=Sum('total_steps'))
    context = {'courses': courses, 'total': total}
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(models.Course, pk=pk, published=True)
    steps = sorted(chain(course.text_set.all(), course.quiz_set.all()),
                   key=lambda step: step.order)
    context = {'course': course, 'steps': steps}
    return render(request, 'courses/course_detail.html', context)


def text_detail(request, course_pk, step_pk):
    step = get_object_or_404(models.Text, course_id=course_pk, pk=step_pk, course__published=True)
    steps = sorted(chain(step.course.text_set.all(), step.course.quiz_set.all()),
                   key=lambda step: step.order)
    context = {'step': step, 'steps': steps}
    return render(request, 'courses/text_detail.html', context)


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def quiz_create(request, course_pk):
    course = get_object_or_404(models.Course, pk=course_pk, published=True)
    form = forms.QuizForm()

    if request.method == 'POST':
        form = forms.QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.add_message(request, messages.SUCCESS, "Quiz added!")
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/quiz_form.html', {'form': form, 'course': course})


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def quiz_edit(request, course_pk, quiz_pk):
    quiz = get_object_or_404(models.Quiz, pk=quiz_pk, course_id=course_pk, course__published=True)
    form = forms.QuizForm(instance=quiz)

    if request.method == 'POST':
        form = forms.QuizForm(instance=quiz, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/quiz_form.html', {'form': form, 'course': quiz.course})


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def create_question(request, quiz_pk, question_type):
    quiz = get_object_or_404(models.Quiz, pk=quiz_pk)
    if question_type == 'tf':
        form_class = forms.TrueFalseQuestionForm
    elif question_type == 'ui':
        form_class = forms.UserInputQuestionForm
    else:
        form_class = forms.MultipleChoiceQuestionForm

    form = form_class()
    answer_forms = forms.AnswerInlineFormSet(
        queryset=models.Answer.objects.none()
    )

    if request.method == 'POST':
        form = form_class(request.POST)
        answer_forms = forms.AnswerInlineFormSet(
            request.POST,
            queryset=models.Answer.objects.none()
        )
        if form.is_valid() and answer_forms.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            answers = answer_forms.save(commit=False)

            for answer in answers:
                answer.question = question
                answer.save()

            quiz.total_questions += 1
            quiz.save()
            messages.success(request, "Added Question")
            return HttpResponseRedirect(quiz.get_absolute_url())

    return render(request, 'courses/question_form.html', {
        'quiz': quiz,
        'form': form,
        'formset': answer_forms,
    })


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def edit_question(request, quiz_pk, question_pk):
    question = get_object_or_404(models.Question, pk=question_pk, quiz_id=quiz_pk)
    if hasattr(question, 'truefalsequestion'):
        form_class = forms.TrueFalseQuestionForm
        question = question.truefalsequestion
    elif hasattr(question, 'userinputquestion'):
        form_class = forms.UserInputQuestionForm
        question = question.userinputquestion
    else:
        form_class = forms.MultipleChoiceQuestionForm
        question = question.multiplechoicequestion

    form = form_class(instance=question)
    answer_forms = forms.AnswerInlineFormSet(
        queryset=form.instance.answer_set.all()
    )

    if request.method == 'POST':
        form = form_class(request.POST, instance=question)
        answer_forms = forms.AnswerInlineFormSet(
            request.POST,
            queryset=form.instance.answer_set.all(),
        )
        if form.is_valid() and answer_forms.is_valid():
            form.save()
            answers = answer_forms.save(commit=False)

            for answer in answers:
                answer.question = question
                answer.save()

            for answer in answer_forms.deleted_objects:
                answer.delete()

            messages.success(request, "Updated Question")
            return HttpResponseRedirect(question.quiz.get_absolute_url())

    return render(request, 'courses/question_form.html', {
        'form': form,
        'quiz': question.quiz,
        'formset': answer_forms,
    })


@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def answer_form(request, question_pk):
    question = get_object_or_404(models.Question, pk=question_pk)

    formset = forms.AnswerFormSet(queryset=question.answer_set.all())

    if request.method == 'POST':
        formset = forms.AnswerFormSet(request.POST,
                                      queryset=question.answer_set.all())
        if formset.is_valid():
            answers = formset.save(commit=False)

            for answer in answers:
                answer.question = question
                answer.save()
            messages.success(request, "Added Answers")
            return HttpResponseRedirect(question.quiz.get_absolute_url())

    return render(request, 'courses/answer_form.html', {
        'question': question,
        'formset': formset,
    })


@login_required
def quiz_detail(request, course_pk, quiz_pk):
    step = get_object_or_404(models.Quiz, course_id=course_pk, pk=quiz_pk, course__published=True)
    steps = sorted(chain(step.course.text_set.all(), step.course.quiz_set.all()),
                   key=lambda step: step.order)
    curr_user = request.user

    try:
        quiz_taker = curr_user.quiztaker_set.get(quiz_id=quiz_pk)
        error_message = "You have already taken this quiz"
    except models.QuizTaker.DoesNotExist:
        quiz_taker = None
        error_message = ""

    if request.method == 'POST':
        # if quiz_taker wants to retake completed quiz
        if request.POST.get('quiz_take_or_retake', "") == 'retake_quiz':
            quiz_taker.delete()
            curr_user.quiztaker_set.create(quiz_id=quiz_pk)
            return HttpResponseRedirect(reverse('courses:take_questions', args=(quiz_pk,)))

        elif request.POST.get('quiz_take_or_retake', "") == 'take_quiz':
            curr_user.quiztaker_set.create(quiz_id=quiz_pk)
            return HttpResponseRedirect(reverse('courses:take_questions', args=(quiz_pk,)))

        else:
            return reverse('courses:')

    return render(request, 'courses/take_quiz.html', {
                  'step': step,
                  'steps': steps,
                  'quiz_taker': quiz_taker,
                  'error_message': error_message,
                  })


@login_required
def take_questions(request, quiz_pk):
    quiz = get_object_or_404(models.Quiz, pk=quiz_pk)
    steps = sorted(chain(quiz.course.text_set.all(), quiz.course.quiz_set.all()),
                   key=lambda step: step.order)
    curr_user = request.user
    quiz_taker = curr_user.quiztaker_set.get(quiz_id=quiz_pk)
    questions = quiz.question_set.all()
    user_question_answers = []
    true_question_answers = []
    user_input_question_correct_or_incorrect = []

    if quiz_taker.correct_answers > 0:
        quiz_taker.correct_answers = 0

    if request.method == 'POST':

        for question in questions:

            if question.question_type == 'UIQ':
                true_question_answers.append(question.answer_set.get(correct=True))
                try:
                    question_id = str(question.pk)
                    your_answer = request.POST.get(question_id)
                    user_question_answers.append(your_answer)
                except (KeyError, models.Answer.DoesNotExist):
                    return render(request, 'courses/take_questions.html', {
                        'steps': steps,
                        'questions': questions,
                        'quiz': quiz,
                        'error_message': "You didn't answer a question"
                    })
                else:
                    if your_answer == question.answer_set.get(correct=True).text:
                        quiz_taker.correct_answers += 1
                        user_input_question_correct_or_incorrect.append(True)
                    else:
                        user_input_question_correct_or_incorrect.append(False)

            else:
                user_input_question_correct_or_incorrect.append(False)
                true_question_answers.append(question.answer_set.get(correct=True))
                try:
                    question_id = str(question.pk)
                    your_answer = question.answer_set.get(pk=request.POST.get(question_id))
                    user_question_answers.append(your_answer)
                except (KeyError, models.Answer.DoesNotExist):
                    return render(request, 'courses/take_questions.html', {
                        'steps': steps,
                        'questions': questions,
                        'quiz': quiz,
                        'error_message': "You didn't answer a question"
                    })
                else:
                    if your_answer.correct is True:
                        quiz_taker.correct_answers += 1

        quiz_taker.completed = True
        quiz_taker.save()

        quiz_taker_data = zip(
            questions,
            user_question_answers,
            true_question_answers,
            user_input_question_correct_or_incorrect,
        )

        context = {'quiz': quiz,
                   'steps': steps,
                   'quiz_taker': quiz_taker,
                   'quiz_taker_data': quiz_taker_data,
                   }

        return render(request, 'courses/quiz_result.html', context)

    return render(request, 'courses/take_questions.html', {
        'steps': steps,
        'questions': questions,
        'quiz': quiz
    })

def quiz_result(request, username, quiz_pk):
    return render(request, 'courses/quiz_result.html')

###################################################################


def courses_by_teacher(request, teacher):
    courses = models.Course.objects.filter(teacher__username=teacher, published=True)
    return render(request, 'courses/course_list.html', {'courses': courses})


def search(request):
    term = request.GET.get('q')
    courses = models.Course.objects.filter(
        Q(title__icontains=term) | Q(description__icontains=term),  # or
        published=True,
    )
    return render(request, 'courses/course_list.html', {'courses': courses})
