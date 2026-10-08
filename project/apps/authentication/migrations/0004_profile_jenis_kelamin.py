from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_profile_kepegawaian_profile_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='jenis_kelamin',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
