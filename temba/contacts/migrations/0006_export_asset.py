# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.core.files.storage import default_storage
from django.db import migrations
from temba.assets import AssetType
from temba.orgs.models import Org


def migrate_contact_exports(apps, schema_editor):
    ExportContactsTask = apps.get_model('contacts', 'ExportContactsTask')

    handler = AssetType.contact_export.get_handler()

    num_copied = 0
    num_missing = 0
    num_failed = 0

    for task in ExportContactsTask.objects.select_related('created_by').all():
        if not task.filename:
            num_missing += 1
            continue

        identifier = task.pk
        existing_ext = os.path.splitext(task.filename)[1][1:]

        # need to patch org attribute to have get_user_org_group method
        task.org.get_user_org_group = lambda u: Org.objects.get(pk=task.org_id).get_user_org_group(u)

        try:
            existing_file = default_storage.open(task.filename)
            handler.save(identifier, existing_file, existing_ext)
            num_copied += 1
        except Exception:
            print "Unable to open %s" % task.filename
            num_failed += 1

    print 'Copied %d contact export files (%d tasks have no file, %d could not be opened)' % (num_copied, num_missing, num_failed)


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20141210_0208'),
    ]

    operations = [
        migrations.RunPython(migrate_contact_exports)
    ]
