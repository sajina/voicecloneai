"""
Management command to auto-generate sample audio for all voice profiles.
Run with: python manage.py generate_samples
Options:
  --force    Regenerate even if sample_audio already exists
  --id ID    Generate for a specific profile ID only
"""

import os
import uuid
import asyncio
import edge_tts

from django.conf import settings
from django.core.management.base import BaseCommand
from apps.voices.models import VoiceProfile
from apps.voices.services import voice_service


# Sample texts per language (short intro for each voice)
SAMPLE_TEXTS = {
    'en': "Hello, I am {name}. This is a sample of my voice.",
    'es': "Hola, soy {name}. Esta es una muestra de mi voz.",
    'fr': "Bonjour, je suis {name}. Ceci est un échantillon de ma voix.",
    'de': "Hallo, ich bin {name}. Dies ist eine Hörprobe meiner Stimme.",
    'pt': "Olá, eu sou {name}. Esta é uma amostra da minha voz.",
    'it': "Ciao, sono {name}. Questo è un campione della mia voce.",
    'ru': "Привет, я {name}. Это образец моего голоса.",
    'ja': "こんにちは、{name}です。これは私の声のサンプルです。",
    'ko': "안녕하세요, 저는 {name}입니다. 제 목소리 샘플입니다.",
    'zh': "你好，我是{name}。这是我的声音样本。",
    'hi': "नमस्ते, मैं {name} हूँ। यह मेरी आवाज़ का नमूना है।",
    'bn': "নমস্কার, আমি {name}। এটি আমার কণ্ঠের নমুনা।",
    'ta': "வணக்கம், நான் {name}. இது என் குரலின் மாதிரி.",
    'te': "నమస్కారం, నేను {name}. ఇది నా గొంతు నమూనా.",
    'mr': "नमस्कार, मी {name}. हा माझ्या आवाजाचा एक नमुना आहे.",
    'gu': "નમસ્તે, હું {name} છું. આ મારા અવાજનો નમૂનો છે.",
    'kn': "ನಮಸ್ಕಾರ, ನಾನು {name}. ಇದು ನನ್ನ ಧ್ವನಿಯ ಮಾದರಿ.",
    'ml': "നമസ്കാരം, ഞാൻ {name}. ഇതെന്റെ ശബ്ദത്തിന്റെ മാതൃകയാണ്.",
    'pa': "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਮੈਂ {name} ਹਾਂ। ਇਹ ਮੇਰੀ ਆਵਾਜ਼ ਦਾ ਨਮੂਨਾ ਹੈ।",
    'ur': "ہیلو، میں {name} ہوں۔ یہ میری آواز کا نمونہ ہے۔",
    'th': "สวัสดี ฉันชื่อ {name} นี่คือตัวอย่างเสียงของฉัน",
    'vi': "Xin chào, tôi là {name}. Đây là mẫu giọng nói của tôi.",
    'id': "Halo, saya {name}. Ini adalah contoh suara saya.",
    'ms': "Halo, saya {name}. Ini adalah contoh suara saya.",
    'fil': "Kamusta, ako si {name}. Ito ay isang halimbawa ng aking boses.",
    'my': "မင်္ဂလာပါ၊ ကျွန်ုပ်အမည် {name} ပါ။ ဒါက ကျွန်ုပ်အသံနမူနာပါ။",
    'ar': "مرحباً، أنا {name}. هذه عينة من صوتي.",
    'he': "שלום, אני {name}. זו דוגמה של הקול שלי.",
    'fa': "سلام، من {name} هستم. این نمونه‌ای از صدای من است.",
    'tr': "Merhaba, ben {name}. Bu sesimin bir örneği.",
    'nl': "Hallo, ik ben {name}. Dit is een voorbeeld van mijn stem.",
    'pl': "Cześć, jestem {name}. To próbka mojego głosu.",
    'sv': "Hej, jag heter {name}. Detta är ett prov på min röst.",
    'da': "Hej, jeg hedder {name}. Dette er en prøve på min stemme.",
    'no': "Hei, jeg heter {name}. Dette er en prøve på min stemme.",
    'fi': "Hei, olen {name}. Tässä on näyte äänestäni.",
    'el': "Γεια σας, είμαι ο {name}. Αυτό είναι ένα δείγμα της φωνής μου.",
    'cs': "Ahoj, jsem {name}. Toto je ukázka mého hlasu.",
    'hu': "Szia, {name} vagyok. Ez a hangom mintája.",
    'ro': "Bună, sunt {name}. Acesta este un exemplu al vocii mele.",
    'uk': "Привіт, я {name}. Це зразок мого голосу.",
    'bg': "Здравейте, аз съм {name}. Това е проба от моя глас.",
    'sk': "Ahoj, som {name}. Toto je ukážka môjho hlasu.",
    'hr': "Bok, ja sam {name}. Ovo je uzorak mog glasa.",
    'sl': "Živjo, jaz sem {name}. To je vzorec mojega glasu.",
    'lt': "Labas, aš esu {name}. Tai mano balso pavyzdys.",
    'lv': "Sveiki, es esmu {name}. Šis ir manas balss paraugs.",
    'et': "Tere, olen {name}. See on minu hääle näidis.",
    'ca': "Hola, soc {name}. Aquesta és una mostra de la meva veu.",
    'ga': "Dia duit, is mise {name}. Seo sampla de mo ghuth.",
    'cy': "Helo, {name} ydw i. Dyma sampl o fy llais.",
    'sw': "Hujambo, mimi ni {name}. Hii ni sampuli ya sauti yangu.",
    'af': "Hallo, ek is {name}. Hierdie is 'n voorbeeld van my stem.",
    'am': "ሰላም፣ እኔ {name} ነኝ። ይህ የድምፄ ናሙና ነው።",
    'zu': "Sawubona, ngingu-{name}. Lesi isibonelo sezwi lami.",
}


class Command(BaseCommand):
    help = 'Auto-generate sample audio for voice profiles using edge-tts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate sample audio even if one already exists',
        )
        parser.add_argument(
            '--id',
            type=int,
            default=None,
            help='Generate sample audio for a specific profile ID only',
        )

    def handle(self, *args, **options):
        force = options['force']
        profile_id = options['id']

        if profile_id:
            profiles = VoiceProfile.objects.filter(id=profile_id)
        elif force:
            profiles = VoiceProfile.objects.all()
        else:
            # Only profiles without sample_audio
            profiles = VoiceProfile.objects.filter(sample_audio='')

        total = profiles.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No profiles need sample audio generation.'))
            return

        # Ensure output directory exists
        output_dir = os.path.join(settings.MEDIA_ROOT, 'voiceprofile_audio')
        os.makedirs(output_dir, exist_ok=True)

        self.stdout.write(f'Generating sample audio for {total} voice profiles...\n')

        success_count = 0
        fail_count = 0

        for i, profile in enumerate(profiles, 1):
            # Get localized sample text
            template = SAMPLE_TEXTS.get(profile.language, SAMPLE_TEXTS['en'])
            sample_text = template.replace('{name}', profile.name)

            self.stdout.write(f'[{i}/{total}] {profile.name} ({profile.language}/{profile.gender})... ', ending='')

            try:
                # Get the correct edge-tts voice
                voice_shortname = voice_service.get_voice_shortname(profile=profile)

                # Generate unique filename
                filename = f'{uuid.uuid4().hex}.mp3'
                filepath = os.path.join(output_dir, filename)

                # Generate audio with edge-tts
                async def _generate():
                    communicate = edge_tts.Communicate(sample_text, voice_shortname)
                    await communicate.save(filepath)

                asyncio.run(_generate())

                # Get duration
                duration = 0
                try:
                    from mutagen.mp3 import MP3
                    audio = MP3(filepath)
                    duration = round(audio.info.length, 2)
                except Exception:
                    duration = round(len(sample_text) / (150 * 5 / 60), 2)

                # Save relative path to the profile's sample_audio field
                relative_path = f'voiceprofile_audio/{filename}'
                profile.sample_audio = relative_path
                profile.save(update_fields=['sample_audio'])

                self.stdout.write(self.style.SUCCESS(f'OK ({duration}s)'))
                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'FAILED: {e}'))
                fail_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! Generated: {success_count}, Failed: {fail_count}, Total: {total}'
        ))

