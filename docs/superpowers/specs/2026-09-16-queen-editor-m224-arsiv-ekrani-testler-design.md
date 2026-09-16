# Madde 224 · Arşiv ekranı kendi düğmelerini taşıyacak — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcının söylediği

> *"Arşive gelince içinde proje oluşturabiliyorum. Arşive girince geri butonu olsun projeye
> girinceki gibi, ve oluştur da olmasın."*

İki şey, ve ikisi de aynı sebepten: **arşiv girilen bir yer**, listenin bir süzgeci değil.

## Bugün ne var

[`ProjectsScreen`](../../../queen-editor/frontend/src/features/projects/ProjectsScreen.jsx)'in
başlığı iki listede de **aynı**: solda uygulamanın adı, ortada `inArchive ? "Arşiv" : "Projeler"`,
sağda iki düğme — biri listeyi değiştiren anahtar *(`inArchive ? "Projeler" : "Arşiv"`)*, öteki
**Yeni proje**.

Yani arşivdeyken **Yeni proje** duruyor ve basılabiliyor. Bastığında açılan pencere gerçekten bir
proje açıyor — ama o proje **projelere** düşüyor, bakılan listeye değil. Düğme bulunduğu yerde yalan
söylüyor: kullanıcı arşive bir şey eklediğini sanır, ve eklediği şey görünmez.

Çıkış ise bugün **Projeler** yazan bir anahtar. Anahtar olduğu için iki yönlü okunuyor; kullanıcının
istediği ise **çıkış**, ve uygulamada çıkışın bir biçimi zaten var:
[`ProjectScreen`](../../../queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx)'in
sağ üstünde duran ghost **Projeden çık** düğmesi.

## Karar

Arşiv görünümünün başlığı **kendi düğmesini** taşıyor, ve o tek düğme:

| Görünüm | Sağdaki düğmeler |
|---|---|
| Projeler | `Arşiv` *(ghost)* · `+ Yeni proje` *(hl)* |
| Arşiv | `Arşivden çık` *(ghost)* |

**Ad, projeninkinin aynı kalıbı** — *"Projeden çık"* varken *"Arşivden çık"* öğrenilecek bir şey
değil, tanınacak bir şey. Ok işareti yok, çünkü projeninkinde de yok: uygulamanın çıkışı bir kelime.

**Yeni proje arşivde hiç çizilmiyor**, kapalı değil. Kapalı bir düğme *"burada da olabilirdi"* der;
oysa orada olacak bir şey değil.

Arşivin **boş hâli** zaten kendi cümlesini taşıyor *("arşivde proje yok")* ve içinde bir açma düğmesi
yok — yani o taraf 221'de doğru kurulmuştu, eksik olan yalnız başlıktı.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Arşivdeyken **Yeni proje** düğmesi yok | **kırmızı** |
| 2 | Arşivdeyken çıkış düğmesi **Arşivden çık** diyor | **kırmızı** |
| 3 | Ona basınca projeler listesi geri geliyor | **kırmızı** |
| 4 | Projeler listesinde **Arşiv** ve **Yeni proje** ikisi de duruyor | yeşil, ve öyle kalmalı |
| 5 | **Boş** arşivde de açacak bir şey yok | **kırmızı** |

Üçüncüsü yazarken kırmızı çıktı: arşivden **çıkan** hiçbir test yokmuş — girmeyi tutan var, çıkmayı
tutan yok. Düğmenin adı zaten değişiyor, yani o çivi hem yeni adı hem ilk kez çıkışın kendisini
tutuyor.

Beşincisi ayrı bir soru, birincinin tekrarı değil: **boş** liste, projeler tarafında bir *açma
düğmesi* çizen tek yer *("İlk projeyi oluştur")*. Arşivin boş hâli 221'de doğru kurulmuştu ve öyle
kalmalı.

## Bu turda değişen

Yalnız testler: `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`.

Arka uçta hiçbir şey değişmiyor — arşivde proje açmak zaten arka uca hiç sorulmayan bir şey, ve
açılan proje de kurallara göre açılıyor. Bu madde baştan sona ekranın kendi meselesi.
