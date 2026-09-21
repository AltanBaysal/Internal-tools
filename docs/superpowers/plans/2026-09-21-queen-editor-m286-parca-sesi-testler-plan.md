# Madde 286 · Parçaların ses akışı — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m286-parca-sesi-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `FakeRun` sesi de cevaplıyor:** `sounds` eşlemesi — dosya adı → `"48000:stereo"`, ya da sesi
olmayan için boş satır. Ses sorusu `a:0` taşıdığı için ölçü sorusundan ayırt ediliyor.
**Varsayılan: hiçbirinin sesi yok**, yani ses söylemeyen mevcut testler tek düzenli bir set
soruyor ve davranışları değişmiyor.

**2 · Olgu 1'in testi:** her parçaya sesi soruluyor, parça başına bir kez.

**3 · Olgu 2 ve 3'ün testi:** karışık sette sessiz parçaya `anullsrc` ile ses yazılıyor, video
kopyalanıyor, ve sessizliğin hızı/kanal düzeni sesli parçadan geliyor.

**4 · Olgu 4'ün testi:** hepsi sesli ve hiçbiri sesli setlerde yazma çağrısı yalnız
birleştirmenin kendisi.

**5 · Olgu 5'in testi:** `concat` listesi sessiz parçanın yerine sesli kopyasını yazıyor, sıra
korunuyor.

**6 · Takım:** dört satır paralel, verbatim. Kırmızı yalnız queen-editor arka ucunda; mevcut
birleştirme testleri yeşil kalmalı.

**7 · Commit** (kırmızı).
