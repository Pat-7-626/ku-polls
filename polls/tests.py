from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question
import datetime


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    now = timezone.localtime()
    time = now + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_question_2(question_text, start, end):
    """
    Create a question with the given `question_text` and published the
    given number of `start` and `end` (negative for the past,
    positive for the future).
    """
    now = timezone.localtime()
    time_start = now + datetime.timedelta(days=start)
    time_end = now + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time_start,
                                   end_date=time_end)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59,
                                                   seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class IsPublishedTests(TestCase):
    def test_future_pub_date(self):
        """
        Questions with a future pub date should not be shown in the UI.
        """
        create_question_2(question_text="future question 1.",
                          start=1, end=3)
        create_question_2(question_text="future question 2.",
                          start=3, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertEqual(list(response.context['latest_question_list']), [])

    def test_default_pub_date(self):
        """
        Questions with a default pub date should be shown in the UI.
        """
        question1 = create_question_2(question_text="future question 1.",
                                      start=0, end=3)
        question2 = create_question_2(question_text="future question 2.",
                                      start=0, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question2, question1],
        )

    def test_past_date(self):
        """
        Questions with a past pub date should be shown in the UI.
        """
        question1 = create_question_2(question_text="future question 1.",
                                      start=-5, end=3)
        question2 = create_question_2(question_text="future question 2.",
                                      start=-1, end=5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['latest_question_list']),
            [question2, question1],
        )


class CanVoteTests(TestCase):
    def test_cannot_vote_after_end_date(self):
        """
        Can not vote for questions after the end date.
        """
        question = create_question_2(question_text="future question 1.",
                                     start=-2, end=-1)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_vote_before_start_date(self):
        """
        Can not vote for questions before the start date.
        """
        question = create_question_2(question_text="future question 1.",
                                     start=1, end=2)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_can_vote_between_period(self):
        """
        Can vote for questions between the polling period.
        """
        question = create_question_2(question_text="future question 1.",
                                     start=-1, end=2)
        url = reverse('polls:detail', args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
