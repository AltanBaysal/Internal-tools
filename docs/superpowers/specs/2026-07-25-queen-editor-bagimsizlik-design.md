# Queen Editor — collab-toolbox'tan bağımsızlık (tasarım)

**Tarih:** 2026-07-25 · **Durum:** onaylandı, uygulama bekliyor
**Değiştirdiği spec:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md) — Drive kökü kararı
**İlgili:** [Bölüm 3 spec](2026-07-25-queen-editor-b3-proje-design.md) · [yol haritası](../plans/2026-07-24-queen-editor-roadmap.md)

## Amaç

Queen Editor, `collab-toolbox/` altındaki photo generator notebook'larından **bağımsız bir ürün**.
Motorun kendisini (nova-3dcg ComfyUI grafiği) ve kanıtlanmış davranışını kullanmaya devam eder, ama
o notebook'ların dosyalarına, Drive klasörüne veya kodun kendisine bağlı değildir. Bu spec o sınırı
yazıya döker ve sınırı ihlal eden tek kararı — paylaşılan Drive kökü — devirir.

## Bağlam

- Şemsiye spec, projeleri `MyDrive/photoGenV2/<ad>/` altına koyuyordu; gerekçe "fotolar eski
  fotoların yanında dursun"du.
- Ama `photoGenV2` **nova-3dcg notebook'unun kendi klasörü** ve boş değil:
  `workflow_api.json` (kullanıcının Export (API)'ı) + `output/` (notebook'un yazdığı fotolar).
- Queen Editor kökün **her alt klasörünü proje sayar** (`list_dirs` → kart). Yani gerçek Drive'da
  Projeler ekranı `output` diye bir **hayalet proje kartı** gösterirdi. Paylaşımın kazancı da yoktu:
  `workflow_api.json` Queen Editor'de Drive'dan değil **repodan** okunuyor (şemsiye kararı).
- Kullanıcı kararı (2026-07-25): batch üretim mantığı **alınacak** — ama o notebook kullanılamadığı
  için kodu Queen Editor'ün kendi Python'unda yazılacak: *"aynı mantıkta kod yazacağız… sadece aynı
  notebook'u kullanamayacağız."*

## Kararlar

| Karar | Gerekçe |
|---|---|
| Drive kökü **`MyDrive/queenEditor/<proje>/`**; `photoGenV2` hiç kullanılmaz | Kullanıcı kararı. Kök yalnız Queen Editor'ün: yabancı alt klasör (`output/`) hayalet kart üretmez, iki araç birbirinin dosyalarına dokunmaz, kodda "bunlar proje değil" gizli filtresi taşımak gerekmez. Yeni kök **boş başlar** — eski klasörden hiçbir şey taşınmaz, `photoGenV2` olduğu gibi kalır. |
| **Bağımsızlık ilkesi:** Queen Editor çalışma zamanında `collab-toolbox/` altındaki hiçbir notebook'a, dosyaya veya Drive klasörüne bağlı değil | Kullanıcı kararı ("ayrı olacak"). Bağımlılık olsaydı iki araç birbirini kırardı: notebook'un CONFIG'i değişince arayüz bozulur, Drive klasörü yeniden düzenlenince projeler kaybolurdu. Devralınan tek şey **bilgi** (aşağıdaki tablo). |
| Batch üretim **davranışı aynı**, **kodu Queen Editor'ün kendi Python'u** | Kullanıcı kararı. `api.ipynb`'nin mantığı (plan, varyant, numaralandırma, seed, hata politikası, devam) doğru ve kanıtlı; ama tek hücrede, CONFIG'e gömülü ve test edilemez hâlde. Queen Editor aynı davranışı katmanlı ve testli yazar: `services/comfy/` (grafiğe enjekte et → bytes) + `features/generation/` (plan, kuyruk, politika). Notebook'tan kod kopyalanmaz, import edilmez. |
| `queen-editor/` **bu repoda kalır** | Bağımsızlık işlevsel; depo değil. Notebook uygulamayı bu repodan `git clone` ile alıyor (Bölüm 1-2'de kanıtlandı) — repoyu ayırmak o akışı yeniden kurmak olurdu, karşılığında bir kazanç yok. |
| `nova-3dcg` notebook'larına **dokunulmaz** | Onlar çalışıyor ve kullanılmaya devam edecek. Bu spec yalnız `queen-editor/` ve Queen Editor dokümanlarını değiştirir. |
| Klasör adı **tek düğme**: notebook CONFIG'indeki `DRIVE_FOLDER`. Kod, yorum ve docstring adı tekrar etmez — "Drive kökü" der, yolu `QE_DRIVE_ROOT`'tan alır | Kullanıcı kararı ("değiştirmesi kolay olsun, hardcoded olmasın"). Ad üç yerde yazılı olsaydı yarın `queenEditor` → başka bir şey olduğunda ikisi güncellenip biri kalırdı; `config.py`'deki tam yol bilinçli olarak yalnız yedek varsayılan. `docs/superpowers/**` istisna: onlar tarihli kayıt. |
| Grafiğin repo kopyası (`queen-editor/workflow_api.json`) **Bölüm 4'te** gelir | Kullanıcı kararı: "şu an foto üretimi yapmayacaksak şimdi yapmayalım." Şimdi kullanılmayan bir dosya repoya girmez. Sınır yine yazılı: Bölüm 4 grafiği `collab-toolbox`'tan **okumaz**, kendi kopyasını alır. |

## Bağımsızlık sınırı

| Devralınır (bilgi) | Devralınmaz (bağımlılık) |
|---|---|
| ComfyUI grafiği — `queen-editor/` altına **kendi kopyası** olarak (Bölüm 4'te, üretimle birlikte) | `collab-toolbox/photo_generator/nova-3dcg/workflow_api.json`'u okumak ya da Drive'daki kopyasını |
| Enjeksiyon node id'leri: `PROMPT_NODE = "3"`, `NEGATIVE_NODE = "4"`, `SEED_NODE = "40"` | `api.ipynb`'nin CONFIG hücresi |
| Kurulum bilgisi: 7 custom node paketi, 5 model, ComfyUI headless — `app.ipynb`'de **kendi hücreleri** | `nova-3dcg/api.ipynb`'nin hücrelerini çalıştırmak veya ona referans vermek |
| Davranış desenleri: `ComfyClient` akışı (`POST /prompt` → `/history` → `/view`), `describe_comfy_error` / `is_infra` ayrımı, üst üste 3 hatada durma, cloudflared tüneli | O fonksiyonların kodunun kopyalanması — Queen Editor kendi katmanlarına yazar |
| Çıktı adlandırma fikri: `N_a.png … N_d.png` | `photoGenV2/output/` klasörü |

Kural tek cümlede: **grafik ve gerekçe ortak, kod ve klasör ayrı.**

## Etki

### Kod (Bölüm 3'te yazılan)

Bölüm 3 kökü ortam değişkeninden okuyor, o yüzden kod değişikliği küçük:

| Dosya | Değişiklik |
|---|---|
| `backend/config.py` | `DRIVE_ROOT` varsayılanı `/content/drive/MyDrive/queenEditor` |
| `backend/features/projects/data/project_store.py` | docstring'deki yol (`queenEditor/<name>/`) |
| `app.ipynb` | CONFIG'de `DRIVE_FOLDER = "queenEditor"`; başlık markdown'ındaki yol |
| `README.md` | iki yerde yol |

Test değişmez: testler `tmp_path` kullanıyor, gerçek yola bağlı değil. 42 test aynen geçer.

### Dokümanlar

| Dosya | Değişiklik |
|---|---|
| [şemsiye spec](2026-07-24-queen-editor-v1-design.md) | Drive kökü karar satırı + Drive düzeni şeması + doğrulama adımı 3; bu spec'e link |
| [yol haritası](../plans/2026-07-24-queen-editor-roadmap.md) | Bölüm 3 satırındaki klasör yolu |
| [Bölüm 3 spec](2026-07-25-queen-editor-b3-proje-design.md) + [planı](../plans/2026-07-25-queen-editor-b3-proje.md) | yollar; kararın gerekçesi olarak hayalet kart notu |

### Bölüm 4-7'ye etkisi

Sıra ve kapsam değişmez. Netleşen: `services/comfy` ve `features/generation` **sıfırdan yazılır**
(notebook'tan kopyalanmaz), `app.ipynb` kendi kurulum hücrelerini taşır, üretilen fotolar
`queenEditor/<proje>/` altına iner.

## Doğrulama

1. `queen-editor/` içinde `photoGenV2` araması **hiç sonuç vermez**; `collab-toolbox/` ve
   nova-3dcg dokümanlarındaki `photoGenV2` geçişleri **olduğu gibi durur**.
2. `pytest` → 42 test geçer (yol testlere girmiyor).
3. Colab Run all → `✓ Drive bağlı — proje kökü: /content/drive/MyDrive/queenEditor`.
4. Projeler ekranı **boş** açılır — `photoGenV2/output` diye hayalet kart yok.
5. Yeni proje → `MyDrive/queenEditor/<ad>/` oluşur; `photoGenV2` klasörü değişmez.

## Riskler

- **Motor iki yerde kurulur.** Model listesi veya custom node sürümü değişirse iki notebook ayrı
  güncellenir. Bilinçli bedel — şemsiye spec'te de böyle yazılı; bağımsızlığın fiyatı bu.
- **Grafik kopyası eskiyebilir.** `queen-editor/workflow_api.json`, ComfyUI'da ayar değiştikçe
  yeniden export edilip commit'lenmeli; aksi hâlde iki araç aynı prompt'tan farklı sonuç verir.
- **Aynı GPU'da iki ComfyUI çalıştırmak** (nova-3dcg notebook'u ve Queen Editor aynı anda) belleğe
  sığmaz. İkisi ayrı Colab oturumlarında kullanılır — v1'de kısıt değil, bilinmesi gereken bir sınır.

## Kapsam dışı

`photoGenV2` içindeki mevcut verinin taşınması veya silinmesi · `nova-3dcg` notebook'larında herhangi
bir değişiklik · repo ayrımı · grafiğin repo kopyasının şimdi alınması (Bölüm 4) · Queen Editor'ün
ComfyUI'a custom node olarak gömülmesi · model kurulumunun iki araç arasında paylaşılması (ör. ortak
Drive model cache).
