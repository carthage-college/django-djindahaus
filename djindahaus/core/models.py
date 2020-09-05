# -*- coding: utf-8 -*-

"""Data models."""

from django.db import models
from django.contrib.auth.models import User

from taggit.managers import TaggableManager


class Area(models.Model):
    """Area model."""

    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    name = models.CharField("Friendly Name", max_length=128)
    rf = models.CharField("RF Domain Name", max_length=128, null=True, null=True)
    parent = models.ForeignKey(
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
    )
    capacity = models.IntegerField()
    active = models.BooleanField(default=True, verbose_name="Active?")
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        """Default data for display."""
        return "{0}, {1}".format(
            self.created_by.last_name, self.created_by.first_name
        )


class Capacity(models.Model):
    """Capacity model."""

    area = models.ForeignKey(
        Area,
        related_name='capacity',
        editable=False,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    occupied = models.IntegerField(
        verbose_name="Capacity Count",
        null=True,
        blank=True,
        default=0,
        help_text="A number that determines this object's position in a list.",
    )
    status = models.BooleanField(default=True, verbose_name="Active?")

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['created_at-']

    def __str__(self):
        """Default data for display."""
        return self.count
