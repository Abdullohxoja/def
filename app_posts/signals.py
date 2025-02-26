from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


from app_posts.models import PostModel

@receiver(pre_save, sender=PostModel)
def generate_slug_for_post(sender ,instance ,  **kwargs):
        if not instance.slug:
            original_slug = slugify(instance.title )
            slug = original_slug
            count = 0
            while PostModel.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{count}"
                count += 1

        instance.slug = slug


