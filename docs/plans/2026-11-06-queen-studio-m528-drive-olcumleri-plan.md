# Madde 528 · Drive'ın ölçümleri — plan

[Tasarım](../specs/2026-11-06-queen-studio-m528-drive-olcumleri-design.md). Ölçüm maddesi: ürün kodu
yok, betiklerin testi yok; her deney önce küçük sayılarla bir kez denendi (`tmp/m528/debug.py`).

1. **Ortak parça.** `queen-studio/measurements/drive/common.py`: token yolundan istemci, iş parçacığı
   başına bir bağlantı, her denemeyi ayrı ölçen ve 403/429'da üstel bekleyen çağrı, istatistik,
   geçici dosya + yerine koyma ile yazma. `requirements.txt`: Google kütüphanelerinin sürümleri.
2. **Deneyler.** `consistency.py` (kimlikle okumanın güncelliği, içerik + etiket, yarıda kesilen
   yükleme, listenin gecikmesi); `scale.py` (1.000 dosyanın sayfaları, 2.000 dosyalı klasörü çöpe
   atmak, 500 güncellemenin sürümleri ve kota); `naming.py` (ayrılmış kimlikler, `name contains`);
   `durations.py` (çağrı süreleri); `rate_limit.py` (dört süreç).
3. **Koşturucu.** `run.py`: tek kök klasör, her deneye alt klasör, her sonucu bitince
   `tmp/m528/<makine>/<deney>.json`'a yazar, sonda kökü çöpe atar.
4. **Bu makinede koşu.** `run.py --host local --reserve-pending`, sonra `rate_limit` ve
   `trash_limit` (koşuda eklendi; tasarım, Sonuçlar 7b).
5. **Colab'da koşu.** CPU oturumu; betikler ve token `colab upload`; `run.py --host colab` arkada;
   sonuçlar `colab download`; token VM'den silinir; `colab stop`.
6. **Kayıt.** `summarize.py` → `queen-studio/measurements/drive.json`; `check_reserved_ids.py`
   sonraki günlerin bakışı için. Tasarımın Sonuçlar bölümü.
7. **Kontrol.** ruff (suite'in `test_checks.py`'si `measurements/`'ı da tarar) ve queen-studio'nun
   Python suite'i.
