"""tests.py for testing the application."""

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from polls.models import Question
import datetime
import time


def create_question(question_text, days, start=None, end=None):
    """Create a question with `question_text` and set pub date."""
    now = timezone.localtime()
    time = now + datetime.timedelta(days=days)
    if start and end:
        time_start = now + datetime.timedelta(days=start)
        time_end = now + datetime.timedelta(days=end)
        return Question.objects.create(question_text=question_text,
                                       pub_date=time_start,
                                       end_date=time_end)
    else:
        return Question.objects.create(question_text=question_text,
                                       pub_date=time)


def create_question_2(question_text, start, end):
    """Create a question with `question_text` and set pub and end date."""
    now = timezone.localtime()
    time_start = now + datetime.timedelta(days=start)
    time_end = now + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time_start,
                                   end_date=time_end)


class QuestionIndexViewTests(TestCase):
    """tests for the index view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_past_question(self):
        """Questions with a past pub_date are displayed on the index."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question],
        )

    def test_future_question(self):
        """Questions with a future pub_date aren't displayed on the index."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_future_question_and_past_question(self):
        """Only past questions are displayed."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question],
        )

    def test_two_past_questions(self):
        """The questions index may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-5)
        question2 = create_question(question_text="Past question 2.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question1, question2],
        )


class QuestionDetailViewTests(TestCase):
    """tests for the detail view."""

    def test_future_question(self):
        """The detail view of a future pub_date question returns 404."""
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """The detail view of a past pub_date question displays a question."""
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class IsPublishedTests(TestCase):
    """tests for the is_published."""

    def test_future_pub_date(self):
        """Questions with a future pub date should not be shown in the UI."""
        create_question_2(question_text="future question 1.",
                          start=1, end=3)
        create_question_2(question_text="future question 2.",
                          start=3, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_default_pub_date(self):
        """Questions with a default pub date should be shown in the UI."""
        question1 = create_question_2(question_text="future question 1.",
                                      start=0, end=3)
        time.sleep(5)
        question2 = create_question_2(question_text="future question 2.",
                                      start=0, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question2, question1],
        )

    def test_past_date(self):
        """Questions with a past pub date should be shown in the UI."""
        question1 = create_question_2(question_text="future question 1.",
                                      start=-1, end=3)
        question2 = create_question_2(question_text="future question 2.",
                                      start=-5, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question1, question2],
        )


class CanVoteTests(TestCase):
    """tests for can_vote."""

    def test_cannot_vote_after_end_date(self):
        """Can not vote for questions after the end date."""
        question = create_question_2(question_text="future question 1.",
                                     start=-2, end=-1)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_vote_before_start_date(self):
        """Can not vote for questions before the start date."""
        question = create_question_2(question_text="future question 1.",
                                     start=1, end=2)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_can_vote_between_period(self):
        """Can vote for questions between the polling period."""
        question = create_question_2(question_text="future question 1.",
                                     start=-1, end=2)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
