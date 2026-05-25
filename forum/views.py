from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from knowledge.models import SAPModule


@login_required
def question_list(request):
    status_filter = request.GET.get('status', '')
    module_filter = request.GET.get('module', '')
    query = request.GET.get('q', '')

    questions = Question.objects.select_related('asked_by', 'module').prefetch_related('answers')
    if status_filter:
        questions = questions.filter(status=status_filter)
    if module_filter:
        questions = questions.filter(module__slug=module_filter)
    if query:
        questions = questions.filter(Q(title__icontains=query) | Q(body__icontains=query))

    paginator = Paginator(questions, 10)
    page = paginator.get_page(request.GET.get('page'))

    modules = SAPModule.objects.filter(is_active=True)
    return render(request, 'forum/question_list.html', {
        'questions': page,
        'modules': modules,
        'status_filter': status_filter,
        'selected_module': module_filter,
        'query': query,
        'status_choices': Question.STATUS_CHOICES,
    })


@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    Question.objects.filter(pk=pk).update(view_count=question.view_count + 1)
    answers = question.answers.select_related('answered_by')
    form = AnswerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.answered_by = request.user
        answer.save()
        # mark question answered
        if question.status == 'pending':
            Question.objects.filter(pk=pk).update(status='answered')
        messages.success(request, 'Answer posted!')
        return redirect('forum:question_detail', pk=pk)
    return render(request, 'forum/question_detail.html', {
        'question': question,
        'answers': answers,
        'form': form,
    })


@login_required
def question_create(request):
    form = QuestionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        q = form.save(commit=False)
        q.asked_by = request.user
        q.save()
        messages.success(request, 'Question posted! Experts will answer soon.')
        return redirect('forum:question_detail', pk=q.pk)
    return render(request, 'forum/question_form.html', {'form': form})


@login_required
def accept_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user == answer.question.asked_by or request.user.is_admin_or_trainer:
        Answer.objects.filter(question=answer.question).update(is_accepted=False)
        answer.is_accepted = True
        answer.save()
        Question.objects.filter(pk=answer.question.pk).update(status='answered')
        messages.success(request, 'Answer marked as accepted!')
    return redirect('forum:question_detail', pk=answer.question.pk)


@login_required
def upvote_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if request.user in answer.upvoted_by.all():
        answer.upvoted_by.remove(request.user)
        answer.upvotes = max(0, answer.upvotes - 1)
    else:
        answer.upvoted_by.add(request.user)
        answer.upvotes += 1
    answer.save()
    return JsonResponse({'upvotes': answer.upvotes})