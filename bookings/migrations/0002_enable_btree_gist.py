from django.db import migrations
from django.contrib.postgres.operations import BtreeGistExtension

class Migration(migrations.Migration):
    dependencies = [("bookings", "0001_initial")]

    operations = [BtreeGistExtension()]
