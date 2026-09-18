/** Copy to your generated project's src/config.ts alongside narration.txt. */
export type HudEntry = {fromS: string; toS: string; text: string; tech?: string; fromOffset?: number; toOffset?: number; w?: number};
export type RailSpec = {steps: string[]; switchS: string[]; fromS: string; toS: string};
export const VIDEO = {
  slug: 'turkce',
  lang: 'tr' as 'zh' | 'en' | 'tr',
  bg: 'stars' as 'stars' | 'dots',
  title: {big: 'TÜRKÇE', rest: '', en: 'Ses ve altyazı', tagline: 'Çığ, ışık, güneş ve öğrenme'},
  credit: null as {kicker: string; title: string; byline: string; note: string} | null,
  chapterTech: ['', ''],
  hud: [
    {fromS: 'S01', toS: 'S01', text: 'Türkçe karakterler'},
    {fromS: 'S02', toS: 'S02', text: 'Eşzamanlı altyazı'},
  ] as HudEntry[],
  rails: [] as RailSpec[],
  endingFade: 30,
};
