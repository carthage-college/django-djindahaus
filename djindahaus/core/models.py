# -*- coding: utf-8 -*-

"""Data models."""

from django.db import models

from taggit.managers import TaggableManager


class Area(models.Model):
    """Area model."""

    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    rf_domain = models.CharField(
        "RF Domain Name",
        max_length=128,
    )
    name = models.CharField("Friendly Name", max_length=128)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
    )
    capacity = models.IntegerField()
    rank = models.IntegerField(
        verbose_name="Ranking",
        default=0,
        help_text="A number that determines this object's position in a list.",
    )
    active = models.BooleanField(default=True, verbose_name="Active?")
    access_points = models.TextField(
        null=True,
        blank=True,
        help_text="Comma separated list of MAC addresses. Format: B8-50-01-3A-CB-C6",
    )
    tags = TaggableManager(blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']

    def __str__(self):
        """Default data for display."""
        return self.name


class Capacity(models.Model):
    """Capacity model."""

    area = models.ForeignKey(
        Area,
        related_name='occupied',
        editable=False,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    occupied = models.IntegerField(
        verbose_name="Capacity Count",
        null=True,
        blank=True,
        default=0,
    )
    capacity = models.IntegerField(
        verbose_name="Capacity Number",
        null=True,
        blank=True,
        default=0,
        help_text="Capacity number at the time of creation.",
    )
    status = models.BooleanField(default=True, verbose_name="Active?")

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']

    def __str__(self):
        """Default data for display."""
        return self.count
