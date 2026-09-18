# Kurulumdan ilk videoya — anything2explainer

[Görsel çalışma rehberi](rehber.html) · [Türkçe proje özeti](README_TR.md) · [Ana README](README.md)

Bu rehber, depoyu ilk kez indiren kişinin önce **Türkçe sesli ve altyazılı bir test MP4'ü**, ardından kendi konusuna ait sahneleri olan bir video üretmesi içindir. Windows PowerShell ve macOS/Linux adımları ayrıdır. Komutları seçtiğiniz işletim sistemi sırasıyla çalıştırın.

## 1. Ne kuruyorsunuz?

Depo üç parça sunar:

1. **`SKILL.md` ve `reference/`:** AI kodlama ajanına araştırma, senaryo, sahne tasarımı ve kalite kontrolün nasıl yapılacağını anlatan talimatlar.
2. **`template/`:** Remotion, React ve TypeScript ile hazırlanmış video projesi. Genel katmanlar hazırdır; konuya özel sahne dizileri başlangıçta boştur.
3. **`scripts/`:** Ses üretme, zaman çizelgesi çıkarma, önizleme, render ve kontrol araçları; şablonun içindedir ve yeni projeye kopyalanır.

Kodlama ajanı (Codex veya Claude Code), isteğinizi okuyup dosya yazar ve komutları çalıştırır. **TTS metni sese dönüştürür; Remotion sahne kodunu karelere ve videoya dönüştürür.** Depoda kendi kendine çalışan bir LLM sunucusu veya tek komutla bütün filmi tasarlayan bir uygulama yoktur.

Hazır test örneğini AI hesabı olmadan render edebilirsiniz. Kendi konunuzun anlatımını ve sahnelerini hazırlamak için bir kodlama ajanı kullanın veya bu dosyaları kendiniz yazın.

## 2. Gerekenler

| Araç | Neden gerekli? | Nasıl doğrulanır? |
|---|---|---|
| Git veya indirilmiş ZIP | Kaynak dosyalarını almak | `git --version` (ZIP için gerekmez) |
| Node.js ve npm | Remotion, React, TypeScript | `node --version`, `npm --version` |
| Python 3 | TTS ve kontrol betikleri | `python --version` / `python3 --version` |
| FFmpeg ve ffprobe | Sesi çözmek, kare çıkarmak, çıktı incelemek | `ffmpeg -version`, `ffprobe -version` |
| Kodlama ajanı ve hesabı | Araştırma, senaryo ve sahne kodu hazırlamak | Ajanı açıp proje klasörüne erişebildiğini kontrol edin |
| İnternet | Paket kurulumu, araştırma, çevrimiçi AI ve Türkçe Edge TTS | Bağlantı gerekir |

README'nin Node alt sınırı 18'dir; yeni kurulumda [Node.js'in desteklenen LTS sürümünü](https://nodejs.org/en/download) kullanın. Türkçe akışı Python 3.12 ile kontrol edildi. Python'u [resmî indirme sayfasından](https://www.python.org/downloads/), FFmpeg'i [platformunuza uygun indirme bağlantısından](https://ffmpeg.org/download.html) edinebilirsiniz. Windows'ta FFmpeg'in `bin` klasörü `PATH` içinde olmalıdır; kurulumdan sonra terminali yeniden açın.

Türkçe varsayılan ses için GPU, Kokoro, PyTorch, espeak-ng veya bir TTS API anahtarı gerekmez. Edge TTS senaryo metnini Microsoft'un çevrimiçi ses hizmetine gönderir. Kodlama ajanının oturumu, kullanım kotası veya ücretlendirmesi ayrı bir konudur; repo bunları sağlamaz. İlk Remotion çalıştırması tarayıcı indirmesi yapabilir. README, çalışma için en az yaklaşık 5 GB boş alan önerir; uzun videolarda kare klasörü çok büyüyebilir.

## 3. Doğru sürümü indirin

**Türkçe desteği içeren [omergocmen/anything2explainer](https://github.com/omergocmen/anything2explainer) deposunu indirin.** Bu sürüm `examples/turkish/` klasörünü ve `template/src/config.ts` içinde `'tr'` dil seçeneğini içerir. Farklı bir fork veya özgün depo aynı ekleri içermeyebilir.

Git ile:

```text
git clone https://github.com/omergocmen/anything2explainer.git
cd anything2explainer
```

ZIP indirdiyseniz çıkarın ve terminali içinde `SKILL.md`, `template/`, `reference/` bulunan klasörde açın. Bundan sonra bu konuma **repo kökü**, oluşturacağınız film klasörüne **video proje kökü** diyeceğiz. `npm install` repo kökünde değil, video proje kökünde çalışır; repo kökünde `package.json` yoktur.

## 4A. Windows PowerShell: ilk projeyi kurun

Repo kökünde:

```powershell
$repo = (Get-Location).Path
node --version
npm.cmd --version
python --version
ffmpeg -version

python -m venv .venv
$python = Join-Path $repo '.venv\Scripts\python.exe'
& $python -m pip install edge-tts==7.2.8 numpy pillow scipy

$proje = Join-Path $repo 'videolar\ilk-video'
if (Test-Path -LiteralPath $proje) {
    throw 'Bu proje zaten var. Yeni bir proje adı seçin.'
}
New-Item -ItemType Directory -Path $proje | Out-Null
Copy-Item template/src,template/public,template/scripts,template/script -Destination $proje -Recurse
Copy-Item template/package.json,template/tsconfig.json,template/remotion.config.ts,template/.gitignore -Destination $proje

# Türkçe test senaryosu ve onunla eşleşen ayarlar:
Copy-Item examples/turkish/config.ts (Join-Path $proje 'src\config.ts')
Copy-Item examples/turkish/narration.txt (Join-Path $proje 'script\narration.txt')

Set-Location $proje
New-Item -ItemType Directory -Path research,qc,stills,renders -Force | Out-Null
npm.cmd install
npm.cmd run typecheck
```

Her adım hata vermeden tamamlanmalıdır. Sonraki adımlara geçmeden ilk hatayı çözün. Bu yöntem sanal ortamı aktive etmez; Python'u tam yoluyla çağırdığı için PowerShell execution policy değiştirmenize gerek kalmaz. `python` bulunamıyor ama Windows Python başlatıcısı varsa ilk komutları `py -3 --version` ve `py -3 -m venv .venv` olarak kullanabilirsiniz.

**Yeni terminal açarsanız** `$repo`, `$proje`, `$python` değişkenleri kaybolur. Yeniden ayarlayın:

```powershell
$repo = 'C:\GERCEK\YOL\anything2explainer'
$proje = Join-Path $repo 'videolar\ilk-video'
$python = Join-Path $repo '.venv\Scripts\python.exe'
Set-Location $proje
```

`C:\GERCEK\YOL\...` kısmını kendi klasörünüzle değiştirin. Kullanıcı adınız Türkçe karakter içeriyorsa klasörünüzü yeniden adlandırmanız gerekmez; yolları tırnak içinde kullanın.

## 4B. macOS / Linux: ilk projeyi kurun

Repo kökünde, Node.js ve FFmpeg kurulu olduktan sonra:

```bash
repo="$PWD"
python3 -m venv "$repo/.venv"
source "$repo/.venv/bin/activate"
python -m pip install edge-tts==7.2.8 numpy pillow scipy
node --version
npm --version
ffmpeg -version
```

Şablon oluşturma yardımcısı **zsh ve rsync** kullanır. Sisteminizde yoksa paket yöneticinizle kurun. Örneğin Ubuntu/Debian'da `sudo apt install zsh rsync python3-venv ffmpeg`; macOS'ta Homebrew kullanıyorsanız `brew install ffmpeg`.

```bash
proje="$repo/videolar/ilk-video"
# Aşağıdaki hedef daha önce oluşturulmuşsa yeni bir ad seçin.
if [ -e "$proje" ]; then
  echo "Hedef zaten var; yeni bir proje adı seçin."
else
  zsh "$repo/template/scripts/new_project.sh" "$proje" turkce
fi
```

Hedef zaten varsa veya oluşturma hata verdiyse devam etmeyin. Yeni proje hazır olduğunda:

```bash
cp "$repo/examples/turkish/config.ts" "$proje/src/config.ts"
cp "$repo/examples/turkish/narration.txt" "$proje/script/narration.txt"
cd "$proje"
npm run typecheck
```

Yeni terminalde sanal ortamı yeniden aktive edin ve proje köküne geçin. Raspberry Pi / Linux ARM üzerinde Remotion'ın kullanacağı sistem Chromium'unu ayrıca kurmanız gerekebilir; `export REMOTION_BROWSER_EXECUTABLE=/usr/bin/chromium` ayarı `remotion.config.ts` tarafından okunur. Ayrıntılar ana README'nin Linux/ARM bölümündedir.

## 5. Türkçe sesi ve altyazıları üretin

**Video proje kökünde**, önceki projelerden kalan motor/ses/hız ayarlarını temizleyin ve varsayılan Türkçe sesi kullanın.

Windows PowerShell:

```powershell
Remove-Item Env:TTS_ENGINE,Env:VOICE,Env:RATE -ErrorAction SilentlyContinue
& $python -X utf8 scripts/tts_build.py
```

macOS/Linux (sanal ortam aktif):

```bash
unset TTS_ENGINE VOICE RATE
python -X utf8 scripts/tts_build.py
```

Beklenen sonuç: logda `lang=tr`, `engine=edge`, `voice=tr-TR-AhmetNeural`; `script/timeline.json` ve `public/assets/turkce/audio.wav` oluşur. Örnek iki cümle ve iki bölümden oluşur; sessizliklerle birlikte yaklaşık 20 saniyedir. Gerçek süre hizmetin ürettiği sese bağlıdır.

| Oluşan dosya | Ne işe yarar? |
|---|---|
| `public/assets/turkce/audio.wav` | Türkçe ses, 48 kHz stereo 16-bit |
| `src/common/timeline.ts` | Toplam kare sayısı, cümleler ve bölümler |
| `src/common/subs.ts` | Remotion'ın ekrana çizdiği altyazı blokları |
| `script/timeline.json` / `timeline.md` | Zamanların incelenebilir kaydı |
| `script/subtitles.srt` / `subtitles.vtt` | Harici oynatıcı veya editör için altyazı |
| `audio/cache/` | Aynı metin ve ses ayarının yeniden sentezlenmesini önleyen önbellek |

Emel sesine geçmek için PowerShell'de `$env:VOICE = 'tr-TR-EmelNeural'` yazıp TTS komutunu tekrar çalıştırın. macOS/Linux'ta `VOICE=tr-TR-EmelNeural python -X utf8 scripts/tts_build.py` kullanın. Yeni ses zaman çizelgesini değiştirir; sahneler yazıldıysa kare aralıkları da güncellenmelidir.

## 6. İlk MP4'ü alın

Video proje kökünde (PowerShell'de `npm` yerine `npm.cmd`, `npx` yerine `npx.cmd` kullanabilirsiniz):

```bash
npm run typecheck
npx remotion studio src/index.ts
```

Studio terminalde bir yerel adres gösterir. Tarayıcıda **`Video`** kompozisyonunu seçin. `Overlay` ve `G1`–`G8` önizlemeleri sesi içermez; ses için `Video` gerekir. Studio çalışırken ikinci bir terminal açıp video proje köküne geçin veya Studio'yu `Ctrl+C` ile durdurun. Ardından:

```bash
npx remotion render src/index.ts Video renders/ilk-video.mp4 --codec=h264 --concurrency=2
```

**İlk başarılı çıktı:** `videolar/ilk-video/renders/ilk-video.mp4`. Başlık, Türkçe ses, altyazı, üst bilgi ve bölüm çubuğu görünmelidir. Orta alanın çoğunda arka plan olması normaldir: `examples/turkish/` bir ses/altyazı testidir; `SHOTS_G1`–`SHOTS_G8` henüz boş olduğu için konu anlatan çizimler içermez.

## 7. Kendi konunuzdan tam video oluşturun

### Ajanı projeye bağlayın

Codex veya Claude Code'u sağlayıcının [Codex başlangıç](https://developers.openai.com/codex/quickstart) / [Claude Code başlangıç](https://code.claude.com/docs/en/quickstart) yönergeleriyle kurup oturum açın. **Yerel dosyaları okuyabilen, düzenleyebilen ve terminal komutları çalıştırabilen kodlama ortamını** kullanın.

İlk kullanımda kalıcı skill kaydı şart değildir: ajan içinde **repo kökünü** açın ve aşağıdaki istemle `SKILL.md` dosyasını açıkça okutun. Böylece `reference/`, `template/` ve `examples/` dosyalarına erişebilir. Yalnızca oluşturduğunuz video klasörünü açtıysanız repo kökünün tam yolunu da belirtip ajanın o konuma erişebildiğini doğrulayın.

Kalıcı kullanım için kullandığınız istemcinin [Codex skill](https://developers.openai.com/codex/skills) veya [Claude Code skill](https://code.claude.com/docs/en/skills) yönergelerine göre **bütün depo klasörünü** skill olarak erişilebilir kılın; tek başına `SKILL.md` kopyalamak referansları ve şablonu taşımaz. Depodaki eski symlink örneklerinin hedef yolu istemci sürümünüze göre değişebilir. Kayıt sonrası skill'in listelendiğini kontrol edin; görünmüyorsa doğrudan dosya okutma yöntemiyle ilerleyin.

### Kopyalanabilir başlangıç istemi

Aşağıdaki metni **ajanın sohbetine** yapıştırın; terminal komutu değildir. Konuyu ve hedef kitleyi değiştirin:

```text
Bu klasördeki anything2explainer reposunu kullanarak bir video üret.
Önce SKILL.md, README_TR.md ve reference/narration-guidance.md dosyalarını oku.

Konu: İnternet üzerinden bir mesaj karşı tarafa nasıl ulaşır?
Hedef kitle: Teknik bilgisi olmayan yetişkinler.
Süre: Yaklaşık 3 dakika.
Dil: Türkçe; src/config.ts içinde lang: 'tr'.
Ses: Edge TTS, tr-TR-AhmetNeural, RATE=+0%.
Görünüm: Reponun siyah zemin, beyaz çizgiler ve mor vurgu stili; bg: 'stars'.
Yeni proje: videolar/mesaj-yolculugu. Mevcut ilk-video testini koru.

Araştırmayı kaynaklarıyla yap. Türkçe senaryo ve bölüm planını bana göster.
Metni onayladıktan sonra ses ve zaman çizelgesini üret.
Her cümle için mekanizmayı anlatan sahne kodu yaz; yalnızca altyazılı arka planla bırakma.
İlk 30 saniyeyi hazırlayıp onayımı al, ardından kalan sahneleri tamamla.
Araştırma, storyboard, sahne kodu, kalite raporu, MP4 ve SRT/VTT teslim et.
Çalıştığın işletim sistemine uygun komutları kullan. Alt ajanlar varsa sahneleri
gruplara böl; yoksa aynı aşamaları sırayla tamamla.
Python için repo kökündeki .venv ortamını kullan.
```

Senaryonuz zaten hazırsa konu yerine dosya yolunu ekleyin: “Senaryo kaynağım `senaryom.txt`; anlatımı koru, gerekli altyazı bölmelerini ve sahne planını hazırla; anlam değişikliklerini önce göster.” Düz metin için doğrudan kopyalama yeterli olabilir; PDF veya bağlantıların önce ajan tarafından okunup senaryo formatına dönüştürülmesi gerekir. `tts_build.py` PDF/URL okuyucusu değildir.

### Dört karar noktası

| Nokta | Sizin belirlediğiniz | Neden burada? |
|---|---|---|
| Süre ve dil | Kapsam, hedef kitle, Türkçe | Araştırmanın derinliğini ve senaryonun boyunu belirler |
| Senaryo | Tam metin, bölümler, doğruluk | Ses üretiminden önce değişiklik yapmak kolaydır |
| Ses | Ahmet, Emel veya kendi sesiniz | Tüm kare zamanları gerçek sesin süresinden çıkar |
| İlk 30 saniye | Görünüm, okunabilirlik, tempo | Görsel dil tüm sahnelere yayılmadan kontrol edilir |

Başlangıç isteminde süre, dil ve ses verilmişse ajan bunları kullanabilir; eksik tercihleri netleştirir. Senaryo ve pilot için verdiğiniz onaylar üretimi ilerletir. Repo süre için 1–3 saatlik örnek tahminler verir; donanım, ajan, sahne sayısı ve düzeltmeler bu süreyi değiştirir.

## 8. Ajanın yazacağı dosyalar ve üretim sırası

1. **Araştırma:** Kaynaklı notlar `research/` altında. Özgün akış `research/调研.md` adını kullanır; Çince dosya adları araçların beklediği yerlerde korunabilir, dosya içeriği Türkçe olabilir.
2. **Senaryo:** `script/narration.txt`. Bir satır bir cümle; `# CHAPTER 1 Giriş` bölüm açar. `Bir mesaj yazarsınız.|Gönder tuşuna basarsınız.` gibi `|` ile altyazı bölünür. Türkçe blok başına 42 karakter hedeflenir; bloklar sese gönderilirken boşlukla birleşir.
3. **Ses ve zaman:** `scripts/tts_build.py`. Seslendirme gerçek cümle ve kelime sürelerini sağlar; üretilen karelere göre tasarım yapılır.
4. **Storyboard:** `script/storyboard_src.md`. Her sahnenin görseli, hareketi, odak öğesi, ışığı ve zamanı yazılır. `{S01.from}`, `{S01.to}`, `{S01.c2}`, `{C2}` ve `{TOTAL}` yer tutucuları `python -X utf8 scripts/render_storyboard.py` ile doldurulur; çıktı `分镜表.md` olur.
5. **Görsel ayarlar:** `src/config.ts`, gerekirse `src/ui.tsx` ve `src/fx.tsx`. `title`, `hud`, `chapterTech`, `rails`, `credit` metinleri konuya göre Türkçeleştirilir. `slug`, `public/assets/<slug>/audio.wav` yolunu belirler.
6. **Sahne kodu:** `src/shots/G1/SC01.tsx` gibi React bileşenleri. Bileşenleri yazmak tek başına yetmez; grubun `index.ts` dosyasında `SHOTS_G1` listesine `{id, from, to, Comp}` olarak eklemek gerekir. Şablon G1–G8'i `Main.tsx` içinde birleştirir. G9 ve sonrası gerekirse `Main.tsx` ve `Root.tsx` kayıtları da eklenir.
7. **Pilot, üretim, kontrol:** İlk grup render edilir; onaydan sonra kalan gruplar yapılır. `npm run typecheck`, statik kontroller ve kare incelemesi uygulanır.
8. **Son render ve teslim:** `renders/<film>.mp4`, altyazılar, kaynak proje ve kalite notları verilir.

`npm install`, `tts_build.py` veya render komutu konuya özel TSX sahneleri kendiliğinden yazmaz. Bu, AI kodlama ajanının veya sizin işinizdir. AI olmadan çalışıyorsanız aynı dosya sırasını elle uygulayın; React/TypeScript ve Remotion bilgisi gerekir.

## 9. Kendi filminizin önizlemesi ve kalite kontrolü

Video proje kökünde, toplam video en az 900 kareyse ilk 30 saniye:

```bash
npx remotion render src/index.ts Video renders/pilot.mp4 --frames=0-899 --codec=h264 --concurrency=2
```

Kısa test için `0-899` kullanmayın: son kareyi `TOTAL_FRAMES - 1` ile sınırlayın veya bütün testi render edin. Remotion CLI 0'dan, repo zaman çizelgesi 1'den başlayan kare numarası kullanır.

Tam film ve kareler için (klasörleri önceden oluşturun):

```bash
npm run typecheck
npx remotion render src/index.ts Video renders/film.mp4 --codec=h264 --concurrency=2
ffmpeg -i renders/film.mp4 -q:v 4 fin_frames/f_%04d.jpg
```

`fin_frames`, `qc` ve `renders` yoksa PowerShell'de `New-Item -ItemType Directory -Path fin_frames,qc,renders -Force`, macOS/Linux'ta `mkdir -p fin_frames qc renders` kullanın. Her sürüm için yeni/boş bir kare klasörü kullanın; eski filmden artan kareler analizi etkiler. Yukarıdaki FFmpeg komutu kare dosyaları zaten varsa üzerine yazmayı sorar.

Storyboard ve sahneler hazır olduktan sonra, macOS/Linux'ta aktif sanal ortamla:

```bash
python -X utf8 scripts/selfcheck.py
python -X utf8 scripts/sheet.py fin_frames renders/kareler.html 60
python -X utf8 scripts/frame_metrics.py --out qc/kare-olcumleri.md
python -X utf8 scripts/motion_check.py --frames fin_frames
```

Windows'ta bu dört komutun `python` bölümünü `& $python` olarak değiştirin. `motion_check.py G1` gibi grup önizleme yolu sistemde `npx` çağırır; Windows'ta sorun yaşarsanız gösterilen **önceden çıkarılmış karelerle `--frames`** yolunu kullanın. Shell yardımcılarını Windows PowerShell'de doğrudan çalıştırmayın.

Kontrol betikleri storyboard'un tablo biçimine ve bazı özgün başlıklara dayanır. Ajanın `reference/` içindeki biçimi korumasını isteyin. “0 sahne bulundu” sonucu kalite onayı değildir. `selfcheck.py` ve hareket analizi raporlarını okuyun; yalnızca süreç çıkış koduna bakmak yeterli değildir.

İzleyerek kontrol edin: ses doğru mu, her altyazı okunabiliyor mu, bölüm geçişleri düzgün mü, görseller söylenen şeyi açıklıyor mu, boş sahneler veya kaynak dışı iddialar var mı? Sayısal metrikler bu insan/ajan incelemesini tamamlar.

## 10. Sorun giderme

| Sorun | Yapılacak işlem |
|---|---|
| `package.json` bulunamıyor | Repo kökünden video proje köküne geçin; `template/` içeriğini oraya kopyalamış olmalısınız |
| `numpy`, `edge_tts`, `PIL` veya `scipy` yok | Betiği, paketleri kurduğunuz `.venv` Python'uyla çalıştırın |
| PowerShell `npm.ps1` çalıştırmıyor | `npm.cmd` ve `npx.cmd` kullanın; sistem execution policy'sini değiştirmek gerekmez |
| `ffmpeg` bulunamıyor | FFmpeg'in `bin` klasörünü PATH'e ekleyin ve terminali yeniden açın |
| Ses İngilizce/Çince veya yanlış ses hatası | `src/config.ts` içinde `lang: 'tr'`; eski `VOICE`, `RATE`, `TTS_ENGINE` ortam değişkenlerini temizleyin |
| Kokoro Türkçeyi reddediyor | `TTS_ENGINE=auto` veya `edge` kullanın; Türkçe varsayılanı Kokoro değildir |
| Edge TTS bağlantı hatası / boş ses | İnternet ve servis erişimini kontrol edin, yeniden deneyin; betik sınırlı sayıda tekrar dener |
| `audio.wav` bulunamıyor | Önce TTS çalıştırın; `config.slug` ile varlık klasörünün eşleştiğini kontrol edin |
| Altyazı var ama çizim yok | `SHOTS_Gn` boş olabilir veya yeni bileşen grubun `index.ts` listesine eklenmemiştir |
| Studio'da ses yok | `Video` kompozisyonunu seçin; grup ve Overlay önizlemeleri sessizdir |
| `S03` gibi cümle bulunamadı | `hud` / `rails` kayıtlarını üretilen `SENTENCES` kimlikleriyle eşleştirin |
| Türkçe harfler bozuk | Metni UTF-8 kaydedin; güncel Noto Sans dosyalarını kopyalayın; `FONT_HEAVY` kullanın |
| Altyazı taşıyor | Metni kelime sınırında `|` ile daha kısa bloklara bölün, TTS ve zamanları yeniden üretin |
| Altyazı zamanları için tahmin uyarısı | İlgili blokları dinleyin; sayı, kısaltma veya bölünmüş ekleri daha doğal yazın |
| Senaryo/ses değişti, sahneler kaydı | TTS → storyboard → sahne kareleri → render sırasıyla yeniden oluşturun |
| Tarayıcı indirme/başlatma hatası | Remotion'ın indireceği tarayıcıya erişimi kontrol edin veya `REMOTION_BROWSER_EXECUTABLE` ile kurulu Chrome/Chromium yolunu verin |
| Render sırasında bellek yetmiyor | `--concurrency=1` deneyin; paket, font ve ses dosyalarını silmeden boş disk alanını kontrol edin |
| QC “0 sahne” gösteriyor | Storyboard'un sahne satırları ve kare aralıkları beklenen biçimde olmalı |

PowerShell'de yerel Chrome örneği: `$env:REMOTION_BROWSER_EXECUTABLE = 'C:\Program Files\Google\Chrome\Application\chrome.exe'`. Yolun sizde mevcut olduğunu doğrulayın; sonra render komutunu tekrar çalıştırın. Bu değişken `template/remotion.config.ts` üzerinden okunur.

## 11. Yeniden üretim, paylaşım ve lisans

Video başına ayrı klasör tutun. Bir filmi paylaşırken `src/`, `script/`, gerekli `public/` varlıkları, `package.json`, oluşan `package-lock.json`, ayarlar ve araştırma/kalite notlarını da saklayın. Yalnızca MP4'ü paylaşmak izleme için yeterlidir; yeniden düzenleme için kaynak proje gerekir. `audio/cache/` hız kazandırır ama zorunlu teslim dosyası değildir. `node_modules/` yeniden kurulabilir.

Kaynak kod açıkça erişilebilir olsa da depodaki lisans **PolyForm Noncommercial**'dır. `LICENSE` dosyası aracın ticari kullanımında yazarın önceden iznini ister; üretilen videoların üreticisine ait olduğunu belirtir. Fontlar ayrı OFL lisanslarıyla gelir. [LICENSE](LICENSE), [font lisansları](template/public/fonts/LICENSE.md) ve [Remotion lisans koşulları](https://www.remotion.dev/license) ilgili metinlerdir.

## 12. Başarı kontrolü

- [ ] Türkçe desteği içeren repo sürümünü indirdim.
- [ ] Bağımlılıkları kurdum; doğru Python ve proje klasöründeyim.
- [ ] Ahmet veya Emel ile gerçek `audio.wav` oluştu.
- [ ] İlk test MP4'ünde ses, altyazı ve Türkçe harfler doğru.
- [ ] Kendi filmim için ajan senaryo ve kaynaklı araştırma hazırladı.
- [ ] Senaryoyu ve ilk 30 saniyeyi onayladım.
- [ ] Konuya özel sahneler yazıldı ve `SHOTS_Gn` listelerine eklendi.
- [ ] Son videoyu izledim; kalite raporları gerçek sahneleri inceliyor.
- [ ] MP4, SRT/VTT ve yeniden düzenlenebilir proje dosyalarını sakladım.

Bu rehberin teknik dayanakları: [SKILL.md](SKILL.md), [proje oluşturucu](template/scripts/new_project.sh), [TTS üreticisi](template/scripts/tts_build.py), [sahne birleştirici](template/src/Main.tsx), [kompozisyon kayıtları](template/src/Root.tsx), [senaryo ve storyboard kuralları](reference/narration-storyboard.md). HTML rehberde aynı akışı etkileşimli zaman çizelgesiyle inceleyebilirsiniz.
