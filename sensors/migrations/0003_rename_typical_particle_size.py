# Generated manually to rename the camelCase legacy field name.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0002_weatherdata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sps30data',
            old_name='typicalParticleSize',
            new_name='typical_particle_size',
        ),
    ]
