# Madde 224 · Arşiv ekranı kendi düğmelerini taşıyacak — uygulamanın tasarımı

**Test turu:** [tasarım](2026-09-16-queen-editor-m224-arsiv-ekrani-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı duran dört çivi tek bir değişiklik istiyor, ve o da tek dosyada:
[`ProjectsScreen`](../../../queen-editor/frontend/src/features/projects/ProjectsScreen.jsx)'in
başlığındaki düğme öbeği.

## Ne çizilecek

Bugün öbek iki listede de aynı: bir anahtar *(`inArchive ? "Projeler" : "Arşiv"`)* ve **Yeni proje**.
Bundan sonra öbek hangi listeye bakıldığına göre **ayrışıyor**:

```
inArchive  ->  [ Arşivden çık ]                        (ghost)
projeler   ->  [ Arşiv ] [ + Yeni proje ]              (bugünkü hâli)
```

**Girişin görünüşü değişmiyor.** *Arşiv* düğmesi bugünkü `wf-btn`'ünü koruyor: kullanıcının sorduğu
şey çıkıştı, ve sormadığı bir düğmeyi de değiştirmek maddeyi genişletmek olurdu.

**Çıkış ghost**, çünkü taklit ettiği şey ghost:
[`ProjectScreen`](../../../queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx)'in
*Projeden çık*'ı. Aynı yerde, aynı ağırlıkta, aynı kalıpta bir kelime.

**Yeni proje arşivde hiç çizilmiyor** — `disabled` değil. Kapalı bir düğme *"burada da olabilirdi"*
der, oysa orası onun yeri değil.

## Ne değişmiyor

- `toggleArchive` aynı işlevi görüyor: iki düğme de onu çağırıyor, çünkü yapılan iş aynı iş —
  yalnız bir tanesi girmek, öteki çıkmak diye adlanıyor.
- Başlığın ortasındaki `inArchive ? "Arşiv" : "Projeler"` duruyor; düğme artık onunla aynı kelimeyi
  söylemediği için ekranda hiçbir kelime iki kez geçmiyor — 221'deki kural kendiliğinden korunuyor.
- `modalOpen`, `NameModal` ve proje açma yolu **hiç ellenmiyor**. Arşivde açacak düğme kalmadığı
  için pencereye giden yol da kalmıyor.
- Arka uç, rotalar, `api.js`: hiçbiri.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `frontend/src/features/projects/ProjectsScreen.jsx` | başlıktaki düğme öbeği ikiye ayrılıyor |
| `frontend/dist/**` | defter derlemiyor, `dist` kaynakla aynı commit'e giriyor |
