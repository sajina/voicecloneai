
import os
import django
from django.conf import settings

# Configure Django settings manually if needed, or rely on DJANGO_SETTINGS_MODULE env var
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from apps.voices.models import VoiceProfile

total = VoiceProfile.objects.count()
with_audio = VoiceProfile.objects.exclude(sample_audio='').exclude(sample_audio__isnull=True).count()
without_audio = VoiceProfile.objects.filter(sample_audio__in=['', None]).count()

print(f"Total profiles: {total}")
print(f"With sample audio: {with_audio}")
print(f"Without sample audio: {without_audio}")

# List a few sample audio paths if any exist
if with_audio > 0:
    print("\nSample paths:")
    for vp in VoiceProfile.objects.exclude(sample_audio='').exclude(sample_audio__isnull=True)[:5]:
        print(f"- {vp.name}: {vp.sample_audio}")
