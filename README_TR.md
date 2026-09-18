# anything2explainer — Türkçe

[English](README.md) | [简体中文](README_ZH.md) | **Türkçe**

**Yeni başlayanlar:** [Kurulumdan ilk videoya](KURULUM_TR.md) — Windows/macOS/Linux adımları ve AI'a verilecek istem. [Görsel çalışma rehberi](rehber.html) — bütün üretim süreci, AI'ın rolü ve etkileşimli zaman çizelgesi; dosyayı tarayıcıda açın.

Bir konu veya senaryodan seslendirmeli, altyazılı açıklayıcı video üreten Claude Code / Codex becerisi ve Remotion şablonu. Görseller React + TypeScript koduyla çizilir. Çıktı 1280×720, 30 fps H.264 videodur. Araştırma, senaryo, seslendirme, zaman çizelgesi, sahneler ve kalite kontrol adımları [SKILL.md](SKILL.md) içinde tanımlıdır. Bu depo tek komutla her senaryoya görsel üreten bağımsız bir uygulama değildir; sahneleri kodlama ajanı veya geliştirici hazırlar.

## AI ajanıyla hızlı başlangıç

Türkçe desteği içeren sürümü indirin:

```bash
git clone https://github.com/omergocmen/anything2explainer.git
cd anything2explainer
```

[Kurulum rehberindeki](KURULUM_TR.md) işletim sisteminize uygun bağımlılıkları kurun. Codex veya Claude Code'da repo klasörünü açın ve aşağıdaki metni **ajanın sohbetine** yazın:

```text
SKILL.md ve KURULUM_TR.md dosyalarını oku. Bu repoyu kullanarak
[KONUNUZ / SENARYO DOSYANIZ] için yaklaşık 3 dakikalık bir video üret.
Yeni projeyi videolar/benim-videom klasöründe oluştur.
Seslendirme, altyazılar ve ekrandaki metinler Türkçe olsun.
src/config.ts içinde lang: 'tr' kullan; ses Edge TTS tr-TR-AhmetNeural olsun.
Önce senaryoyu, ardından ilk 30 saniyeyi onayıma sun.
Konuya özel sahneleri de oluştur; MP4, SRT/VTT ve kaynak projeyi teslim et.
Python için repo kökündeki .venv ortamını kullan.
```

`[KONUNUZ / SENARYO DOSYANIZ]` kısmını değiştirin. Kadın ses isterseniz `tr-TR-EmelNeural` belirtin. Türkçe model veya font indirmeniz gerekmez; font depodadır, ses çevrimiçi Edge TTS ile üretilir. Dil ve sahne ayarlarını ajan yapabilir. Ayrıntılı kurulum, ilk test ve sorun giderme için [KURULUM_TR.md](KURULUM_TR.md) dosyasını izleyin.

## Türkçe desteği

- `src/config.ts` içinde `lang: 'tr'` seçilir. Dil tahmini yapılmaz; Türkçe karakter içermeyen `Merhaba bu bir test` gibi cümleler de Türkçe sesle okunur.
- Varsayılan motor `edge`, ses `tr-TR-AhmetNeural`, hız `+0%`. Kadın ses için `VOICE=tr-TR-EmelNeural` kullanılabilir. [Microsoft ses listesi](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts) her iki sesi de listeler. Edge TTS internet gerektirir; metni Microsoft'un çevrimiçi hizmetine gönderir, API anahtarı gerektirmez.
- Sesin kelime zamanları altyazı bloklarına eşlenir. `İ/i`, `I/ı`, `ç, ğ, ö, ş, ü` ve `İstanbul'da` / `İstanbul’da` gibi yazımlar korunur. Eşleşmeyen bloklar için tahmini zaman kullanıldığında uyarı verilir; önizlemede kontrol edilmelidir.
- Altyazılar videoya gömülür; ayrıca UTF-8 `script/subtitles.srt` ve `script/subtitles.vtt` üretilir. İkisi de videoyla aynı zaman çizelgesini kullanır.
- Gövde, başlık, bölüm adları ve altyazılarda Türkçe harfleri kapsayan Noto Sans kullanılır. Font depoda bulunur; render sırasında font indirilmez. Türkçe başlıklar yatay daraltılmaz.
- `kokoro` ve `kokoro_onnx` Türkçe için reddedilir. Yerel Piper kullanılacaksa ayrıca **Türkçe bir model** verilmelidir; varsayılan İngilizce modeller Türkçe desteği sağlamaz. Hazır ses kaydı da özgün projedeki elle zaman çizelgesi doldurma yöntemiyle kullanılabilir.

## Kurulum

Node.js 18 veya üzeri, Python 3 ve `PATH` içinde FFmpeg gerekir. Türkçe için Kokoro, PyTorch veya espeak-ng kurmaya gerek yoktur.

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install edge-tts==7.2.8 numpy pillow scipy
```

macOS/Linux proje oluşturma:

```bash
template/scripts/new_project.sh ~/work/turkce-video turkce
cd ~/work/turkce-video
```

Windows PowerShell için yeni, boş bir klasöre şablonu kopyalayın. Depo kökünden:

```powershell
$proje = Join-Path $PWD 'turkce-video'
New-Item -ItemType Directory -Path $proje -ErrorAction Stop
Copy-Item template/src,template/public,template/scripts,template/script -Destination $proje -Recurse
Copy-Item template/package.json,template/tsconfig.json,template/remotion.config.ts -Destination $proje
Set-Location $proje
npm.cmd install
```

`new_project.sh` ve diğer `.sh` yardımcıları zsh içindir. Windows'ta aşağıdaki Python ve Remotion komutları doğrudan kullanılabilir.

## Senaryo ve seslendirme

Projenin `src/config.ts` dosyasında:

```ts
lang: 'tr' as 'zh' | 'en' | 'tr',
title: {big: 'YAPAY ZEKA', rest: '', en: 'Nasıl çalışır?', tagline: 'Bir örnek üzerinden öğrenelim'},
chapterTech: ['', ''],
```

`slug`, başlık, `hud`, bölüm alt başlıkları ve varsa `rails` / `credit` metinlerini de içeriğinize göre düzenleyin. `title.en` alanı tarihsel adıyla kalmıştır; Türkçe alt başlık yazılabilir. `hud` aralıklarındaki `S01`, `S02` gibi kimlikler senaryodaki cümlelere karşılık gelir.

UTF-8 `script/narration.txt` örneği:

```text
# CHAPTER 1 Giriş
Bir sorunuz var.|Yanıtı nerede ararsınız?
# CHAPTER 2 Örnek
İstanbul'daki bir kütüphaneyi düşünün.|Önce ilgili kitabı bulursunuz.
```

Bir satır bir seslendirme cümlesidir. `|` altyazı bloklarını ayırır; seslendirmeye gönderilmeden önce bloklar **boşlukla** birleştirilir. Kelimeleri veya kesme işaretli ekleri ortadan bölmeyin. Her blokta boşluk ve noktalama dahil **en fazla 42 karakter**, bölüm adlarında yaklaşık 14 karakter hedefleyin. Uzun bloklarda uyarı ve yazı boyutu küçültme vardır; okunabilir sonuç için metni `|` ile bölün. `## gap 20` sonraki cümleden önce 20 kare bekleme ekler.

Türkçe ekler ve terimler konuşma süresini etkiler. İlk taslak için dakikada 110–140 kelime bir **yazım tahminidir**, ölçülmüş motor hızı değildir. Kısa örnek üretin, `script/timeline.json` içindeki gerçek süreyi kontrol edin ve hedef süre için metni düzenleyin.

Varsayılan Ahmet sesiyle, proje kökünde:

```bash
python -X utf8 scripts/tts_build.py
```

Emel sesiyle PowerShell:

```powershell
$env:TTS_ENGINE = 'edge'
$env:VOICE = 'tr-TR-EmelNeural'
$env:RATE = '+0%'
python -X utf8 scripts/tts_build.py
# Sonraki çalışmada dilin varsayılanlarına dönmek için:
Remove-Item Env:TTS_ENGINE,Env:VOICE,Env:RATE -ErrorAction SilentlyContinue
```

macOS/Linux:

```bash
TTS_ENGINE=edge VOICE=tr-TR-EmelNeural RATE=+0% python scripts/tts_build.py
```

Önceki projeden kalan `VOICE` değişkeni farklı bir dili seçiyorsa Türkçe üretimi açıklayıcı bir hatayla durur. Dil ve ses değişince önbellek anahtarı değişir; eski ses yeniden kullanılmaz.

Üretilen dosyalar:

| Dosya | İçerik |
|---|---|
| `public/assets/<slug>/audio.wav` | 48 kHz stereo, 16-bit ses |
| `src/common/timeline.ts` | Bölüm ve cümle kareleri, toplam süre |
| `src/common/subs.ts` | Videoya gömülen altyazılar |
| `script/timeline.json`, `script/timeline.md` | İncelenebilir zaman çizelgesi |
| `script/subtitles.srt`, `script/subtitles.vtt` | Ayrı oynatıcı/editörler için altyazı |

Seslendirmeden sonra `script/storyboard_src.md` hazırlanır; `python -X utf8 scripts/render_storyboard.py` kareleri doldurur. Sahne bileşenleri `src/shots/` altında yazılır. Metin değişirse zamanlar da değişir; sahne kodundaki kareler yeniden uyarlanmalıdır.

```bash
npm run typecheck
npx remotion studio src/index.ts
npx remotion render src/index.ts Video renders/turkce.mp4 --codec h264
```

Şablon başlangıçta yalnızca genel katmanları içerir. [Türkçe örnek](examples/turkish/README.md) ses, altyazı ve harf kontrolü içindir; tamamlanmış açıklayıcı film değildir.

## Doğrulama

Depo kökünden çevrimdışı testler:

```bash
python -X utf8 -m unittest discover -s template/tests -v
npm run typecheck --prefix template
```

Testler `numpy` gerektirir ve ses servisine bağlanmaz. Gerçek servis kontrolü için örnek senaryoyu iki sesle de üretip önizleyin. Türkçe font kapsamı için isteğe bağlı `fonttools` kurup `python template/tests/check_turkish_fonts.py` çalıştırın.

## Lisans

Projenin lisansı [PolyForm Noncommercial](LICENSE): ticari kullanım için özgün yazarın izni gerekir. Ürettiğiniz videolar size aittir. Fontların [SIL OFL lisansları](template/public/fonts/LICENSE.md) ayrıdır. Ayrıntılı mimari ve özgün referans filmler için [ana README](README.md) dosyasına bakın.
