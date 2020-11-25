import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, get_user, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models.functions import Lower
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from opinioxx.base.forms import IdeaForm, ProjectForm, CustomUserCreationForm, CommentForm, \
    CustomPasswordChangeForm, EmailSettingsForm, VoteForm
from opinioxx.base.models import Idea, Vote, User, Favorite, Project, Comment, GlobalSettings
from opinioxx.base.signals import access_allowed_ideas


def index(request):
    """ index-view to display available projects """
    user = get_user(request)
    context = {
        'new_project_allowed': (settings.ALLOW_NEW_PROJECTS and not user.is_anonymous) or request.user.is_superuser,
        'projects': User.get_projects(user),
    }
    return render(request, 'base/index.html', context)


def register(request):
    """ view to register a new user """
    if User.objects.count() > 0 and not settings.ALLOW_USER_REGISTRATION:
        raise PermissionDenied
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if User.objects.count() == 1:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            return HttpResponseRedirect(reverse('base:login'))
    return render(request, 'registration/register.html', {'form': form})


def profile(request):
    """ view to display the profile page """
    user = get_user(request)
    if user.is_anonymous:
        raise PermissionDenied
    tab = request.GET.get('tab', 'password')
    form_passwordchange = CustomPasswordChangeForm(request.user)
    form_emailsettings = EmailSettingsForm(request.user, instance=request.user)
    return render(request, 'base/profile.html', {
        'form_passwordchange': form_passwordchange,
        'form_emailsettings': form_emailsettings,
        'tab': tab,
    })


def profile_changepassword(request):
    """ view to change the password on the profile page """
    user = get_user(request)
    if user.is_anonymous:
        raise PermissionDenied
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Dein Passwort wurde erfolgreich gespeichert!')
        else:
            messages.error(request,
                           'Dein Passwort konnte nicht gespeichert werden. Bitte behebe die untenstehenden Fehler.')
    response = redirect('base:profile')
    response['Location'] += '?tab=password'
    return response


def profile_emailsettings(request):
    """ view to change the email settings on the profile page """
    user = get_user(request)
    if user.is_anonymous:
        raise PermissionDenied
    if request.method == 'POST':
        form = EmailSettingsForm(request.user, request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deine Einstellungen wurden erfolgreich gespeichert!')
        else:
            messages.error(request, 'Deine Einstellungen konnten nicht erfolgreich gespeichert werden')
    response = redirect('base:profile')
    response['Location'] += '?tab=email'
    return response


def newproject(request, project_id=None):
    """ view to create a new project or edit an existing one """
    user = get_user(request)
    if project_id:
        if user.is_anonymous or not Project.objects.filter(id=project_id,
                                                           admins__id=user.id).exists() and not user.is_superuser:
            raise PermissionDenied
        project = get_object_or_404(Project, id=project_id)
        form = ProjectForm(instance=project)
        form.fields['anonymous_votes'].disabled = True
        context = {
            'form': form,
            'title': 'Projekt editieren',
            'success': False,
            'edit': True,
        }
        if request.method == 'POST':
            form = ProjectForm(request.POST, instance=project)
            if 'delete' in request.POST:
                project.delete()
                return HttpResponseRedirect(reverse('base:index'))
            elif form.is_valid():
                p = form.save()
                p.add_notifications()
                context['success'] = True
        return render(request, 'base/newproject.html', context)
    else:
        if (not settings.ALLOW_NEW_PROJECTS or user.is_anonymous) and not request.user.is_superuser:
            raise PermissionDenied
        context = {
            'form': ProjectForm(),
            'title': 'Neues Projekt anlegen',
            'success': False,
            'edit': False,
        }
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            if form.is_valid():
                p = form.save()
                p.add_notifications()
                context['success'] = True
        return render(request, 'base/newproject.html', context)


def cron(request):
    """ view to handle recurring tasks via curl requests """
    globalsettings = GlobalSettings.objects.get_or_create(id=1)[0]
    # send daily notifications
    if globalsettings.last_cron_run < datetime.date.today():
        for user in User.objects.filter(notify_interval=1).all():
            user.send_notification()
    # send weekly notifications
    if globalsettings.last_cron_run.weekday() + (datetime.date.today() - globalsettings.last_cron_run).days > 7:
        for user in User.objects.filter(notify_interval=7).all():
            user.send_notification()
    # send monthly notifications
    if datetime.date.today().day == 1 and globalsettings.last_cron_run.month != datetime.date.today().month:
        for user in User.objects.filter(notify_interval=30).all():
            user.send_notification()
    globalsettings.last_cron_run = datetime.date.today()
    globalsettings.save()
    return HttpResponse('OK')


def newidea(request, project_id):
    """ view to store a new idea for a given project """
    user = get_user(request)
    project = get_object_or_404(Project, id=project_id)
    if not project.access_allowed(user):
        raise PermissionDenied
    context = {
        'form': IdeaForm(),
        'new_feedback_text': project.new_idea_description,
        'success': False,
        'project': project,
    }
    if request.method == 'POST':
        form = IdeaForm(request.POST)
        if form.is_valid():
            try:
                Idea.objects.get(title=form.cleaned_data['title'], project_id=project.id)
                messages.warning(request, 'Es existiert bereits ein Feedback mit identischem Titel!')
                context['form'] = IdeaForm(request.POST)
            except ObjectDoesNotExist:
                idea = Idea(title=form.cleaned_data['title'], description=form.cleaned_data['description'],
                            project=project)
                idea.save()
                if form.cleaned_data['upvote']:
                    # upvote the idea directly
                    if project.voting_allowed(user):
                        if user.is_anonymous:
                            if not 'idea_ids' in request.session:
                                request.session['idea_ids'] = []
                            request.session['idea_ids'].append(idea.id)
                            request.session.modified = True
                        else:
                            if project.anonymous_votes:
                                Vote(user=user, idea=idea).save()
                            else:
                                Vote(user=user, idea=idea, value=Vote.POSITIVE).save()
                    idea.save()
                context['success'] = True
    return render(request, 'base/newidea.html', context)


def project(request, project_id, archive=False, compact=False):
    """ project-view to show all associated ideas """
    user = get_user(request)
    project = get_object_or_404(Project, id=project_id)
    if not project.access_allowed(user):
        raise PermissionDenied
    request.session['compactview'] = compact
    request.session.modified = True
    if archive:
        ideas = project.idea_set.filter(state=Idea.SUCCESS).all() | project.idea_set.filter(state=Idea.REJECTED).all()
    else:
        ideas = project.idea_set.filter(state=Idea.OPEN).all()
    priority = 100
    for receiver, response in access_allowed_ideas.send(request, ideas=ideas, user=user, project=project):
        if response and response['priority'] and response['value'] and response['priority'] < priority:
            ideas = response['value']
            priority = response['priority']
    ideas = sorted(ideas, key=lambda x: -x.get_vote_value())  # sort ideas
    context = {
        'project': project,
        'user': user,
        'show_settings': user in project.admins.all(),
        'ideas': ideas,
        'archive': archive,
        'compact': compact,
        'view': 'project',
    }
    return render(request, 'base/project.html', context)


def vote(request, project_id):
    """ view to store a vote and redirect to project page """
    user = get_user(request)
    project = get_object_or_404(Project, id=project_id)
    idea = None
    if not project.access_allowed(user) or not project.voting_allowed(user):
        return JsonResponse({'error': 'Es ist ein unerwarteter Fehler aufgetreten! Die Seite wird neu geladen.'})
    if request.POST:
        vote_data = VoteForm(request.POST)
        if not vote_data.is_valid():
            return JsonResponse({'error': 'Es ist ein unerwarteter Fehler aufgetreten! Die Seite wird neu geladen.'})
        idea = get_object_or_404(Idea, pk=request.POST['idea'])
        if vote_data.cleaned_data['action'] == 'star' and not user.is_anonymous:
            # user clicked on star
            star_value = False
            try:
                star = Favorite.objects.get(user=request.user, idea=idea)
                star.delete()  # remove star
            except Favorite.DoesNotExist:
                # add star
                user_model = get_user_model()
                user = user_model.objects.get(id=request.user.id)
                if user.get_free_favorites(project.id) > 0:
                    Favorite(user=request.user, idea=idea).save()
                    star_value = True
            return JsonResponse({'idea': idea.id,
                                 'star': star_value,
                                 'stars_available': user.get_free_favorites(project.id) > 0,
                                 'rating_sum': idea.get_vote_value(),
                                 'voting_allowed': not user.is_anonymous,
                                 'participations': idea.get_vote_count(),
                                 'stars': idea.get_star_count(),
                                 })
        elif vote_data.cleaned_data['action'] == 'up':
            value = Vote.POSITIVE
        elif vote_data.cleaned_data['action'] == 'neutral':
            value = Vote.NEUTRAL
        elif vote_data.cleaned_data['action'] == 'down':
            value = Vote.NEGATIVE
        else:
            return JsonResponse({'error': 'Es ist ein unerwarteter Fehler aufgetreten! Die Seite wird neu geladen.'})
        if user.is_anonymous:
            if not 'idea_ids' in request.session:
                request.session['idea_ids'] = []
            if idea.id in request.session['idea_ids']:
                raise PermissionDenied
            request.session['idea_ids'].append(idea.id)
            request.session.modified = True
            Vote(idea=idea, value=value).save()
        else:
            try:
                vote = Vote.objects.get(user=request.user, idea=idea)
                vote.delete()
            except Vote.DoesNotExist:
                pass
            if project.anonymous_votes:
                Vote(idea=idea, value=value).save()
            else:
                Vote(user=request.user, idea=idea, value=value).save()
        if idea.get_vote_value() <= project.automatic_closing_limit:
            # automatically close idea
            idea.state = Idea.REJECTED
            idea.save()
            comment = Comment(
                content=f'Das Feedback wurde automatisch abgelehnt, da es {idea.get_vote_value()} Stimmen erhalten '
                        f'hat. Dieser Wert kann von dem Projekt-Administrator angepasst werden.',
                idea=idea,
                statechange=Comment.CLOSE
            )
            comment.save()
        star_new = True if not user.is_anonymous and idea.favorite_set.filter(user_id=user.id).exists() else False
    else:
        star_new = False
    return JsonResponse({'idea': idea.id if idea else 0,
                         'star': star_new,
                         'stars_available': user.get_free_favorites(project.id) > 0 if not user.is_anonymous else False,
                         'rating_sum': idea.get_vote_value(),
                         'voting_allowed': not user.is_anonymous,
                         'participations': idea.get_vote_count(),
                         'stars': idea.get_star_count(),
                         })


def idea(request, project_id, idea_id):
    """ detail view of an idea """
    user = get_user(request)
    project = get_object_or_404(Project, id=project_id)
    idea = get_object_or_404(Idea, pk=idea_id)
    if not project.access_allowed(user) or \
            (not project.public_visible and user.is_anonymous):
        raise PermissionDenied
    special_rights = False
    form = CommentForm(idea)
    plugin_users = project.get_special_users()
    if not user.is_anonymous and Project.objects.filter(id=project.id, admins=user).exists() \
            or user.is_superuser or user in plugin_users:
        special_rights = True
    if request.method == 'POST':
        if not project.public_voting and user.is_anonymous:
            raise PermissionDenied
        form = CommentForm(idea, request.POST)
        if form.is_valid():
            comment = Comment(
                content=form.cleaned_data['content'],
                author=user if not form.cleaned_data['anonymous'] and not user.is_anonymous else None,
                idea=idea,
            )
            if not form.cleaned_data['anonymous']:
                if form.cleaned_data['archive'].__contains__('success'):
                    idea.state = Idea.SUCCESS
                    comment.category = Comment.ACCEPT
                elif form.cleaned_data['archive'].__contains__('failure'):
                    idea.state = Idea.REJECTED
                    comment.category = Comment.CLOSE
                elif form.cleaned_data['archive'].__contains__('reopen'):
                    idea.state = Idea.OPEN
                    comment.category = Comment.REOPEN
                idea.save()
            comment.save()
            form = CommentForm(idea)
    if special_rights:
        form.fields['anonymous'].widget.attrs['checked'] = False
    context = {
        'project': project,
        'idea': idea,
        'form': form,
        'author': user.username if special_rights else 'Anonymous',
        'special_rights': special_rights,
        'comments': Comment.objects.filter(idea_id=idea.id).order_by('date', 'id'),
        'view': 'detail',
        'admins': project.get_special_users(),
        'archive': request.META['HTTP_REFERER'].endswith('archive') if 'HTTP_REFERER' in request.META else False,
    }
    return render(request, 'base/idea_detail.html', context=context)
