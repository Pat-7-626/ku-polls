from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from .models import Choice, Question
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions, not including those set to be
        published in the future or that have already been closed.
        """
        questions = Question.objects.order_by('-pub_date')
        return [question for question in questions if question.can_vote()][:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet
        or that have already been closed.
        """
        return (Question.objects.filter(  # use can_vote logic
            pub_date__lte=timezone.localtime()).filter(
            Q(end_date__gte=timezone.localtime()) | Q(end_date__isnull=True)))


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """Vote for one of the answers to a question."""
    user = request.user
    print("current user is", user.id, "login", user.username)
    print("Real name:", user.first_name, user.last_name)
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    # Reference to the current user
    this_user = request.user

    # Get the user's vote
    try:
        # vote = user.vote_set.get(choice.question=question)
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # User has a vote for this question! Update his choice.
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        Vote.objects.create(user=this_user, choice=selected_choice)
        # Does not have to vote yet
        # Auto save
        messages.success(request, f"Your vote was changed to '{selected_choice.choice_text}'")
    selected_choice.votes = F("votes") + 1
    selected_choice.save()
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
