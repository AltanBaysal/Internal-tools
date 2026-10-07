# Madde 346 — Projenin son kullanıldığı an, ve listenin sırası, sunucu · uygulama turu

**Kaynak:** [yol haritasının 346'sı (v9-2j)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turunun spec'i](2026-09-29-queenagent-m346-son-kullanim-sira-testler-design.md) — "kullanıldı"nın
ne demek olduğu, sıra, ve neden. Bu belge kırmızı testleri yeşile getiren kodu anlatır.

**Kullanıcıdan gereken:** hiçbir şey.

## Parçalar

Katmanlar CODE-STANDARD'daki gibi: `presentation → domain ← data → services`. Servis değişmez —
`Store`'un `list_dir`, `exists` ve `mtime`'ı yetiyor. Yeni dosya yok, yani CODE-STANDARD'ın tablosu
değişmez.

**`domain/project.py`** — `Project` iki alan kazanır, ikisi de diskten okunur ve hiçbir yere geri
yazılmaz: `last_chat_at: str = ""` (en yeni sohbet dosyasının anı; sohbet yoksa boş) ve
`pinned_at: str = ""` (sabitlendiği an; sabitli değilse boş). `pinned` alan olmaktan çıkar ve
`pinned_at`'ten okunan bir özellik olur — iki alan aynı cevabı iki kez verirdi. Yeni özellik
`last_activity`: `last_chat_at`, boşsa `created_at`. "Sohbeti yoksa doğduğu an" bir kural, o yüzden
alanın içinde, deponun değil.

**`data/file_project_store.py`** — `list_all` her proje için:
- `chats/`'ın listesini bir kez okur; sayı ondan, `last_chat_at` içindekilerin en yeni mtime'ından
  (liste boşsa `""`).
- `pinned` varsa `pinned_at` onun mtime'ı, yoksa `""`.

Bir mtime ISO'ya `_now`'un biçimiyle çevrilir — UTC, milisaniye —; `createdAt` de o biçimde, o yüzden
anlar metin olarak karşılaştırılabilir, `list_chats`'in ve bugünkü `list_projects`'in yaptığı gibi.
`file_file_store.py`'deki `_iso` aynı tek satır; özel bir adı öteki modülden almak yerine burada bir
kez daha yazılır.

**`domain/usecases/list_projects.py`** — kural değişir: sabitliler `(pinned_at, id)` artan; ötekiler
`(last_activity, id)` azalan; önce birinciler, sonra ikinciler. Arşivdekiler ayrılmaz.

**`presentation/routes.py`** — `_project_json` `"lastActivity": project.last_activity` ekler; liste,
oluşturma ve düzenleme aynı fonksiyondan geçtiği için üçü de söyler. `"pinned"` aynı kalır.

**`CODE-STANDARD.md`** — *"No file repeats another's answer"* paragrafı dosya listesinin `2h ago`'sunu
örnek veriyor; yanına projeninki bir cümleyle gelir: projenin `2h ago`'su en yeni sohbet dosyasının
mtime'ı, sohbeti yoksa `createdAt`. Bu, ileride o anı `project.json`'a yazmak isteyen kodu bağlayan
kural; kodun kendisi bunu söylemez.

**`frontend/src/features/workspace/useProjects.js`** — yeni projeyi listenin sonuna ekleyen satırın
yorumu *"the server lists projects oldest first"* diyor; artık yanlış. Kod değişmez (ön uç bu maddenin
değil, All projects v9-2n'de geliyor), yorum bugünkü doğruyu söyler: sona eklenmesi liste yeniden
okunana kadar; yeri sunucunun sırası, ve kuralın bir kopyası burada ondan kayardı. Yorum derlenen
koda girmez, `dist` değişmez.

## Ekranda ne değişir

Bugünkü kenar çubuğu projeleri sunucunun sırasıyla çiziyor, ve `/` listenin ilk projesine açılıyor:
- Kenar çubuğunda projeler artık en eskiden değil, en son kullanılandan başlıyor (bugün arayüzden
  sabitlenemiyor; sabitli olan olursa en üstte).
- Uygulama en eski projeye değil, en son kullanılana açılıyor.
- Bir projede sohbet edince, tur bitip liste yeniden okununca o proje en üste çıkıyor.
- Yeni proje önce listenin sonunda çıkıyor, liste yeniden okununca üste geçiyor.

## Değişmeyenler

- Ön ucun kodu ve `dist`.
- Sohbetin `lastActivity`'si ve `list_chats`.
- `pinned` ve `archived` dosyaları, ve `PATCH`'in kapısı.

## Nasıl görülür

CLAUDE.md'deki dört satır: queen-agent'ın arka ucu 954 yeşil, ön ucu 695; queen-editor'ün arka ucu
1160, ön ucu 749.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m346-son-kullanim-sira-uygulama-plan.md).
