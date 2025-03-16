from django.db import migrations

def create_missing_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')

    for user in User.objects.all():
        if not Profile.objects.filter(user=user).exists():  # More reliable than hasattr
            Profile.objects.create(user=user)

class Migration(migrations.Migration):
    
    dependencies = [
    ('accounts', '0001_initial'),
]

operations = [
        migrations.RunPython(create_missing_profiles),
    ]
