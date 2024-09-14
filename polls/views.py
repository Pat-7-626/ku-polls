"""views.py for poll app."""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse
from django.views import generic
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import (user_logged_in, user_logged_out,
                                         user_login_failed)
from django.dispatch import receiver
from .models import Choice, Question, Vote
import logging

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """Index view."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the all published questions that are not closed."""
        questions = Question.objects.order_by('-pub_date')
        return [question for question in questions if question.can_vote()]


class DetailView(generic.DetailView):
    """Detail view."""

    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        """Display previous vote if exists."""
        messages.get_messages(self.request).used = True
        question = self.get_object()
        context = {'question': question}
        user = self.request.user
        if user.is_authenticated:
            try:
                vote = Vote.objects.get(user=user, choice__question=question)
                selected_choice = vote.choice
                messages.success(self.request,
                                 f"Your current vote "
                                 f"'{selected_choice.choice_text}'")
            except Vote.DoesNotExist:
                pass
        return context

    def get_queryset(self):
        """Excludes any questions that aren't published or is closed."""
        return (Question.objects.filter(  # use can_vote logic
            pub_date__lte=timezone.localtime()).filter(
            Q(end_date__gte=timezone.localtime()) | Q(end_date__isnull=True)))


class ResultsView(generic.DetailView):
    """results view."""

    model = Question
    template_name = 'polls/results.html'


@login_required
def vote(request, question_id):
    """Vote for one of the answers to a question."""
    messages.get_messages(request).used = True
    question = get_object_or_404(Question, pk=question_id)
    this_user = request.user
    ip_add = get_client_ip(request)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        logger.error(f"An error occurred for User {this_user.username} "
                     f"(IP: {ip_add}) while updating the vote by not "
                     f"selecting a choice.")
        messages.error(request, "You didn't select a choice.")
        return redirect('polls:detail', pk=question_id)

    # Get the user's vote
    try:
        # vote = user.vote_set.get(choice.question=question)
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # User has a vote for this question! Update his choice.
        vote.choice = selected_choice
        vote.save()
        messages.success(request, f"Your vote was changed to "
                                  f"'{selected_choice.choice_text}'")
        logger.info(f"User {this_user.username} (IP: {ip_add}) changed "
                    f"the vote in '{question}' to "
                    f"'{selected_choice.choice_text}'")
    except Vote.DoesNotExist:
        Vote.objects.create(user=this_user, choice=selected_choice)
        # Does not have to vote yet
        # Auto save
        messages.success(request, f"Your vote was submitted to "
                                  f"'{selected_choice.choice_text}'")
        logger.info(f"User {this_user.username} (IP: {ip_add}) submitted "
                    f"the vote in '{question}' to "
                    f"'{selected_choice.choice_text}'")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def signup(request):
    """Register a new user."""
    messages.get_messages(request).used = True
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(request, user, **kwargs):
    """Log for login."""
    ip_add = get_client_ip(request)
    logger.info(f"User {user.username} (IP: {ip_add}) logged in.")


@receiver(user_logged_out)
def log_user_logout(request, user, **kwargs):
    """Log for logout."""
    ip_add = get_client_ip(request)
    logger.info(f"User {user.username} (IP: {ip_add}) logged out.")


@receiver(user_login_failed)
def log_unsuccessful_login(credentials, request, **kwargs):
    """Log for login failed."""
    ip_add = get_client_ip(request)
    logger.warning(
        f"Unsuccessful login attempt for User {credentials.get('username')} "
        f"(IP: {ip_add})")
