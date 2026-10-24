
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Course, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        'onlinecourse/course_details_bootstrap.html',
        {'course': course}
    )
def take_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        'onlinecourse/exam.html',
        {'course': course}
    )

def submit(request, course_id):
    if request.method != 'POST':
        return redirect('course_details', course_id=course_id)

    course = get_object_or_404(Course, id=course_id)
    student_name = request.POST.get('student_name', 'Student').strip()
    if not student_name:
        student_name = 'Student'

    questions = Question.objects.filter(course=course)
    total_questions = questions.count()
    score = 0
    results = []

    for question in questions:
        selected_id = request.POST.get(f'question_{question.id}')
        selected_choice = Choice.objects.filter(
            id=selected_id,
            question=question
        ).first() if selected_id else None

        correct_choice = Choice.objects.filter(
            question=question,
            is_correct=True
        ).first()

        is_correct = (
            selected_choice is not None
            and selected_choice.is_correct
        )

        if is_correct:
            score += 1

        results.append({
            'question': question,
            'selected_choice': selected_choice,
            'correct_choice': correct_choice,
            'is_correct': is_correct,
        })

    submission = Submission.objects.create(
        student_name=student_name,
        course=course,
        score=score
    )

    request.session['exam_result'] = {
        'submission_id': submission.id,
        'student_name': student_name,
        'course_id': course.id,
        'score': score,
        'total_questions': total_questions,
        'results': [
            {
                'question': str(item['question'].question_text),
                'selected': (
                    item['selected_choice'].choice_text
                    if item['selected_choice'] else 'Not answered'
                ),
                'correct': (
                    item['correct_choice'].choice_text
                    if item['correct_choice'] else 'Not configured'
                ),
                'is_correct': item['is_correct'],
            }
            for item in results
        ]
    }

    return redirect('show_exam_result')


def show_exam_result(request):
    exam_result = request.session.get('exam_result')

    if not exam_result:
        return render(request, 'onlinecourse/exam_result.html', {
            'exam_result': None
        })

    return render(request, 'onlinecourse/exam_result.html', {
        'exam_result': exam_result
    })
