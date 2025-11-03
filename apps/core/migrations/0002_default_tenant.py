from django.db import migrations


def create_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('core', 'Tenant')
    if not Tenant.objects.filter(subdomain='default').exists():
        Tenant.objects.create(
            name='Default',
            subdomain='default',
            is_active=True,
            settings={},
            max_users=100,
            max_storage_mb=10240,
            features_enabled={'crm': True, 'commerce': True, 'operations': True, 'finance': True, 'analytics': True},
        )


def delete_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('core', 'Tenant')
    Tenant.objects.filter(subdomain='default').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tenant, delete_default_tenant),
    ]