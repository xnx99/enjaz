# -*- coding: utf-8  -*-
import json
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators import csrf
from django.utils import timezone
from dal import autocomplete
from post_office import mail

from clubs.models import city_code_choices
from core.utils import get_search_queryset, create_tweet_by_access
from core.models import StudentClubYear, Tweet
from core import decorators
from bulb.models import Category, Book, NeededBook, Request, Point, Group, Membership, Session, Report, ReaderProfile, Recruitment, NewspaperSignup, Readathon, BookCommitment, RecommendedBook, BookRecommendation
from bulb.forms import BookGiveForm, BookLendForm, BookEditForm, NeededBookForm, RequestForm, GroupForm, FreeSessionForm, SessionForm, ReportForm, ReaderProfileForm, RecruitmentForm, NewspaperSignupForm, DewanyaSuggestionFormSet, BookCommitmentForm, UpdateBookCommitmentForm, CulturalProgramForm, EditBookRecommendationForm, AddBookRecommendationForm
from bulb import utils
import accounts.utils
import clubs.utils
import core.utils


def index(request):
    groups = Group.objects.current_year().for_user_city(request.user).unarchived().undeleted().order_by("?")[:6]
    sessions = Session.objects.current_year().for_user_city(request.user).undeleted()\
                              .filter(date__gte=timezone.now().date())\
                              .public()\
                              .order_by("date")[:5]
    group_count = Group.objects.current_year().undeleted().count()
    session_count = Session.objects.current_year().undeleted().count()
    group_user_count = (User.objects.filter(reading_group_memberships__isnull=False) | \
                        User.objects.filter(reading_group_coordination__isnull=False)).distinct().count()
    book_sample = Book.objects.current_year().for_user_city(request.user).available().order_by("?")[:6]
    latest_books = Book.objects.current_year().for_user_city(request.user).undeleted().order_by("-submission_date")[:6]
    latest_needed_books = NeededBook.objects.current_year().for_user_city(request.user).undeleted().order_by("-submission_date")[:6]
    book_count = Book.objects.current_year().for_user_city(request.user).undeleted().count()
    book_request_count = Request.objects.current_year().for_user_city(request.user).count()
    reader_profiles = ReaderProfile.objects.order_by("?")[:10]
    reader_profile_count = ReaderProfile.objects.count()
    context = {'groups': groups, 'group_count': group_count,
               'session_count': session_count, 'group_user_count':
               group_user_count, 'sessions': sessions, 'book_sample':
               book_sample, 'latest_books': latest_books,
               'latest_needed_books': latest_needed_books,
               'book_count': book_count, 'book_request_count':
               book_request_count, 'reader_profiles': reader_profiles,
               'reader_profile_count': reader_profile_count}
    return render(request, "bulb/index.html", context)

@login_required
def search_books(request):
    context = {}
    if request.GET.get('q'):
        existing_books = Book.objects.current_year().undeleted().available().for_user_city(request.user)
        fields = ['title', 'authors', 'description',
                  'submitter__common_profile__ar_first_name',
                  'submitter__common_profile__ar_middle_name',
                  'submitter__common_profile__ar_last_name',
                  'submitter__common_profile__en_first_name',
                  'submitter__common_profile__en_middle_name',
                  'submitter__common_profile__en_last_name']
        results = get_search_queryset(existing_books, fields, request.GET['q'])
        context['results'] = results
    return render(request, "bulb/exchange/search.html", context)

@login_required
def search_readers(request):
    context = {}
    if request.GET.get('q'):
        existing_readers = ReaderProfile.objects.all()
        fields = ['areas_of_interests', 'favorite_books',
                  'favorite_writers', 'twitter',
                  'user__common_profile__ar_first_name',
                  'user__common_profile__ar_middle_name',
                  'user__common_profile__ar_last_name',
                  'user__common_profile__en_first_name',
                  'user__common_profile__en_middle_name',
                  'user__common_profile__en_last_name']
        results = get_search_queryset(existing_readers, fields, request.GET['q'])
        context['results'] = results
    return render(request, "bulb/readers/search.html", context)

@login_required
def list_book_categories(request):
    categories = Category.objects.distinct().filter(book__isnull=False,
                                                    book__is_available=True,
                                                    book__is_deleted=False)
    # If we have books, show the All category.
    if Book.objects.current_year().undeleted().for_user_city(request.user).available().exists():
        categories |= Category.objects.filter(code_name="all").distinct()
    context = {'categories': categories}
    return render(request, "bulb/exchange/list_categories.html",
                  context)

@login_required
def list_needed_book_categories(request):
    categories = Category.objects.distinct().filter(neededbook__isnull=False,
                                                    neededbook__is_deleted=False)
    # If we have books, show the All category.
    if NeededBook.objects.current_year().undeleted().for_user_city(request.user).still_needed().exists():
        categories |= Category.objects.filter(code_name="all").distinct()
    context = {'categories': categories, 'needed': True}
    return render(request, "bulb/exchange/list_categories.html",
                  context)

@login_required
def books_by_date(request):
    books =  Book.objects.current_year().for_user_city(request.user).undeleted().order_by("-submission_date")
    return render(request, "bulb/exchange/books_by_date.html",
                  {'books': books})

@login_required
def show_category(request, code_name, needed=False):
    category = get_object_or_404(Category, code_name=code_name)
    context = {'category': category, 'needed': needed}
    return render(request, "bulb/exchange/show_category.html", context)

@decorators.ajax_only
@csrf.csrf_exempt
@login_required
def list_book_previews(request, source, name):
    if source == "category":
        category = get_object_or_404(Category, code_name=name)
        books = Book.objects.current_year().for_user_city(request.user).undeleted().available()
        if category.code_name != 'all':
            books = books.filter(category=category)
    elif source == "user":
        condition = request.POST.get('condition')
        user = get_object_or_404(User, username=name)
        if condition == 'available':
            books = Book.objects.current_year().undeleted().available().of_user(user)
        elif condition == 'borrowed':
            book_pks = Request.objects.filter(book__contribution='L', owner_status='D')\
                                      .values_list('book__pk', flat=True)
            books = Book.objects.current_year().undeleted().filter(pk__in=book_pks, is_deleted=False).of_user(user).distinct()
        elif condition == 'done':
            book_pks = (Request.objects.filter(book__contribution="G",
                                          owner_status="D") | \
                        Request.objects.filter(book__contribution="L",
                                          owner_status="R"))\
                                       .values_list('book__pk', flat=True)
            books = Book.objects.current_year().undeleted().filter(pk__in=book_pks, is_deleted=False).of_user(user).distinct()

    return render(request, "bulb/exchange/components/list_books.html",
                  {'books': books})

@decorators.ajax_only
@csrf.csrf_exempt
@login_required
def list_needed_book_previews(request, source, name):
    if source == "category":
        category = get_object_or_404(Category, code_name=name)
        needed_books = NeededBook.objects.current_year().for_user_city(request.user).undeleted().still_needed()
        if category.code_name != 'all':
            needed_books = needed_books.filter(category=category)
    elif source == "user":
        condition = request.POST.get('condition')
        user = get_object_or_404(User, username=name)
        if condition == 'still_needed':
            needed_books = NeededBook.objects.current_year().undeleted().still_needed().of_user(user)
        elif condition == 'fulfilled':
            needed_books = NeededBook.objects.current_year()\
                                             .undeleted()\
                                             .filter(existing_book__isnull=False)\
                                             .of_user(user)

    return render(request, "bulb/exchange/components/list_needed_books.html",
                  {'needed_books': needed_books})

@decorators.ajax_only
@decorators.get_only
@login_required
def order_instructions(request, pk):
    book = get_object_or_404(Book, pk=pk, is_deleted=False)
    book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", book.submitter).coordinator
    last_request = book.last_pending_request()
    current_year = StudentClubYear.objects.get_current()
    if current_year.bookexchange_close_date and timezone.now().date() > current_year.bookexchange_close_date:
        return render(request, 'bulb/exchange/bookexchange_closure.html', {'current_year':current_year})
    if not (last_request and last_request.requester == request.user) and \
       not utils.can_order_book(request.user, book):
        raise PermissionDenied

    context = {'book': book, 'book_exchange_coordinator': book_exchange_coordinator}

    return render(request, "bulb/exchange/components/order_body.html",
                  context)

@decorators.ajax_only
@login_required
@csrf.csrf_exempt
def confirm_book_order(request, pk):
    book = get_object_or_404(Book, pk=pk, is_deleted=False)
    book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", book.submitter).coordinator
    current_year = StudentClubYear.objects.get_current()
    instance = Request(requester=request.user, book=book)

    if current_year.bookexchange_close_date and timezone.now() > current_year.bookexchange_close_date:
        return render(request, 'bulb/exchange/book_section_is_closed.html', {'current_year':current_year})

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=instance)

        # TODO: In case the user lost thier balance after this form
        # was shown, no error message will be shown.  Show it?
        if book.contribution == 'G':
            balance_test = request.user.book_points.count_total_giving
        elif book.contribution == 'L':
            balance_test = request.user.book_points.count_total_lending

        if form.is_valid() and balance_test():
            book_request = form.save()
            current_year = StudentClubYear.objects.get_current()
            Point.objects.create(year=current_year,
                                 category=book.contribution,
                                 request=book_request,
                                 user=request.user,
                                 value=-1)
            book.is_available = False
            book.save()
            email_context = {'book': book,
                             'book_request': book_request}
            my_books_url = reverse('bulb:my_books')
            my_books_full_url = request.build_absolute_uri(my_books_url)
            if book_request.delivery == 'I':
                owner_template = "book_requested_indirectly_to_owner"
                if book_exchange_coordinator:
                    indirect_requests_url = reverse('bulb:indirect_requests')
                    indirect_requests_full_url = request.build_absolute_uri(indirect_requests_url)
                    email_context['full_url'] = indirect_requests_full_url
                    email_context['book_exchange_coordinator'] = book_exchange_coordinator
                    cc = utils.get_indirect_request_cc(book)
                    mail.send([book_exchange_coordinator.email],
                              cc=cc,
                              template="book_requested_indirectly_to_coordinator",
                              context=email_context)
            elif book_request.delivery == 'D':
                owner_template = "book_requested_directly_to_owner"

            # If the book is publicly owned, don't send an emial
            # notification
            if not book.is_publicly_owned:
                email_context['full_url'] = my_books_full_url
                mail.send([book.submitter.email],
                          template=owner_template,
                          context=email_context)
            requests_by_me_url = reverse('bulb:requests_by_me')
            full_url = request.build_absolute_uri(requests_by_me_url)
            return {"message": "success", "list_url": full_url}

    elif request.method == 'GET':
        form = RequestForm(instance=instance)


    return render(request, "bulb/exchange/components/confirm_book_order.html",
                  {'book': book, 'form': form})

@login_required
def show_book(request, pk):
    book = get_object_or_404(Book, pk=pk, is_deleted=False)
    book_pool = Book.objects.exclude(pk=book.pk).current_year().for_user_city(request.user).available().order_by("?")
    if book.is_publicly_owned:
        sample_user_books = book_pool.filter(is_publicly_owned=True)[:3]
    else:
        sample_user_books = book_pool.filter(submitter=book.submitter)[:3]
    sample_category_books = book_pool.exclude(pk__in=[b.pk for b in sample_user_books])\
                                     .filter(category=book.category)[:3]
    return render(request, "bulb/exchange/show_book.html",
                  {'book': book, 'sample_user_books': sample_user_books,
                   'sample_category_books': sample_category_books})

@login_required
def show_needed_book(request, pk):
    needed_book = get_object_or_404(NeededBook, pk=pk, is_deleted=False)
    sample_category_books = Book.objects.current_year().for_user_city(request.user).available()\
                                        .order_by("?")\
                                        .filter(category=needed_book.category)[:3]
    return render(request, "bulb/exchange/show_needed_book.html",
                  {'needed_book': needed_book,
                   'sample_category_books': sample_category_books})


@decorators.ajax_only
@login_required
@decorators.get_only
def confirm_book_deletion(request, pk):
    book = get_object_or_404(Book, pk=pk, is_deleted=False)
    if not utils.can_edit_book(request.user, book):
        raise PermissionDenied

    return render(request, "bulb/exchange/components/confirm_book_deletion.html",
                  {'book': book})

@decorators.ajax_only
@login_required
@decorators.get_only
def confirm_needed_book_deletion(request, pk):
    needed_book = get_object_or_404(NeededBook, pk=pk, is_deleted=False)
    if not utils.can_edit_needed_book(request.user, needed_book):
        raise PermissionDenied

    return render(request, "bulb/exchange/components/confirm_needed_book_deletion.html",
                  {'needed_book': needed_book})

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk, is_deleted=False)
    if not utils.can_edit_book(request.user, book):
        raise Exception(u"لا تستطيع حذف الكتاب")

    # Book owners cannot delete a book if it has any pending requests,
    # but superusers and Bulb coordinators can, and in that case,
    # notify the book owner, then check for pending requests notify
    # the requester accordingly.
    if request.user != book.submitter:
        pending_request = book.last_pending_request()
        book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", book.submitter).coordinator
        if book_exchange_coordinator:
            cc_coordinator = [book_exchange_coordinator.email]
        else:
            cc_coordinator = []
        email_context = {'book': book,
                         'book_request': pending_request,
                         'book_exchange_coordinator': book_exchange_coordinator}
        if not book.is_publicly_owned:
            mail.send([book.submitter.email],
                      cc=cc_coordinator,
                      template="book_deleted_to_owner",
                      context=email_context)
        if pending_request:
            pending_request.cancel_related_user_point(pending_request.requester)
            mail.send([pending_request.requester.email],
                      cc=cc_coordinator,
                      template="book_deleted_to_requester",
                      context=email_context)

    book.is_deleted = True
    book.save()
    show_category_url = reverse('bulb:show_category',
                                args=(book.category.code_name,))
    full_url = request.build_absolute_uri(show_category_url)
    return {"message": "success", "list_url": full_url}

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def delete_needed_book(request, pk):
    needed_book = get_object_or_404(NeededBook, pk=pk,
                                    is_deleted=False)
    if not utils.can_edit_needed_book(request.user, needed_book):
        raise Exception(u"لا تستطيع حذف المجموعة")

    needed_book.is_deleted = True
    needed_book.save()
    list_url = reverse('bulb:show_needed_category', args=(needed_book.category.code_name,))
    full_url = request.build_absolute_uri(list_url)
    return {"message": "success", "list_url": full_url}

@decorators.ajax_only
@login_required
def add_book(request, contribution):

    if contribution  == 'lend':
        BookForm = BookLendForm
        contribution = 'L'
    elif contribution  == 'give':
        BookForm = BookGiveForm
        contribution = 'G'

    if request.method == 'POST':
        current_year = StudentClubYear.objects.get_current()
        instance = Book(submitter=request.user,
                        year=current_year,
                        contribution=contribution)
        form = BookForm(request.POST, request.FILES, instance=instance, user=request.user)
        if form.is_valid():
            book = form.save()
            show_book_url = reverse('bulb:show_book', args=(book.pk,))
            full_url = request.build_absolute_uri(show_book_url)
            if not book.is_publicly_owned:
                utils.create_tweet(request.user, 'add_book',
                                   (book.title, full_url),
                                   media_path=book.cover.path)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = BookForm(user=request.user)

    context = {'form': form}
    return render(request, 'bulb/exchange/edit_book_form.html', context)
@decorators.ajax_only
@login_required
def add_needed_book(request):
    if request.method == 'POST':
        current_year = StudentClubYear.objects.get_current()
        instance = NeededBook(requester=request.user,
                              year=current_year)
        form = NeededBookForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            needed_book = form.save()
            show_url = reverse('bulb:show_needed_book', args=(needed_book.pk,))
            full_url = request.build_absolute_uri(show_url)
            utils.create_tweet(request.user, 'add_needed_book',
                               (needed_book.title, full_url),
                               media_path=needed_book.cover.path)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = NeededBookForm()

    context = {'form': form}
    return render(request, 'bulb/exchange/edit_needed_book_form.html', context)


@decorators.ajax_only
@login_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if not utils.can_edit_book(request.user, book):
        raise Exception(u"لا تستطيع تعديل الكتاب")

    context = {'book': book}
    if request.method == 'POST':
        form = BookEditForm(request.POST, request.FILES, instance=book, user=request.user)
        if form.is_valid():
            book = form.save()
            show_book_url = reverse('bulb:show_book', args=(book.pk,))
            full_url = request.build_absolute_uri(show_book_url)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = BookEditForm(instance=book, user=request.user)

    context['form'] = form
    return render(request, 'bulb/exchange/edit_book_form.html', context)

@decorators.ajax_only
@login_required
def edit_needed_book(request, pk):
    needed_book = get_object_or_404(NeededBook, pk=pk)

    if not utils.can_edit_needed_book(request.user, needed_book):
        raise Exception(u"لا تستطيع تعديل الكتاب")

    context = {'needed_book': needed_book}
    if request.method == 'POST':
        form = NeededBookForm(request.POST, request.FILES, instance=needed_book)
        if form.is_valid():
            needed_book = form.save()
            show_book_url = reverse('bulb:show_needed_book', args=(needed_book.pk,))
            full_url = request.build_absolute_uri(show_book_url)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = NeededBookForm(instance=needed_book)

    context['form'] = form
    return render(request, 'bulb/exchange/edit_needed_book_form.html', context)


@login_required
def requests_by_me(request):
    context = {}
    context['pending'] = Request.objects.filter(requester=request.user,
                                                requester_status='')
    context['canceled'] = Request.objects.filter(requester=request.user,
                                                 requester_status='C')
    context['rejected'] = Request.objects.filter(requester=request.user,
                                                 owner_status='C')
    context['failed'] = Request.objects.filter(requester=request.user,
                                               owner_status='F')
    context['done'] = Request.objects.filter(requester=request.user,
                                             requester_status='D')
    return render(request, 'bulb/exchange/requests_by_me.html', context)

@login_required
def my_books(request):
    return render(request, 'bulb/exchange/my_books.html')

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def pending_book(request):
    pk = request.POST.get('pk')
    book_request = get_object_or_404(Request, pk=pk)

    if not utils.can_edit_book(request.user, book_request.book):
        raise PermissionDenied

    return render(request, 'bulb/exchange/pending_book.html',
                  {'book': book_request.book})

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def pending_request(request):
    pk = request.POST.get('pk')
    book_request = get_object_or_404(Request, pk=pk)

    return render(request, 'bulb/exchange/pending_request.html',
                  {'book_request': book_request})

@decorators.ajax_only
@login_required
@csrf.csrf_exempt
def list_my_books(request):
    book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", request.user).coordinator
    condition = request.POST.get('condition')
    if condition == 'pending':
        pks = Request.objects.filter(status="",
                                     owner_status__in=["", "F"])\
                          .values_list('book__pk', flat=True)
    elif condition == 'borrowed':
        pks = Request.objects.filter(status__in=["", "D"],
                                     book__contribution="L",
                                     owner_status="D")\
                          .values_list('book__pk', flat=True)
    elif condition == 'done':
        pks = (Request.objects.filter(book__contribution="G",
                                      owner_status="D") | \
               Request.objects.filter(book__contribution="L",
                                      owner_status="R"))\
                      .values_list('book__pk', flat=True)

    books = Book.objects.filter(pk__in=pks, is_deleted=False).of_user(request.user).distinct()

    context =  {'books': books,
                'book_exchange_coordinator': book_exchange_coordinator}
    return render(request, 'bulb/exchange/list_my_books.html', context)


@decorators.ajax_only
@login_required
@csrf.csrf_exempt
def list_my_requests(request):
    book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", request.user).coordinator
    condition = request.POST.get('condition')
    if condition == 'pending':
        requests = Request.objects.filter(requester=request.user,
                                          status="",
                                          requester_status__in=["", "F"])
    elif condition == 'borrowing':
        requests = Request.objects.filter(requester=request.user,
                                          book__contribution="L",
                                          status__in=["", "D"],
                                          requester_status="D")
    elif condition == 'done':
        requests = Request.objects.filter(requester=request.user,
                                          book__contribution="G",
                                          requester_status="D") | \
                   Request.objects.filter(requester=request.user,
                                          book__contribution="L",
                                          requester_status="R")

    context =  {'requests': requests,
                'book_exchange_coordinator': book_exchange_coordinator}
    return render(request, 'bulb/exchange/list_direct_requests.html', context)

@login_required
def indicators(request, city_code=""):
    if not utils.is_bulb_coordinator_or_deputy(request.user) and \
       not utils.is_bulb_member(request.user) and \
       not utils.is_in_book_exchange_team(request.user) and \
       not request.user.is_superuser:
        raise PermissionDenied

    if city_code:
        city = accounts.utils.get_city_from_code(city_code)
        # To avoid user fuck-ups entering non-standard city-code.
        if not city:
            raise Http404
        books = Book.objects.current_year().filter(submitter__common_profile__city=city)
        book_requests = Request.objects.current_year().filter(requester__common_profile__city=city)
        groups = Group.objects.current_year().filter(coordinator__common_profile__city=city)
        sessions = Session.objects.current_year().filter(group__coordinator__common_profile__city=city) | \
                   Session.objects.current_year().filter(group__isnull=True, submitter__common_profile__city=city)

        detailed_users = (User.objects.filter(book_giveaways__isnull=False) |
                          User.objects.filter(reading_group_coordination__isnull=False) |
                          User.objects.filter(request__isnull=False))\
                         .filter(common_profile__city=city).distinct()

        users = (User.objects.filter(book_giveaways__isnull=False) |
                 User.objects.filter(request__isnull=False) |
                 User.objects.filter(reading_group_coordination__isnull=False) |
                 User.objects.filter(reading_group_memberships__isnull=False) |
                 User.objects.filter(reader_profile__isnull=False))\
                 .filter(common_profile__city=city).distinct()

        user_count = users.count()

        book_users = User.objects.filter(common_profile__is_student=True,
                                         book_points__is_counted=True)\
                                 .annotate(point_count=Count('book_points'))\
                                 .filter(point_count__gte=4)\
                                 .filter(common_profile__city=city)
        book_contributing_male_users = User.objects.filter(common_profile__college__gender='M',
                                                           book_giveaways__isnull=False)\
                                                    .filter(common_profile__city=city)\
                                                   .distinct().count()
        book_contributing_female_users = User.objects.filter(common_profile__college__gender='F',
                                                             book_giveaways__isnull=False)\
                                                     .filter(common_profile__city=city)\
                                                     .distinct().count()
        group_male_users = (User.objects.filter(reading_group_memberships__isnull=False,
                                                common_profile__college__gender='M') | \
                            User.objects.filter(reading_group_coordination__isnull=False,
                                                common_profile__college__gender='M'))\
                                        .filter(common_profile__city=city)\
                                        .distinct().count()
        group_female_users = (User.objects.filter(reading_group_memberships__isnull=False,
                                                  common_profile__college__gender='F') | \
                              User.objects.filter(reading_group_coordination__isnull=False,
                                                  common_profile__college__gender='F'))\
                                          .filter(common_profile__city=city).distinct().count()

        newspaper_emails = [user.email for user in users if user.email]
        newspaper_emails += [signup.get_email() for signup in NewspaperSignup.objects.all()]
        newspaper_emails = set(newspaper_emails)

        newspaper_signup_count = NewspaperSignup.objects.count()

        context = {'groups': groups,
                   'sessions': sessions,
                   'books': books,
                   'book_requests': book_requests,
                   'detailed_users': detailed_users,
                   'book_users': book_users,
                   'users': users,
                   'book_contributing_male_users': book_contributing_male_users,
                   'book_contributing_female_users': book_contributing_female_users,
                   'group_male_users': group_male_users,
                   'group_female_users': group_female_users,
                   'user_count': user_count,
                   'newspaper_signup_count': newspaper_signup_count,
                   'newspaper_emails': newspaper_emails}

    else:
        context = {'city_choices':
                   city_code_choices}

    return render(request, 'bulb/indicators.html', context)

@decorators.ajax_only
@csrf.csrf_exempt
@login_required
def list_indirect_requests(request):
    if not utils.is_bulb_coordinator_or_deputy(request.user) and \
       not utils.is_bulb_member(request.user) and \
       not utils.is_in_book_exchange_team(request.user) and \
       not request.user.is_superuser:
        raise PermissionDenied

    condition = request.POST.get('condition')
    book_exchange_team = clubs.utils.get_team_for_user("book_exchange", request.user)
    if condition == 'to_receive':
        # Get all requests that are:
        # * for indirect delivery,
        # * have not been acted upon for owner (i.e. not canceled nor given)
        # * have not been canceled nor received by requester.
        requests = Request.objects.filter(delivery='I',
                                          owner_status='',
                                          requester_status='',
                                          book__submitter__common_profile__city=book_exchange_team.city,
                                          book__submitter__common_profile__college__gender=book_exchange_team.gender)
        side = 'owner'
    elif condition == 'to_give':
        # Get all requests that are:
        # * for indirect delivery,
        # * have been received from owner,
        # * have not been acted upon for requester (i.e. not canceled nor received)
        requests = Request.objects.filter(delivery='I',
                                          owner_status='D',
                                          requester_status='',
                                          requester__common_profile__city=book_exchange_team.city,
                                          requester__common_profile__college__gender=book_exchange_team.gender)
        side = 'requester'
    elif condition == 'to_return_to_owner':
        # Get all requesters that are:
        # * for indirect delivery,
        # * for lending,
        # * have been returned by the requester but not to the owner
        requests = Request.objects.filter(delivery='I',
                                          book__contribution='L',
                                          requester_status='R',
                                          owner_status='D',
                                          borrowing_end_date__lte=timezone.now(),
                                          book__submitter__common_profile__city=book_exchange_team.city,
                                          book__submitter__common_profile__college__gender=book_exchange_team.gender)
        side = 'owner'
    elif condition == 'to_claim_from_requester':
        # Get all requesters that are:
        # * for indirect delivery,
        # * for lending,
        # * haven't been returned by the requesters,
        requests = Request.objects.filter(delivery='I',
                                          book__contribution='L',
                                          requester_status='D',
                                          borrowing_end_date__lte=timezone.now(),
                                          requester__common_profile__city=book_exchange_team.city,
                                          requester__common_profile__college__gender=book_exchange_team.gender)
        side = 'requester'
    elif condition == 'failed_requester':
        # Get all requesters that are:
        # * for indirect delivery,
        # * for lending,
        # * haven't been returned by the requesters,
        requests = Request.objects.filter(delivery='I',
                                          requester_status='F',
                                          requester__common_profile__city=book_exchange_team.city,
                                          requester__common_profile__college__gender=book_exchange_team.gender)
        side = 'requester'
    elif condition == 'failed_owner':
        requests = Request.objects.filter(delivery='I',
                                          owner_status='F',
                                          book__submitter__common_profile__city=book_exchange_team.city,
                                          book__submitter__common_profile__college__gender=book_exchange_team.gender)
        side = 'owner'
    elif condition == 'done':
        # Get all requesters that are:
        # * for indirect delivery,
        # * either the requester's status is done and the requester's gender is the same as the bulb's,
        # * or the owner's status is done and the owner's gender is the same as bulb's.
        # * exclude requests that are supposed to be in the claim/return lists.
        requests = Request.objects.filter(delivery='I',
                                          owner_status='D',
                                          book__submitter__common_profile__city=book_exchange_team.city,
                                          book__submitter__common_profile__college__gender=book_exchange_team.gender)\
                                  .exclude(book__contribution='L',
                                           borrowing_end_date__lte=timezone.now()) | \
                   Request.objects.filter(delivery='I',
                                          requester_status='D',
                                          requester__common_profile__city=book_exchange_team.city,
                                          requester__common_profile__college__gender=book_exchange_team.gender)\
                                  .exclude(book__contribution='L',
                                           borrowing_end_date__lte=timezone.now()) | \
                   Request.objects.filter(delivery='I',
                                          book__contribution='L',
                                          status='R',
                                          requester__common_profile__city=book_exchange_team.city,
                                          requester__common_profile__college__gender=book_exchange_team.gender)

        side = None

    context = {'requests': requests,
               'side': side}

    return render(request, 'bulb/exchange/list_indirect_requests.html', context)

@login_required
def indirect_requests(request):
    if not utils.is_bulb_coordinator_or_deputy(request.user) and \
       not utils.is_bulb_member(request.user) and \
       not utils.is_in_book_exchange_team(request.user) and \
       not request.user.is_superuser:
        raise PermissionDenied

    return render(request, 'bulb/exchange/indirect_requests.html')

@login_required
def disputed_requests(request):
    if not utils.is_bulb_coordinator_or_deputy(request.user) and \
       not request.user.is_superuser:
        raise PermissionDenied

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def control_request(request):
    action = request.POST.get('action')
    request_pk = request.POST.get('pk')
    book_request = get_object_or_404(Request, pk=request_pk)
    book = book_request.book
    book_exchange_coordinator = clubs.utils.get_team_for_user("book_exchange", book.submitter).coordinator
    if book_exchange_coordinator:
        cc_coordinator = [book_exchange_coordinator.email]
    else:
        cc_coordinator = []
    email_context = {'book': book,
                     'book_request': book_request,
                     'book_exchange_coordinator': book_exchange_coordinator}

    if action.startswith('owner_'):
        if not utils.can_edit_owner_status(request.user, book):
            raise Exception(u"لا يمكنك اتخاذ إجراء باسم صاحب الكتاب.")
        previous_owner_status = book_request.owner_status
        if action == 'owner_done' and previous_owner_status != 'D':
            book.is_available = False
            book_request.owner_status = 'D'
            book_request.owner_status_date = timezone.now()

            # If the book requester had already confirmed the request,
            # consider the reuqest done.  Otherwise, keep it pending
            # (to be shown in the requester's pending requests list).
            # In that case, when seven days have passed since the
            # request was submitted, a cron job would mark it as done
            # (to be removed from the requester's pending requests
            # list).
            if book_request.requester_status == 'D':
                book_request.status = 'D'

            # If no previous points or codes have been created
            # (i.e. by requester's confirmation), create one.
            book_request.create_related_points()
            book_request.create_related_niqati_codes()

        elif action == 'owner_returned' and previous_owner_status != 'R':
            book.is_available = True
            book_request.owner_status = 'R'
            book_request.owner_status_date = timezone.now()
            # If the book requester had already confirmed returning
            # the book, consider the reuqest returned.  Otherwise,
            # keep it pending (to be shown in the requester's pending
            # requests list).  In that case, when seven days have
            # passed since the request was submitted, a cron job would
            # mark it as done (to be removed from the requester's
            # pending requests list).
            if book_request.requester_status == 'R':
                book_request.status = 'R'

        elif action == 'owner_failed' and previous_owner_status != 'F':
            book_request.owner_status = 'F'
            book_request.owner_status_date = timezone.now()

            requests_by_me_url = reverse('bulb:requests_by_me')
            full_url = request.build_absolute_uri(requests_by_me_url)
            email_context['full_url'] = full_url

            if book_request.delivery == 'I':
                # If Bulb coordinator failed to comminicate with the
                # owner, make the book available again and email both
                # the owner and the requester that the request has
                # been canceled.
                book.is_available = True
                book_request.status = 'C'
                # Return the point to the book requester
                book_request.cancel_related_user_point(book_request.requester)
                mail.send([book_request.requester.email],
                          cc=cc_coordinator,
                          template="indirect_book_request_failed_to_requester",
                          context=email_context)
                if not book.is_publicly_owned:
                    mail.send([book.submitter.email],
                              cc=cc_coordinator,
                              template="indirect_book_request_failed_to_owner",
                              context=email_context)
            elif book_request.delivery == 'D':
                # Just to make sure
                book.is_available = False
                mail.send([book_request.requester.email],
                           template="book_request_failed_to_requester",
                           context=email_context)

        elif action == 'owner_canceled' and previous_owner_status != 'C':
            book.is_available = True
            book_request.owner_status = 'C'
            book_request.owner_status_date = timezone.now()

            # If one party canceled the request (in this case: the
            # book owner), and ther other hasn't confirmed it, that's
            # enough to consider the whole request canceled.
            # Otherwise, it will be handled in the conflicts section.
            if book_request.requester_status != 'D':
                book_request.status = 'C'

            # Return the point to the book requester
            book_request.cancel_related_user_point(book_request.requester)
            list_book_categories_url = reverse('bulb:list_book_categories')
            full_url = request.build_absolute_uri(list_book_categories_url)
            email_context['full_url'] = full_url
            mail.send([book_request.requester.email],
                      cc=cc_coordinator,
                      template="book_request_canceled_to_requester",
                      context=email_context)
            # Also, email Bulb coordinator.
            if book_request.delivery == 'I' and book_exchange_coordinator:
                cc = utils.get_indirect_request_cc(book)
                mail.send([book_exchange_coordinator.email],
                          cc=cc,
                          template="indirect_book_request_canceled_to_coordinator",
                          context=email_context)
    elif action.startswith('requester_'):
        if not utils.can_edit_requester_status(request.user, book_request):
            raise Exception(u"لا يمكنك اتخاذ إجراء باسم مقدم الطلب.")

        previous_requester_status = book_request.requester_status
        if action == 'requester_done' and previous_requester_status != 'D':
            book.is_available = False
            book_request.requester_status = 'D'
            book_request.requester_status_date = timezone.now()

            # If the book owner had already confirmed the request,
            # consider the reuqest done.  Otherwise, keep it pending
            # (to be shown in the owner's pending books list).  In the
            # case, when seven days have passed since the request was
            # submitted, a cron job would mark it as done (to be
            # removed from the owner's pending book list).
            if book_request.owner_status == 'D':
                book_request.status = 'D'

            # If no previous points or codes have been created
            # (i.e. by requester's confirmation), create one.
            book_request.create_related_points()
            book_request.create_related_niqati_codes()

        elif action == 'requester_returned' and previous_requester_status != 'R':
            book.is_available = True
            book_request.requester_status = 'R'
            book_request.requester_status_date = timezone.now()
            # If the book requester had already confirmed returning
            # the book, consider the reuqest returned.  Otherwise,
            # keep it pending (to be shown in the requester's pending
            # requests list).  In that case, when seven days have
            # passed since the request was submitted, a cron job would
            # mark it as done (to be removed from the requester's
            # pending requests list).
            if book_request.owner_status == 'R':
                book_request.status = 'R'

        elif action == 'requester_failed' and previous_requester_status != 'F':
            book_request.requester_status = 'F'
            book_request.requester_status_date = timezone.now()

            my_books_url = reverse('bulb:my_books')
            full_url = request.build_absolute_uri(my_books_url)
            email_context['full_url'] = full_url

            if book_request.delivery == 'I':
                # If Bulb coordinator failed to comminicate with the
                # owner, make the book available again and email both
                # the owner and the requester that the request has
                # been canceled.
                book.is_available = True
                book_request.status = 'C'
                # Return the point to the book requester
                book_request.cancel_related_user_point(book.submitter)
                mail.send([book_request.requester.email],
                          cc=cc_coordinator,
                          template="indirect_book_request_failed_to_requester",
                          context=email_context)
                if not book.is_publicly_owned:
                    mail.send([book.submitter.email],
                              cc=cc_coordinator,
                              template="indirect_book_request_failed_to_owner",
                              context=email_context)
            elif book_request.delivery == 'D':
                # Just to make sure
                book.is_available = False
                mail.send([book.submitter.email],
                          cc=cc_coordinator,
                          template="book_request_failed_to_owner",
                          context=email_context)

        elif action == 'requester_canceled' and previous_requester_status != 'C':
            # You cannot delete a request after it has been approved
            # by the requester.
            if book_request.requester_status == 'D':
                raise Exception(u'لا يمكنك إلغاء طلب منجز.')

            book.is_available = True
            book_request.requester_status = 'C'
            book_request.requester_status_date = timezone.now()

            # If one party canceled the request (in this case: the
            # book requester), and ther other hasn't confirmed it,
            # that's enough to consider the whole request canceled.
            # Otherwise, it will be handled in the conflicts section.
            if book_request.owner_status != 'D':
                book_request.status = 'C'

            # Return the point to the book requester
            book_request.cancel_related_user_point(request.user)

            if not book.is_publicly_owned:
                mail.send([book.submitter.email],
                          template="book_request_canceled_to_owner",
                          context=email_context)

            # Also, email Bulb coordinator.
            if book_request.delivery == 'I' and book_exchange_coordinator:
                cc = utils.get_indirect_request_cc(book)
                mail.send([book_exchange_coordinator.email],
                          cc=cc,
                          template="indirect_book_request_canceled_to_coordinator",
                          context=email_context)

    book.save()
    book_request.save()
    return {"message": "success"}

@login_required
def student_report(request, username=None):
    if username and \
       not request.user.is_superuser and\
       not utils.is_bulb_coordinator_or_deputy(request.user):
        raise PermissionDenied

    if username:
        bulb_user = get_object_or_404(User, username=username)
    else:
        bulb_user = request.user

    return render(request, 'bulb/exchange/student_report.html',
                  {'bulb_user': bulb_user})

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def convert_balance(request):
    try:
        giving = int(request.POST.get('giving'))
    except ValueError:
        raise Exception(u"أدخل رقما!")

    if giving > request.user.book_points.count_total_giving():
        raise Exception(u"لا تستطيع تحويل أكثر مما تملك من رصيد اقتناء")

    # Start converting the last, counted, positive-one point.
    for giving_point in request.user.book_points.current_year().giving().counted().filter(value=1).order_by("-submission_date")[:giving]:
        giving_point.value = 2
        giving_point.category = 'L'
        giving_point.save()

    return {"message": "success",
            "total_lending": request.user.book_points.count_total_lending(),
            "total_giving": request.user.book_points.count_total_giving()}

# Reading Groups

@login_required
def list_groups(request, archived=False):
    context = {'archived': archived}
    return render(request, 'bulb/groups/list_groups.html', context)

@login_required
def list_sessions(request):
    sessions = Session.objects.current_year().undeleted().public()
    context = {'sessions': sessions}
    return render(request, 'bulb/groups/list_sessions.html', context)

@decorators.ajax_only
@csrf.csrf_exempt
@login_required
def list_group_previews(request, archived=False):
    if archived:
        groups = Group.objects.current_year().undeleted().archived().for_user_city(request.user).order_by('?')
    else:
        groups = Group.objects.current_year().undeleted().unarchived().for_user_city(request.user).order_by('?')

    context = {'groups': groups, 'archived': archived}
    return render(request, "bulb/groups/list_group_previews.html",
                  context)

@decorators.ajax_only
@login_required
def add_group(request):
    if request.method == 'POST':
        current_year = StudentClubYear.objects.get_current()
        instance = Group(coordinator=request.user,
                         year=current_year)
        form = GroupForm(request.POST, request.FILES, instance=instance, user=request.user)
        if form.is_valid():
            group = form.save()
            show_group_url = reverse('bulb:show_group', args=(group.pk,))
            full_url = request.build_absolute_uri(show_group_url)
            utils.create_tweet(request.user, 'add_group', (group.name, full_url))
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = GroupForm(user=request.user)

    context = {'form': form}
    return render(request, 'bulb/groups/edit_group_form.html', context)

@decorators.ajax_only
@login_required
def edit_group(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)

    if not utils.can_edit_group(request.user, group):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    context = {'group': group}
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group, user=request.user)
        if form.is_valid():
            group = form.save()
            show_group_url = reverse('bulb:show_group', args=(group.pk,))
            full_url = request.build_absolute_uri(show_group_url)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = GroupForm(instance=group, user=request.user)

    context['form'] = form
    return render(request, 'bulb/groups/edit_group_form.html', context)

@login_required
def show_group(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk, is_deleted=False)
    context = {'group': group,
               'sessions': group.session_set.order_by("date")}
    return render(request, "bulb/groups/show_group.html", context)

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def delete_group(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk, is_deleted=False)
    if not utils.can_edit_group(request.user, group):
        raise Exception(u"لا تستطيع حذف المجموعة")

    group.is_deleted = True
    group.save()
    list_url = reverse('bulb:list_groups')
    full_url = request.build_absolute_uri(list_url)
    return {"message": "success", "list_url": full_url}

@login_required
def list_memberships(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk, is_deleted=False)

    if not utils.can_edit_group(request.user, group):
        raise PermissionDenied

    return render(request, "bulb/groups/list_memberships.html",
                  {'group': group})

@decorators.ajax_only
@login_required
def add_group_session(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk, is_deleted=False)
    if not utils.can_edit_group(request.user, group):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    if request.method == 'POST':
        instance = Session(group=group, submitter=request.user)
        form = SessionForm(request.POST, instance=instance)
        if form.is_valid():
            session = form.save()
            show_group_url = reverse('bulb:show_group', args=(group.pk,))
            full_url = request.build_absolute_uri(show_group_url)
            utils.create_tweet(request.user, 'add_session', (session.title, full_url))
            create_tweet_by_access("bulb", u"أعلنت مجموعة {} عن جلسة بعنوان {}! للتفاصيل: {}\n#مبادرة_سِراج".format(group.name, session.title, full_url))
            email_context = {'session': session, 'full_url': full_url}
            if session.date >= timezone.now().date():
                # If the coordinator is not already a group member, email
                # them as well.
                bulb_coordinator = utils.get_bulb_club_for_user(session.group.coordinator).coordinator
                for membership in group.membership_set.filter(is_active=True):
                    # Bulb coordinator will be handled later.
                    if bulb_coordinator == membership.user:
                        continue
                    email_context['member'] = membership.user
                    mail.send([membership.user.email],
                               template="reading_group_session_just_submitted",
                               context=email_context)
                # Notify coordinators
                email_context['member'] = group.coordinator
                mail.send([group.coordinator.email],
                           template="reading_group_session_just_submitted",
                           context=email_context)

                # Notify Bulb coordinator and their deputies.
                email_context['member'] = bulb_coordinator
                cc = utils.get_session_submitted_cc(session)
                mail.send([bulb_coordinator.email],
                          cc=cc,
                          template="reading_group_session_just_submitted",
                          context=email_context)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = SessionForm()

    context = {'form': form, 'group': group}
    return render(request, 'bulb/groups/edit_session_form.html', context)

@decorators.ajax_only
@login_required
def add_free_session(request):
    if request.method == 'POST':
        current_year = StudentClubYear.objects.get_current()
        instance = Session(submitter=request.user, year=current_year)
        form = FreeSessionForm(request.POST, instance=instance, user=request.user)
        if form.is_valid():
            session = form.save()
            show_session_url = reverse('bulb:show_session', args=(session.pk,))
            full_url = request.build_absolute_uri(show_session_url)
            utils.create_tweet(request.user, 'add_session', (session.title, full_url))
            create_tweet_by_access("bulb", u"أُعلن عن جلسة حرّة بعنوان {}! للتفاصيل: {}\n#مبادرة_سِراج".format(session.title, full_url))
            email_context = {'session': session, 'full_url': full_url}
            if session.date >= timezone.now().date():
                bulb_coordinator = utils.get_bulb_club_for_user(session.submitter).coordinator
                email_context['member'] = bulb_coordinator
                cc = utils.get_session_submitted_cc(session)
                mail.send([bulb_coordinator.email],
                          cc=cc,
                          template="free_session_just_submitted",
                          context=email_context)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = FreeSessionForm(user=request.user)

    context = {'form': form}
    return render(request, 'bulb/groups/edit_session_form.html', context)

@decorators.ajax_only
@login_required
def edit_session(request, session_pk, group_pk=None):
    session = get_object_or_404(Session, pk=session_pk,
                                is_deleted=False)
    context = {'session': session}
    if group_pk:
        group = get_object_or_404(Group, pk=group_pk, is_deleted=False)
        context['group'] = group

    if not utils.can_edit_session(request.user, session):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    response = {"message": "success"}

    if request.method == 'POST':
        if group_pk:
            form = SessionForm(request.POST, instance=session)
            show_url = reverse('bulb:show_group', args=(group.pk,))
        else:
            form = FreeSessionForm(request.POST, instance=session, user=request.user)
            show_url = reverse('bulb:show_session', args=(session.pk,))
        if form.is_valid():
            session = form.save()
            full_url = request.build_absolute_uri(show_url)
            response['show_url'] = full_url
            return response
    elif request.method == 'GET':
        if group_pk:
            form = SessionForm(instance=session)
        else:
            form = FreeSessionForm(instance=session, user=request.user)

    context['form'] = form
    return render(request, 'bulb/groups/edit_session_form.html', context)

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def delete_session(request, session_pk, group_pk=None):
    session = get_object_or_404(Session, pk=session_pk,
                                is_deleted=False)
    if not utils.can_edit_session(request.user, session):
        raise Exception(u"لا تستطيع حذف المجموعة")

    session.is_deleted = True
    session.save()
    if session.group:
        after_url = reverse('bulb:show_group', args=(session.group.pk,))
    else:
        after_url = reverse('bulb:list_sessions')
    full_url = request.build_absolute_uri(after_url)

    return {"message": "success", "show_url": full_url}

def show_session(request, session_pk):
    session = get_object_or_404(Session, pk=session_pk,
                                is_deleted=False, group=None)
    return render(request, "bulb/groups/show_session.html",
                  {'session': session})

def show_report(request, group_pk, session_pk):
    report = get_object_or_404(Report, session__group__pk=group_pk,
                               session__pk=session_pk)
    return render(request, "bulb/groups/show_report.html",
                  {'report': report})

@decorators.ajax_only
@login_required
def add_report(request, session_pk, group_pk=None):
    session = get_object_or_404(Session, pk=session_pk)

    if not utils.can_edit_session(request.user, session):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    response = {"message": "success"}

    if request.method == 'POST':
        instance = Report(session=session)
        form = ReportForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            report = form.save()
            report.create_related_niqati_codes()
            if group_pk:
                show_report_url = reverse('bulb:show_report', args=(session.group.pk, session.pk))
            else:
                show_report_url = reverse('bulb:show_report', args=(session.pk,))
            full_url = request.build_absolute_uri(show_report_url)
            response['show_url'] = full_url
            return response
    elif request.method == 'GET':
        form = ReportForm()

    context = {'form': form, 'session': session}
    return render(request, 'bulb/groups/edit_report_form.html', context)

@decorators.ajax_only
@login_required
def edit_report(request, session_pk, group_pk=None):
    report = get_object_or_404(Report, session__pk=session_pk)
    if not utils.can_edit_session(request.user, report.session):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    response = {"message": "success"}
    context = {'report': report}
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save()
            if group_pk:
                show_report_url = reverse('bulb:show_report', args=(report.session.group.pk, report.session.pk))
            else:
                show_report_url = reverse('bulb:show_report', args=(report.session.pk,))
            full_url = request.build_absolute_uri(show_report_url)
            response['show_url'] = full_url
            return response
    elif request.method == 'GET':
        form = ReportForm(instance=report)

    context['form'] = form
    return render(request, 'bulb/groups/edit_report_form.html', context)

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def toggle_session_confirmation(request):
    action = request.POST.get('action')
    session_pk = request.POST.get('session_pk')
    session = get_object_or_404(Session, pk=session_pk)
    show_url = reverse('bulb:show_session', args=(session.pk,))
    full_url = request.build_absolute_uri(show_url)

    response = {"message": "success", 'show_url': full_url}
    if action == 'attend':
        # Make sure that the user can indeed be added to the group
        if not utils.can_attend_session(request.user, session):
            raise Exception(u"لا تستطيع حضور هذه الجلسة.")
        session.confirmed_attendees.add(request.user)
        # Notify session submitter
        email_context = {'attendee': request.user,
                         'session': session,
                         'full_url': full_url}
        mail.send([session.submitter.email],
                   template="new_attendee_to_session_submitter",
                   context=email_context)

    elif action == 'cancel':
        # Make sure that the user can indeed be added to the group
        if not session.confirmed_attendees.filter(pk=request.user.pk).exists():
            raise Exception("لا تستطيع مغادرة هذه المجموعة.")
        session.confirmed_attendees.remove(request.user)
    return response

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def control_group(request):
    action = request.POST.get('action')
    group_pk = request.POST.get('group_pk')
    group = get_object_or_404(Group, pk=group_pk)
    user_pk = request.POST.get('user_pk')
    show_group_url = reverse('bulb:show_group', args=(group.pk,))
    full_show_url = request.build_absolute_uri(show_group_url)
    if user_pk:
        user = get_object_or_404(User, pk=user_pk)

    response = {"message": "success"}

    if action in ['deactivate', 'activate', 'archive', 'unarchive']:
        if not utils.can_edit_group(request.user, group):
            raise Exception("You are not allowed to perform this action.")

        if action == 'deactivate':
            Membership.objects.filter(group=group, user=user).update(is_active=False)
        elif action == 'activate':
            Membership.objects.filter(group=group, user=user).update(is_active=True)
        elif action == 'archive':
            group.is_archived = True
            group.save()
            # Notify group coordinator if they were not the one who
            # archived it.
            if request.user != group.coordinator:
                email_context = {'group': group,
                                 'full_url': full_url}
                mail.send([group.coordinator.email],
                           template="group_archived_to_group_coordinator",
                           context=email_context)
        elif action == 'unarchive':
            group.is_archived = False
            group.save()

    elif action == 'join':
        # Make sure that the user can indeed be added to the group
        if not utils.can_join_group(request.user, group):
            raise Exception(u"لا تستطيع الانضمام لهذه المجموعة.")
        Membership.objects.create(group=group, user=request.user,
                                  is_active=not group.is_private)

        # Notify group coordinator
        list_memberships_url = reverse('bulb:list_memberships', args=(group.pk,))
        full_list_memberships_url = request.build_absolute_uri(list_memberships_url)
        email_context = {'member': request.user,
                         'group': group,
                         'full_url': full_list_memberships_url}
        mail.send([group.coordinator.email],
                   template="new_reading_group_member_to_group_coordinator",
                   context=email_context)
        utils.create_tweet(request.user, 'join_group', (group.name, full_show_url))

    elif action == 'leave':
        # Make sure that the user can indeed be added to the group
        if not Membership.objects.filter(group=group, user=request.user).exists():
            raise Exception("لا تستطيع مغادرة هذه المجموعة.")
        Membership.objects.get(group=group, user=request.user).delete()


    response['show_url'] = full_show_url

    return response

@decorators.ajax_only
@login_required
@csrf.csrf_exempt
def new_member_introduction(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk)
    return render(request, 'bulb/groups/new_member_introduction.html',
                  {'group': group})

# Readers

@login_required
def list_reader_profiles(request):
    reader_profiles = ReaderProfile.objects.all()
    return render(request, 'bulb/readers/list_reader_profiles.html',
                  {'reader_profiles': reader_profiles})

@login_required
def show_reader_profile(request, reader_pk):
    reader_profile = get_object_or_404(ReaderProfile, pk=reader_pk)
    group_coordination = Group.objects.current_year().undeleted().filter(coordinator=reader_profile.user)
    group_membership_pks = Membership.objects.current_year().active().filter(user=reader_profile.user).values_list('group__pk', flat=True)
    group_memberships = Group.objects.current_year().undeleted().filter(pk__in=group_membership_pks)
    return render(request, 'bulb/readers/show_reader_profile.html',
                  {'reader_profile': reader_profile,
                   'group_coordination': group_coordination,
                   'group_memberships': group_memberships})

@decorators.ajax_only
@login_required
def add_reader_profile(request):
    if request.method == 'POST':
        instance = ReaderProfile(user=request.user)
        form = ReaderProfileForm(request.POST, instance=instance)
        if form.is_valid():
            reader_profile = form.save()
            show_reader_profile_url = reverse('bulb:show_reader_profile', args=(reader_profile.pk,))
            full_url = request.build_absolute_uri(show_reader_profile_url)
            utils.create_tweet(request.user, 'add_reader', (full_url,))
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = ReaderProfileForm()

    context = {'form': form}
    return render(request, 'bulb/readers/edit_reader_profile_form.html', context)

@decorators.ajax_only
@login_required
def edit_reader_profile(request, reader_pk):
    reader_profile = get_object_or_404(ReaderProfile, pk=reader_pk)

    if not utils.can_edit_reader_profile(request.user, reader_profile):
        raise Exception(u"لا تستطيع تعديل المجموعة")

    context = {'reader_profile': reader_profile}
    if request.method == 'POST':
        form = ReaderProfileForm(request.POST, instance=reader_profile)
        if form.is_valid():
            form.save()
            show_reader_profile_url = reverse('bulb:show_reader_profile', args=(reader_profile.pk,))
            full_url = request.build_absolute_uri(show_reader_profile_url)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = ReaderProfileForm(instance=reader_profile)

    context['form'] = form
    return render(request, 'bulb/readers/edit_reader_profile_form.html', context)

@login_required
def handle_recruitment(request):
    if request.method == 'POST':
        current_year = StudentClubYear.objects.get_current()
        recruitment = Recruitment(user=request.user, year=current_year)
        form = RecruitmentForm(request.POST, request.FILES, instance=recruitment)
        if form.is_valid():
            recruitment = form.save()
            return HttpResponseRedirect(reverse('bulb:recruitment_thanks'))
    else:
        form = RecruitmentForm()
    context = {'form': form}
    return render(request, 'bulb/recruitment.html', context)

@decorators.post_only
@decorators.ajax_only
@csrf.csrf_exempt
def handle_newspaper_signup(request):
    if request.user.is_authenticated():
        previous_signup = NewspaperSignup.objects.filter(user=request.user).exists()
        if previous_signup:
            raise Exception("previous")
        else:
            NewspaperSignup.objects.create(user=request.user)
    else:
        form = NewspaperSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            previous_signup = NewspaperSignup.objects.filter(email=email).exists()
            if previous_signup:
                raise Exception("previous")
            else:
                form.save()
        else:
            raise Exception("invalid")
    return {}

@decorators.get_only
@decorators.ajax_only
def update_newspaper_count(request):
    newspaper_count = NewspaperSignup.objects.count()
    return {'newspaper_count': newspaper_count}


class BulbUserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return User.objects.none()

        qs = User.objects.filter(common_profile__profile_type='S', is_active=True)

        if self.q:
            search_fields = [re.sub('^user__', '', field) for field in core.utils.BASIC_SEARCH_FIELDS]
            qs = get_search_queryset(qs, search_fields, self.q)

        return qs

    def get_result_label(self, item):
        return"%s (<span class=\"english-field\">%s</span>)" % (item.common_profile.get_ar_full_name(), item.username)

class BulbBookAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Book.objects.none()

        qs = Book.objects.available()

        if self.q:
            search_fields=['title', 'authors']
            qs = get_search_queryset(qs, search_fields, self.q)

        return qs

    def get_result_label(self, item):
        try:
            name = item.submitter.common_profile.ar_first_name + " " + item.submitter.common_profile.ar_last_name
        except ObjectDoesNotExist:
            name = item.submitter.username

        return u"%s من %s" % (item.title, name)

class BulbRecommendedBookAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return RecommendedBook.objects.none()

        qs = RecommendedBook.objects.all()

        if self.q:
            search_fields=['title', 'authors']
            qs = get_search_queryset(qs, search_fields, self.q)

        return qs

    def get_result_label(self, item):
        return u"<img class='cover-thumbnail' src='%s'>%s تأليف %s" % (item.cover.url, item.title, item.authors)

def autocomplete_users(request):
    term = request.GET.get('term')
    if not term:
        raise Http404

    qs = User.objects.filter(common_profile__is_student=True)
    search_fields=['common_profile__ar_first_name',
                   'common_profile__ar_middle_name',
                   'common_profile__ar_last_name',
                   'common_profile__en_first_name',
                   'common_profile__en_middle_name',
                   'common_profile__en_last_name']

    result_query = get_search_queryset(qs, search_fields, term)
    result_list = [r.common_profile.get_ar_full_name() for r in result_query]
    return HttpResponse(json.dumps(result_list))

def handle_dewanya_suggestions(request):
    if request.method == 'POST':
        formset = DewanyaSuggestionFormSet(request.POST)
        if formset.is_valid():
            recruitment = form.save()
            return HttpResponseRedirect(reverse('bulb:recruitment_thanks'))
    else:
        formset = DewanyaSuggestionFormSet()
    context = {'formset': formset}
    return render(request, 'bulb/recruitment_dewanya.html', context)

def show_readathon(request, pk):
    readathon = get_object_or_404(Readathon, pk=pk)
    context = {'readathon': readathon}

    if readathon.publication_date and \
       readathon.publication_date > timezone.now():
        raise Http404

    if request.user.is_authenticated():
        user_books = readathon.bookcommitment_set.filter(user__pk=request.user.pk, is_deleted=False)
        context['user_books'] = user_books

    return render(request, readathon.template_name, context)

@decorators.ajax_only
@login_required
def add_book_commitment(request, readathon_pk):
    readathon = get_object_or_404(Readathon, pk=readathon_pk)
    if request.method == 'POST':
        instance = BookCommitment(user=request.user,
                                  readathon=readathon)
        form = BookCommitmentForm(request.POST, request.FILES, instance=instance, readathon=readathon)
        if form.is_valid():
            book_commitment = form.save()
            show_url = reverse('bulb:show_readathon', args=(readathon.pk,))
            full_url = request.build_absolute_uri(show_url)
            utils.create_tweet(request.user, 'add_book_commitment', (book_commitment.title, full_url), media_path=book_commitment.cover.path)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = BookCommitmentForm(readathon=readathon)

    context = {'form': form, 'readathon': readathon}
    return render(request, 'bulb/readathon/edit_book_commitment_form.html', context)

@decorators.ajax_only
@login_required
def edit_book_commitment(request, readathon_pk, pk):
    book_commitment = get_object_or_404(BookCommitment, pk=pk,
                                        is_deleted=False)

    if not utils.can_edit_book_commitment(request.user, book_commitment):
        raise Exception(u"لا تستطيع تعديل الكتاب")

    context = {'book_commitment': book_commitment}
    if request.method == 'POST':
        form = BookCommitmentForm(request.POST, request.FILES, instance=book_commitment, readathon=readathon)
        if form.is_valid():
            book_commitment = form.save()
            show_url = reverse('bulb:show_readathon', args=(book_commitment.readathon.pk,))
            full_url = request.build_absolute_uri(show_url)
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = BookCommitmentForm(instance=book_commitment, readathon=readathon)

    context['form'] = form
    return render(request, 'bulb/readathon/edit_book_commitment_form.html', context)

@decorators.ajax_only
@decorators.post_only
@csrf.csrf_exempt
@login_required
def delete_book_commitment(request, readathon_pk, pk):
    book_commitment = get_object_or_404(BookCommitment, pk=pk,
                                        is_deleted=False)

    if not utils.can_edit_book_commitment(request.user, book_commitment):
        raise Exception(u"لا تستطيع تعديل الكتاب")

    book_commitment.is_deleted = True
    book_commitment.save()
    show_url = reverse('bulb:show_readathon', args=(book_commitment.readathon.pk,))
    full_url = request.build_absolute_uri(show_url)
    return {"message": "success", "show_url": full_url}

@decorators.ajax_only
@login_required
def update_book_commitment(request, readathon_pk, pk):
    book_commitment = get_object_or_404(BookCommitment, pk=pk,
                                        is_deleted=False)

    if not utils.can_edit_book_commitment(request.user, book_commitment):
        raise Exception(u"لا تستطيع تعديل الكتاب")

    context = {'book_commitment': book_commitment}
    if request.method == 'POST':
        form = UpdateBookCommitmentForm(request.POST, instance=book_commitment)
        if form.is_valid():
            book_commitment = form.save()
            show_url = reverse('bulb:show_readathon', args=(book_commitment.readathon.pk,))
            full_url = request.build_absolute_uri(show_url)
            utils.create_tweet(request.user, 'update_book_commitment', (book_commitment.get_progress_percentage(), book_commitment.title, full_url))
            return {"message": "success", "show_url": full_url}
    elif request.method == 'GET':
        form = UpdateBookCommitmentForm(instance=book_commitment)

    context['form'] = form
    return render(request, 'bulb/readathon/update_book_commitment_form.html', context)

@decorators.ajax_only
@login_required
def readathon_products(request, readathon_pk, pk):
    readathon_products = get_object_or_404(ReadathonProducts, pk=pk,
                                            is_deleted=False)
    context = {'readathon_products': readathon_products}

    return render(request, 'bulb/readathon/products.html', context)

@login_required
def handle_cultural_program(request):
    form = CulturalProgramForm()
    context = {'form':form}
    return render(request, 'bulb/cultural_program.html', context)

@decorators.ajax_only
@decorators.post_only
@csrf.csrf_exempt
@login_required
def handle_cultural_program_ajax(request):
    form = CulturalProgramForm(request.POST)
    current_year = StudentClubYear.objects.get_current()
    balance = request.user.book_points.count_total_lending()
    if form.is_valid():
        user = form.cleaned_data['user']
        book = form.cleaned_data['book']
        if book.is_available == False:
            raise Exception(u"سبق وطلب الكتاب")
        if balance < 0:
            raise Exception(u"لا يوجد لديك نقاط استعارة")
        book_request = Request.objects.create(book=book,
                                        requester=user,
                                        delivery='D',
                                        status='D',
                                        requester_status='D',
                                        owner_status='D',
                                        owner_status_date=timezone.now(),
                                        requester_status_date=timezone.now(),
                                        borrowing_end_date=timezone.now() + timezone.timedelta(days=21))
        Point.objects.create(year=current_year,
                             category='L',
                             request=book_request,
                             user=user,
                             value=-1)
        book_request.save()
        book.is_available = False
        book.save
    else:
        raise Exception(u"لم يعبآ النموذج بشكل صحيح ")

def show_recommendation_index(request):
    categories = Category.objects.distinct().filter(recommendedbook__bookrecommendation__isnull=False)
    top_users = User.objects.annotate(recommendations=Count('bookrecommendation'))\
                            .filter(recommendations__gte=1)\
                            .order_by('-recommendations')[:10]
    top_books = RecommendedBook.objects.annotate(recommendations=Count('bookrecommendation'))\
                                       .filter(recommendations__gte=1)\
                                       .order_by('-recommendations')[:10]
    context = {'categories': categories,
               'top_books': top_books,
               'top_users': top_users}
    if request.user.is_authenticated():
        user_recommendations = BookRecommendation.objects.filter(user=request.user, is_deleted=False)
        context['user_recommendations'] = user_recommendations

    return render(request, 'bulb/recommendations/show_index.html', context)

def show_user_recommendations(request, pk):
    recommendation_user = get_object_or_404(User, pk=pk)
    context = {'recommendation_user': recommendation_user}
    return render(request, 'bulb/recommendations/show_user.html', context)

@decorators.ajax_only
@login_required
def add_book_recommendation(request):
    if request.method == 'POST':
        form = AddBookRecommendationForm(request.POST, request.FILES)
        if form.is_valid():
            book_recommendation = form.save(request.user)
            relative_url = reverse('bulb:show_user_recommendations', args=(request.user.pk,))
            # Only tweet with the first book added.
            if request.user.bookrecommendation_set.count() == 1:
                full_url = request.build_absolute_uri(relative_url)
                utils.create_tweet(request.user, 'add_book_recommendation', (full_url,))
            return {"message": "success", 'show_url': relative_url}
    elif request.method == 'GET':
        form = AddBookRecommendationForm()

    context = {'form': form}
    return render(request, 'bulb/recommendations/edit_book_recommendation_form.html', context)

@decorators.ajax_only
@login_required
def edit_book_recommendation(request, pk):
    book_recommendation = get_object_or_404(BookRecommendation, pk=pk,
                                            is_deleted=False)
    if request.method == 'POST':
        form = EditBookRecommendationForm(request.POST, instance=book_recommendation)
        if form.is_valid():
            form.save()
            return {"message": "success"}
    elif request.method == 'GET':
        form = EditBookRecommendationForm(instance=book_recommendation)

    context = {'form': form, 'book_recommendation': book_recommendation}
    return render(request, 'bulb/recommendations/edit_book_recommendation_form.html', context)

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def duplicate_book_recommendation(request, pk):
    book_recommendation = get_object_or_404(BookRecommendation, pk=pk,
                                            is_deleted=False)
    if BookRecommendation.objects.filter(recommended_book=book_recommendation.recommended_book,
                                         user=request.user).exists():
        raise Exception(u"سبق أن زكّيت هذا الكتاب")
    BookRecommendation.objects.create(recommended_book=book_recommendation.recommended_book,
                                      user=request.user)
    list_url = reverse('bulb:show_needed_category', args=(needed_book.category.code_name,))
    full_url = request.build_absolute_uri(list_url)
    return {"message": "success", "list_url": full_url}

@decorators.ajax_only
@decorators.post_only
@login_required
@csrf.csrf_exempt
def delete_book_recommendation(request, pk):
    book_recommendation = get_object_or_404(BookRecommendation, pk=pk,
                                            is_deleted=False)
    if not utils.can_edit_book_recommendation(request.user, book_recommendation):
        raise Exception(u"لا تستطيع حذف هذه التزكية")

    book_recommendation.is_deleted = True
    book_recommendation.save()
    list_url = reverse('bulb:show_needed_category', args=(needed_book.category.code_name,))
    full_url = request.build_absolute_uri(list_url)
    return {"message": "success", "list_url": full_url}

def show_recommendation_category(request, code_name):
    category = get_object_or_404(Category, code_name=code_name)
    context = {'category': category}
    return render(request, "bulb/recommendations/show_category.html", context)

def show_recommended_book(request, pk):
    recommended_book = get_object_or_404(RecommendedBook, pk=pk)
    context = {'recommended_book': recommended_book}
    return render(request, "bulb/recommendations/show_recommended_book.html", context)
