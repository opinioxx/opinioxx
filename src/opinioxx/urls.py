"""opinioxx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import importlib

from django.apps import apps
from django.contrib import admin
from django.urls import path, include

plugin_patterns = []
for app in apps.get_app_configs():
    if hasattr(app, 'OpinioxxPlugin'):
        if importlib.util.find_spec(f'{app.name}.utils'):
            module = importlib.import_module(f'{app.name}.urls')
            plugin_patterns.append(path('', include(module, app.label)))

urlpatterns = [
    path('', include((plugin_patterns, 'plugins'))),
    path('', include('opinioxx.base.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]
