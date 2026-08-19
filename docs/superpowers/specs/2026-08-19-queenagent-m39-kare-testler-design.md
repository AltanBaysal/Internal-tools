# Madde 39 — Shot düşer, frame gelir · Test Turu Tasarım Belgesi

**Tarih:** 2026-08-19 · **Branch:** `fix/mira` · **Madde:** [v3 yol haritası Madde 39](../plans/2026-08-18-queenagent-v3-roadmap.md)
**Kaynak:** [test bulguları, bulgu 9](../research/2026-08-18-queenagent-test-bulgulari.md)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

Bu belge **yalnız testlerin** turuna aittir. Kodun nasıl değişeceği uygulama turunun belgesinde.

---

## 1 · Neden kelime değişiyor

"Shot" süre ve kamera hareketi çağrıştırıyor; üretilen şey tek durağan görüntü. Türkçe konuşurken
zaten "kare" deniyor, ve iki kelimenin arasındaki boşluk her turda modelin de kullanıcının da
kafasını karıştırıyor.

Bu bir yeniden adlandırma maddesi: davranış değişmiyor, **kelime** değişiyor. Bir istisnası var ve
o da adlandırmanın kendisinden geliyor — denetleyen beceri kare adı taşımayacak, çünkü karelere
değil promptların malzemesine bakıyor.

## 2 · Değişen ve değişmeyen

| Ne | Bugün | Yarın |
|---|---|---|
| Yapı dosyasındaki liste | `"shots"` | `"frames"` |
| Hata satırı | `shot 3: …` | `frame 3: …` |
| Yapı dosyasının adı (yönergede) | `intro-shots.json` | `intro-frames.json` |
| Bölen beceri | `split-into-shots` · "Split into shots" | `split-into-frames` · "Split into frames" |
| Denetleyen beceri | `verify-shots` · "Verify shots" | `verify-prompts` · "Verify prompts" |
| Denetleyenin menü satırı | "Check the structure against the rules." | "Check the structure files against the rules." |
| Yönerge metinlerindeki "shot" | her yerde | "frame" |

Değişmeyen: `generate-prompts` ve `generate-prompts-plus`'ın kimlikleri, `-plain` eki, üretilen
Python dosyasının adı (kaynağın adından türüyor, bugün de öyle).

## 3 · Eski dosyalar ve eski sohbetler kırılmaz

**Eski yapı dosyası:** listesi `"shots"` altında olan bir dosya okunmaya devam eder. Kullanıcının
diskinde bugünden kalma dosyalar var ve bir yeniden adlandırma onları çöpe çeviremez.

**Eski sohbet:** kaydında `verify-shots` yazan bir sohbet, kimsenin tanımadığı bir beceri adı
taşıyor demektir. İki taraf da bunu **zaten** biliyor: `instruction_for` tanımadığı ada boş dize
veriyor ("a record can name one that has since been renamed"), `skillName` de tanımadığı kimliği
ham hâliyle gösteriyor. Yeni bir koruma yazılmıyor — var olan davranış çiviliyor.

## 4 · Testler ne çiviliyor

**`test_build_prompts.py`** — dosyanın bütün sözlüğü `frames`'e döner, üstüne iki test:

| # | Durum | Beklenen |
|---|---|---|
| 1 | Listesi `"frames"` altında olan yapı | Promptlar üretilir |
| 2 | Listesi `"shots"` altında olan eski yapı | Aynı promptlar üretilir |
| 3 | İkisini de taşıyan yapı | `frames` kazanır |
| 4 | Bilinmeyen ad | Hata satırı **`frame 1`** der |
| 5 | Listesi boş yapı | Reddedilir, cümle "frame" kelimesini kullanır |

**`test_skills.py`** — kimlik listesi yeni adlarla; üstüne:

| # | Durum | Beklenen |
|---|---|---|
| 6 | `split-into-frames`, `verify-prompts` | Yönerge taşır |
| 7 | `split-into-shots`, `verify-shots` | Boş dize — tanınmayan ad |
| 8 | Bütün yönergeler | Hiçbirinde "shot" kelimesi geçmez |
| 9 | Yapılandırılmış yönerge | Şemada `"frames"` alanı görünür, `intro-frames.json` adı geçer |
| 10 | Denetleyen yönerge | "prompts" üzerinden konuşur, kare adı taşımaz |

**`test_tools.py`** — `build_prompts` tool'unun tarifi "frame" der.

**Ön uç (`skills.test.js`, `SkillPicker.test.jsx`, `App.test.jsx`, `ChatScreen.test.jsx`)** —
kimlikler ve görünen adlar yeni hâliyle; menü satırının metni yeni cümlesiyle.

8 numaralı test bu maddenin süpürgesi: tek tek aramak yerine bütün yönergelerde kelimeyi arıyor,
böylece gözden kaçan bir cümle sessizce kalamıyor.

## 5 · Testlerin bakmadığı yer

Kare açıklamasının ne kadar uzun olacağı (Madde 43) ve hangi dilde geleceği (Madde 44) bu maddenin
konusu değil — o iki madde aynı yönergeyi yeniden yazacak. Burada yalnız kelime değişiyor.

`FilePanel.test.jsx`'teki `shots.json` sabiti de yeni adı alır; bir test verisi, ama sözlüğün
tamamının dönmesi kuralın kendisi.

## 6 · Kabul ölçütü — kırmızının doğru olması

1. Yeniden adlandırılmış her test **düşer**: alan adı, hata satırı, beceri kimliği, görünen ad.
2. 2 numaralı test (eski `"shots"` okunur) **geçer** — bugünkü tek okuma yolu zaten o.
3. 7 numaralı test (eski kimlikler boş döner) **düşer**: `split-into-shots` bugün tanınan bir ad,
   yönerge veriyor. Boş dönmesi ancak adın kalkmasıyla doğru olur.
4. `skip` yok, `xfail` yok.
5. Düşen her testin sebebi kelime; başka bir sebeple düşen test varsa durulur.

## 7 · Risk

Yeniden adlandırma geniş ama sığ: on altı dosyaya dokunuyor, hiçbirinde mantık değişmiyor. Asıl
risk gözden kaçan bir cümle, ve 8 numaralı süpürge testi tam olarak onun için var.
