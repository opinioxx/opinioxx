from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.db.models.functions import Lower
from django.forms import ModelForm

from opinioxx.base.models import Idea, User, Project
from opinioxx.base.signals import form_project_init, form_project_save


class IdeaForm(ModelForm):
    """ Form to create new ideas """
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control, w-100',
                'placeholder': 'Titel',
            }
        )
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control, w-100',
                'placeholder': 'Beschreibung (optional)',
                'rows': 4
            }
        )
    )
    upvote = forms.BooleanField(
        required=False,
        label='unterstütze das Feedback beim Speichern direkt mit deiner Stimme'
    )

    class Meta:
        model = Idea
        fields = ['title', 'description']


class EmailSettingsForm(ModelForm):
    """ Form to change the e-mail notifications on the profile page """

    class Meta:
        model = User
        fields = ['notifiable_projects', 'add_new_projects_to_notify_list', 'notify_interval', 'notify_new_idea',
                  'notify_state_changed', 'notify_comments']
        labels = {
            'notifiable_projects': 'Benachrichtigungen für die folgenden Projekte senden',
            'notify_interval': 'Häufigkeit der Benachrichtigungen',
            'add_new_projects_to_notify_list': 'neue Projekte automatisch zu dieser Liste hinzufügen',
            'notify_new_feedback': 'über neues Feedback benachrichtigen',
            'notify_state_changed': 'über Statusänderungen (Feedback umgesetzt/abgelehnt) benachrichtigen',
            'notify_comments': 'über Kommentare benachrichtigen',
        }
        widgets = {
            'notifiable_projects': forms.SelectMultiple(attrs={
                'class': 'selectpicker form-input w-100 mb-3',
                'data-actions-box': 'true',
                'title': 'Bitte Projekte auswählen...',
            }),
            'notify_interval': forms.Select(attrs={'class': 'form-control w-100 mb-3'}),
        }

    def __init__(self, user, *args, **kwargs):
        """ prefills the form with the selectable projects """
        super().__init__(*args, **kwargs)
        self.fields['notifiable_projects'].queryset = User.get_projects(user)


class ProjectForm(ModelForm):
    """ Form to create or edit a project """
    name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control, w-100',
                'placeholder': 'Name des Projekts (max 50 Zeichen)'
            }
        )
    )
    description = forms.CharField(
        label='Beschreibung',
        max_length=500,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control, w-100',
                'rows': 3,
                'placeholder': 'Kurze Beschreibung des Projekts (max. 500 Zeichen)'
            }
        )
    )
    admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by(Lower('username')),
        label='Administratoren',
        help_text='Liste der Administratoren für dieses Projekt. Administratoren können diese '
                  'Einstellungsseite öffnen und das Projekt komplett verwalten.',
        widget=forms.SelectMultiple(
            attrs={
                'class': 'selectpicker flex-fill',
                'data-actions-box': 'true',
                'data-live-search': 'true',
                'title': 'Bitte Benutzer auswählen...',
            }
        )
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.order_by(Lower('username')),
        label='Benutzer',
        help_text='Liste der Benutzer für dieses Projekt. '
                  'Benutzer können Stimmen für das Feedback abgeben und alle Vorschläge einsehen.',
        widget=forms.SelectMultiple(
            attrs={
                'class': 'selectpicker flex-fill',
                'data-actions-box': 'true',
                'data-live-search': 'true',
                'title': 'Bitte Benutzer auswählen...',
            }
        )
    )
    public_visible = forms.BooleanField(
        label='öffentlich sichtbar',
        help_text='Soll dieses Projekt öffentlich sichtbar sein oder nur für die oben eingetragenen Benutzer?',
        required=False,
    )
    public_voting = forms.BooleanField(
        label='öffentliches Abstimmen erlaubt',
        help_text='Soll ein Abstimmen für alle möglich sein oder nur nach Anmeldung? Macht nur Sinn in Verbindung mit '
                  '"öffentlich sichtbar".',
        required=False,
    )
    public_comments = forms.BooleanField(
        label='öffentliches Kommentieren erlaubt',
        help_text='Soll ein Kommentieren für alle möglich sein oder nur nach Anmeldung? Macht nur Sinn in Verbindung '
                  'mit "öffentlich sichtbar".',
        required=False,
    )
    anonymous_votes = forms.BooleanField(
        label='vollständig anonym',
        help_text='Sollen die Abstimmungen vollständig anonym in der Datenbank gespeichert werden? Beim '
                  'nachträglichen Entfernen von Benutzern können deren Abstimmungen dann nicht mehr gelöscht werden! '
                  'Ebenfalls können abgegebene Stimmen nachträglich nicht mehr geändert werden! '
                  'ACHTUNG: Dieser Wert kann nachträglich nicht mehr geändert werden!',
        required=False,
    )
    automatic_closing_limit = forms.IntegerField(
        label='Feedback automatisch abgelehnt ab',
        help_text='Ab welcher Summe der Abstimmungsergebnisse soll das Feedback automatisch abgelehnt und ins Archiv '
                  'verschoben werden? Muss negativ sein.',
        max_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-input, w-100',
                'placeholder': 'Summe ab wann Feedback automatisch geschlossen wird',
            }
        )
    )
    new_idea_description = forms.CharField(
        label='Hinweistext für Feedback',
        help_text='Dieser Text wird den Benutzern beim Erstellen von neuem Feedback angezeigt (max 500 Zeichen).',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control, w-100',
                'rows': 3,
                'placeholder': 'Hinweistext beim Erstellen von neuem Feedback'
            }
        )
    )
    max_favorites = forms.IntegerField(
        label='Anzahl Favoriten pro Benutzer',
        help_text='Wie viele Favoriten-Sterne kann ein Benutzer maximal vergeben?',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-input, w-100',
                'placeholder': 'Anzahl der Favoriten-Sterne',
            }
        )
    )
    favorite_value = forms.FloatField(
        label='Stimmanzahl pro Favorit',
        help_text='Mit wie vielen Stimmen soll ein Favoriten-Stern zur Gesamtpunktzahl zählen? Beachte, dass die Summe '
                  'am Ende gerundet wird, ein Wert von 0,25 benötigt also mindestens 2 Sterne, um in der '
                  'Gesamtstimmenanzahl aufzutauchen.',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-input, w-100',
                'placeholder': 'Wert pro Favorit',
            }
        )
    )

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        elements = []
        for receiver, response in form_project_init.send(self, **kwargs):
            if response and isinstance(response, dict) and response['priority'] and response['value']:
                elements.append(response)
        for element in sorted(elements, key=lambda x: x['priority']):
            self.fields[element['name']] = element['value']

    def save(self, commit=True):
        project = super(ProjectForm, self).save()
        form_project_save.send(self, project=project)
        return project


class LoginForm(AuthenticationForm):
    """ Form to login into the application """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-input w-100 mt-2',
                   'placeholder': 'Benutzername',
                   }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100 mt-2',
                   'placeholder': 'Passwort',
                   }
        )
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """ Form to change the password on the profile page """
    old_password = forms.CharField(
        label='altes Passwort',
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100 mb-2',
                   'placeholder': 'sUp3rS1ch3R!',
                   }
        ),
    )
    new_password1 = forms.CharField(
        label='neues Passwort',
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100 mb-2',
                   'placeholder': 'sUp3rS1ch3R!',
                   }
        ),
    )
    new_password2 = forms.CharField(
        label='neues Passwort bestätigen',
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100 mb-2',
                   'placeholder': 'sUp3rS1ch3R!',
                   }
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    """ Form to create new users within the application """
    password1 = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100',
                   'placeholder': 'sUp3rS1ch3R!',
                   }
        ),
        help_text='Das Passwort darf nicht ähnlich zu deinen persönlichen Daten sein. Mindestens 8 Zeichen, '
                  'keine üblichen Passwörter und nicht nur Ziffern.'
    )
    password2 = forms.CharField(
        label='Passwort bestätigen',
        widget=forms.PasswordInput(
            attrs={'class': 'form-input w-100',
                   'placeholder': 'sUp3rS1ch3R!',
                   }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': 'Dein Benutzername, der für andere Benutzer sichtbar ist. '
                        'Maximal 150 Zeichen, nur Buchstaben, Zahlen und die Zeichen @.-+_ zulässig.',
            'email': 'Deine E-Mail-Adresse, wird nicht öffentlich angezeigt',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input w-100', 'placeholder': 'user'}),
            'email': forms.EmailInput(attrs={'class': 'form-input w-100', 'placeholder': 'max.mustermann@example.de'}),
        }

    def __init__(self, *args, **kwargs):
        """ defines the email-field as mandatory """
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def save(self, commit=True):
        """ saves the new user and stores additionally the email-address """
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CommentForm(forms.Form):
    """ Form to store new comments for ideas """
    CHOICES = [
        ('empty', 'Status ändern...'),
        ('success', 'Feedback als erfolgreich umgesetzt markieren'),
        ('failure', 'Feedback als abgelehnt markieren'),
        ('reopen', 'Feedback erneut öffnen'),
    ]
    content = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control w-100',
                'placeholder': 'Dein Kommentar?',
                'rows': 4
            }
        )
    )
    archive = forms.ChoiceField(
        required=False,
        choices=CHOICES,
        label='Status',
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )
    anonymous = forms.BooleanField(
        required=False,
        label='Anonym kommentieren',
        widget=forms.CheckboxInput(
            attrs={
                'checked': True,
            }
        )
    )

    def __init__(self, idea, *args, **kwargs):
        """ Removes the already selected choices for the archive field. """
        super(CommentForm, self).__init__(*args, **kwargs)
        if idea.state == Idea.OPEN:
            delete_id = 3
        else:
            if idea.state == Idea.SUCCESS:
                delete_id = 1
            else:
                delete_id = 2
        if delete_id:
            del self.fields['archive'].choices[delete_id]
            del self.fields['archive'].widget.choices[delete_id]


class VoteForm(forms.Form):
    idea = forms.IntegerField()
    CHOICES = [
        ('up', 'up'),
        ('neutral', 'neutral'),
        ('down', 'down'),
        ('star', 'star'),
    ]
    action = forms.ChoiceField(choices=CHOICES)
