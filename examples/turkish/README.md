# Turkish voice and subtitle fixture

This two-line, two-chapter fixture checks Turkish letters, apostrophized suffixes, ASCII-only Turkish, subtitle spacing and chapter transitions. It is not a complete explainer film.

1. Create a project from `template/` (see [Türkçe setup](../../README_TR.md)).
2. Copy this folder's `config.ts` to the project's `src/config.ts`.
3. Copy `narration.txt` to the project's `script/narration.txt`.
4. Run `python -X utf8 scripts/tts_build.py` in the project: default Ahmet, natural speed.
5. Run `npm run typecheck`, then `npx remotion studio src/index.ts`. Check `Video` for narration, subtitles, title, HUD and chapter progress. The content area has no authored shots.
6. For a second voice, set `VOICE=tr-TR-EmelNeural` and rerun TTS. All timing files will be regenerated.

Expected artifacts: `public/assets/turkce/audio.wav`, `script/timeline.json`, `script/subtitles.srt`, `script/subtitles.vtt`, `src/common/subs.ts`, `src/common/timeline.ts`. The JSON must report `lang: tr`, `engine: edge` and the selected Turkish voice. Look for intact `Çç Ğğ Iı İi Öö Şş Üü`, positive non-overlapping subtitle intervals and words separated at `|` boundaries.
