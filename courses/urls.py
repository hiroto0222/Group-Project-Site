from django.urls import path, re_path

from . import views

app_name = 'courses'
urlpatterns = [
    # /courses/
    path('', views.course_list, name='course list view'),
    # /courses/course_pk
    path('<int:pk>/', views.course_detail, name='course detail view'),
    # /courses/course_pk/step_pk
    path('<int:course_pk>/<int:step_pk>/', views.text_detail, name='text detail view'),
    # /courses/course_pk/quiz/step_pk
    path('<int:course_pk>/quiz/<int:quiz_pk>/', views.quiz_detail, name='quiz detail view'),
    # /courses/course_pk/create_quiz
    path('<int:course_pk>/create_quiz/', views.quiz_create, name='create_quiz'),
    # /courses/course_pk/step_pk
    path('<int:course_pk>/edit_quiz/<int:quiz_pk>/', views.quiz_edit, name='edit_quiz'),
    # /courses/quiz_pk/create_question/question_type
    re_path(r'(?P<quiz_pk>\d+)/create_question/(?P<question_type>mc|tf|ui)/$', views.create_question, name='create_question'),
    # /courses/course_pk/step_pk
    path('<int:quiz_pk>/edit_question/<int:question_pk>/', views.edit_question, name='edit_question'),
    # /courses/question_pk/create_answer
    path('<int:question_pk>/create_answer/', views.answer_form, name='create_answer'),
    # /courses/by/teacher
    path('by/<str:teacher>/', views.courses_by_teacher, name='by_teacher'),
    # /courses/search/
    path('search/', views.search, name='search'),
    # /courses/quiz/quiz_pk/question_pk
    # path('take_quiz/<int:quiz_pk>', views.take_quiz, name='take_quiz'),  # TEST URLS
    path('take_questions/<int:quiz_pk>', views.take_questions, name='take_questions'),  # TEST URLS
    path('<str:username>/quiz_result/<int:quiz_pk>', views.quiz_result, name='quiz_result'),  # TEST URLS
]
