"""Offline regression tests: python -m unittest discover -s tests -v (requires numpy)."""
import asyncio
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import wave

import numpy as np

TEMPLATE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('tts_build', TEMPLATE / 'scripts/tts_build.py')
tts = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tts)


class LanguageTests(unittest.TestCase):
    def test_engine_defaults_and_overrides(self):
        for lang, engine in [('tr', 'edge'), ('zh', 'edge'), ('en', 'kokoro')]:
            self.assertEqual(tts.resolve_engine(lang, 'auto'), engine)
            self.assertEqual(tts.resolve_engine(lang, 'edge'), 'edge')
        self.assertEqual(tts.resolve_engine('tr', 'piper'), 'piper')

    def test_turkish_rejects_both_kokoro_engines(self):
        for engine in ('kokoro', 'kokoro_onnx'):
            with self.assertRaisesRegex(SystemExit, 'Turkish is not supported'):
                tts.resolve_engine('tr', engine)

    def test_parser_bom_nfc_and_gaps(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'narration.txt'
            path.write_text('# CHAPTER 1 I\u0307şık\n## gap 12\n## gap 8\n'
                            'G\u0306üneş|ısınmayı sağlar.\n', encoding='utf-8-sig')
            items = tts.parse(path)
            self.assertEqual(items[0]['title'], 'Işık'.replace('I', 'İ'))
            self.assertEqual(items[1]['raw'], 'Ğüneş|ısınmayı sağlar.')
            self.assertEqual(items[1]['gap_before'], 20)

    def test_turkish_case_and_apostrophes(self):
        with patch.object(tts, 'CFG_LANG', 'tr'):
            self.assertEqual(tts.alignment_text('İSTANBUL’UN'), 'istanbulun')
            self.assertEqual(tts.alignment_text('IŞIĞI'), 'ışığı')
            self.assertNotEqual(tts.alignment_text('I'), tts.alignment_text('İ'))
            chunks = ['Işık yayılır.', "İstanbul’da ölçülür.", 'Şimdi bakalım.']
            words = [{'text': 'IŞIK', 't': .1, 'd': .4},
                     {'text': "istanbul'da", 't': 1.6, 'd': .8},
                     {'text': 'ŞİMDİ', 't': 3.1, 'd': .4}]
            starts = tts.chunk_starts(' '.join(chunks), chunks, words, .1, 4, ' ')
            self.assertEqual(starts, [0, 1.5, 3])

    def test_english_and_chinese_boundaries(self):
        for lang, chunks, sep, word in [('en', ['Hello!', 'World.'], ' ', 'world'),
                                       ('zh', ['你好', '世界'], '', '世界')]:
            with patch.object(tts, 'CFG_LANG', lang):
                starts = tts.chunk_starts(sep.join(chunks), chunks,
                                         [{'text': word, 't': 1, 'd': .5}], 0, 2, sep)
                self.assertEqual(starts, [0, 1])

    def test_unmatched_words_do_not_match_one_letter(self):
        chunks = ['Başla', 'bir', 'son']
        with patch.object(tts, 'CFG_LANG', 'tr'), contextlib.redirect_stdout(io.StringIO()) as log:
            starts = tts.chunk_starts(' '.join(chunks), chunks,
                                     [{'text': 'bilinmeyen', 't': 8, 'd': 1},
                                      {'text': 'son', 't': 2, 'd': 1}], 0, 3, ' ')
        self.assertIn('estimated', log.getvalue())
        self.assertTrue(0 < starts[1] < starts[2] == 2)

    def test_missing_boundaries_are_monotonic_and_bounded(self):
        with contextlib.redirect_stdout(io.StringIO()):
            starts = tts.chunk_starts('a b c d', ['a', 'b', 'c', 'd'], [], .2, 2, ' ')
        self.assertEqual(starts, sorted(starts))
        self.assertEqual(starts[0], 0)
        self.assertLess(starts[-1], 2)

    def test_cache_is_language_voice_and_rate_specific(self):
        with patch.object(tts, 'CFG_LANG', 'tr'), patch.object(tts, 'VOICE', 'tr-TR-AhmetNeural'):
            first = tts.cache_path('Merhaba', '.mp3')
            with patch.object(tts, 'VOICE', 'tr-TR-EmelNeural'):
                self.assertNotEqual(first, tts.cache_path('Merhaba', '.mp3'))
            with patch.object(tts, 'RATE', '+10%'):
                self.assertNotEqual(first, tts.cache_path('Merhaba', '.mp3'))
            with patch.object(tts, 'CFG_LANG', 'en'):
                self.assertNotEqual(first, tts.cache_path('Merhaba', '.mp3'))

    def test_width_handles_decomposed_turkish(self):
        self.assertEqual(tts.text_em('İĞŞ'), tts.text_em('I\u0307G\u0306S\u0327'))


class PipelineTests(unittest.TestCase):
    def test_edge_requests_word_boundaries_and_reuses_utf8_cache(self):
        calls = []

        class FakeCommunicate:
            def __init__(self, text, voice, **kwargs):
                calls.append((text, voice, kwargs))

            async def stream(self):
                yield {'type': 'audio', 'data': b'test-mp3'}
                yield {'type': 'WordBoundary', 'offset': 1000000, 'duration': 2000000, 'text': 'İstanbul'}

        with tempfile.TemporaryDirectory() as temp, \
             patch.multiple(tts, CACHE=temp, CFG_LANG='tr', ENGINE='edge',
                            VOICE='tr-TR-EmelNeural', RATE='+0%'), \
             patch.dict(sys.modules, {'edge_tts': types.SimpleNamespace(Communicate=FakeCommunicate)}):
            first = asyncio.run(tts.synth_edge('İstanbul'))
            second = asyncio.run(tts.synth_edge('İstanbul'))
            self.assertEqual(first, second)
            self.assertEqual(calls, [('İstanbul', 'tr-TR-EmelNeural', {'rate': '+0%', 'boundary': 'WordBoundary'})])
            self.assertEqual(first[1], [{'t': .1, 'd': .2, 'text': 'İstanbul'}])

    def test_config_language_and_default_voices_in_fresh_process(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            (root / 'src').mkdir()
            shutil.copy(TEMPLATE / 'scripts/tts_build.py', root / 'scripts/tts_build.py')
            env = {k: v for k, v in os.environ.items() if k not in ('VOICE', 'RATE', 'TTS_ENGINE')}
            for lang, voice, rate in [('tr', 'tr-TR-AhmetNeural', '+0%'),
                                      ('en', 'en-US-AndrewNeural', '+0%'),
                                      ('zh', 'zh-CN-YunxiNeural', '+8%')]:
                # The comment must never override the actual config value.
                (root / 'src/config.ts').write_text(
                    f"// lang: 'en'\nexport const VIDEO = {{\n slug: 'test',\n lang: '{lang}' as 'zh' | 'en' | 'tr',\n}};",
                    encoding='utf-8')
                result = subprocess.run([sys.executable, '-c',
                    "import tts_build as t; print(t.CFG_LANG, t.VOICE, t.RATE)"],
                    cwd=root / 'scripts', env=env, capture_output=True, text=True, check=True)
                self.assertEqual(result.stdout.strip(), f'{lang} {voice} {rate}')

    def test_full_pipeline_preserves_turkish_and_exports_frame_times(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'src/common').mkdir(parents=True)
            narr = root / 'narration.txt'
            narr.write_text('# CHAPTER 1 Işık\nMerhaba|bu bir test.\n'
                            '# CHAPTER 2 Ölçüm\nİstanbul’da ışık|Çığ, öykü, şüphe ve güneş.\n', encoding='utf-8')
            calls = []

            async def fake_synth(chunks, sep):
                calls.append((chunks, sep))
                # Degenerate provider timestamps must still produce positive, adjacent frame intervals.
                return np.full(tts.SR * 2, .1, dtype=np.float32), [0, 0], 2

            with patch.multiple(tts, ROOT=str(root), REM=str(root), CACHE=str(root / 'cache'),
                                CFG_LANG='tr', ENGINE='auto', VOICE='tr-TR-AhmetNeural', RATE='+0%'), \
                 patch.object(tts, 'synth_sentence', fake_synth), contextlib.redirect_stdout(io.StringIO()):
                asyncio.run(tts.main(str(narr)))
            self.assertTrue(all(sep == ' ' for _, sep in calls))
            tl = json.loads((root / 'script/timeline.json').read_text(encoding='utf-8'))
            self.assertEqual((tl['lang'], tl['engine'], tl['voice']), ('tr', 'edge', 'tr-TR-AhmetNeural'))
            self.assertEqual(tl['sentences'][0]['text'], 'Merhaba bu bir test.')
            self.assertEqual([c['title'] for c in tl['chapters']], ['Işık', 'Ölçüm'])
            entries = [sb for s in tl['sentences'] for sb in s['subs']]
            for sb in entries:
                self.assertLessEqual(sb['from'], sb['to'])
            for a, b in zip(entries, entries[1:]):
                self.assertLess(a['to'], b['from'])
            srt = (root / 'script/subtitles.srt').read_text(encoding='utf-8')
            self.assertIn('00:00:02,833 --> 00:00:02,867', srt)
            self.assertIn('İstanbul’da ışık', srt)
            self.assertTrue((root / 'script/subtitles.vtt').read_text(encoding='utf-8').startswith('WEBVTT\n'))
            self.assertIn('Çığ, öykü, şüphe ve güneş.', (root / 'src/common/subs.ts').read_text(encoding='utf-8'))
            with wave.open(str(root / 'public/assets' / tts.SLUG / 'audio.wav')) as wav:
                self.assertEqual((wav.getnchannels(), wav.getframerate(), wav.getsampwidth()), (2, 48000, 2))
                self.assertEqual(wav.getnframes(), tl['total_frames'] * 1600)
            # Downstream storyboard also reads the UTF-8 timeline.
            (root / 'scripts').mkdir()
            shutil.copy(TEMPLATE / 'scripts/render_storyboard.py', root / 'scripts/render_storyboard.py')
            (root / 'script/storyboard_src.md').write_text('Ölçüm {S02.c2} / {C2} / {TOTAL}', encoding='utf-8')
            subprocess.run([sys.executable, '-X', 'utf8', str(root / 'scripts/render_storyboard.py')],
                           check=True, capture_output=True)
            storyboard = (root / '分镜表.md').read_text(encoding='utf-8')
            self.assertIn(str(tl['sentences'][1]['subs'][1]['from']), storyboard)
            self.assertNotIn('{', storyboard)

    def test_unsupported_config_language_is_not_silently_chinese(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            (root / 'src').mkdir()
            shutil.copy(TEMPLATE / 'scripts/tts_build.py', root / 'scripts/tts_build.py')
            (root / 'src/config.ts').write_text(
                "export const VIDEO = {\n slug: 'test',\n lang: 'xx',\n};", encoding='utf-8-sig')
            result = subprocess.run([sys.executable, str(root / 'scripts/tts_build.py')],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Unsupported VIDEO.lang', result.stderr)

    def test_empty_narration_fails_before_synthesis(self):
        with tempfile.TemporaryDirectory() as temp:
            narr = Path(temp) / 'narration.txt'
            narr.write_text('# CHAPTER 1 Boş\n|||', encoding='utf-8')
            with patch.multiple(tts, CFG_LANG='tr', ENGINE='auto', VOICE='tr-TR-AhmetNeural'):
                with self.assertRaisesRegex(SystemExit, 'no spoken text'):
                    asyncio.run(tts.main(str(narr)))

    def test_wrong_voice_fails_before_synthesis(self):
        with patch.multiple(tts, CFG_LANG='tr', ENGINE='edge', VOICE='en-US-AndrewNeural'), \
             patch.object(tts, 'parse', return_value=[]):
            with self.assertRaisesRegex(SystemExit, 'tr-TR voice'):
                asyncio.run(tts.main('unused'))

    def test_vtt_escapes_markup(self):
        with tempfile.TemporaryDirectory() as temp:
            tts.write_subtitle_files([{'from': 1, 'to': 30, 'text': 'Çığ <örnek> & ışık'}], temp)
            vtt = (Path(temp) / 'subtitles.vtt').read_text(encoding='utf-8')
            self.assertIn('00:00:00.000 --> 00:00:01.000', vtt)
            self.assertIn('Çığ &lt;örnek&gt; &amp; ışık', vtt)


if __name__ == '__main__':
    unittest.main()
