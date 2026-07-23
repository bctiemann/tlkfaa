from django.db import migrations, models


def dedupe_favorites(apps, schema_editor):
    Favorite = apps.get_model('fanart', 'Favorite')
    for field in ('artist_id', 'picture_id', 'character_id'):
        seen = {}
        qs = Favorite.objects.filter(user_id__isnull=False, **{f'{field}__isnull': False}).order_by('id')
        for fave in qs.iterator():
            key = (fave.user_id, getattr(fave, field))
            keeper = seen.get(key)
            if keeper is None:
                seen[key] = fave
            else:
                if fave.is_visible and not keeper.is_visible:
                    keeper.is_visible = True
                    keeper.save(update_fields=['is_visible'])
                fave.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('fanart', '0181_prompt'),
    ]

    operations = [
        migrations.RunPython(dedupe_favorites, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=['user', 'artist'], name='unique_favorite_user_artist'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=['user', 'picture'], name='unique_favorite_user_picture'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=['user', 'character'], name='unique_favorite_user_character'),
        ),
    ]