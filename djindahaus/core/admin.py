# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models

from djindahaus.core.models import Area


class AreaAdmin(admin.ModelAdmin):
    """Area admin class."""

    list_display = (
        'name',
        'rf_domain',
        'capacity',
        'rank',
        'active',
        'parent',
        'tags',
        'created_at',
    )
    list_editable = ('active', 'rank', 'capacity')
    list_per_page = 25
    ordering = ('name',)


admin.site.register(Area, AreaAdmin)
