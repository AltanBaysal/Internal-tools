# QueenAgent — Yol Haritası v12

**Durum:** Hazırlanıyor · 0/5 bitti

**Önceki sürüm:** [v11](2026-10-20-queen-agent-v11-roadmap.md) — bitti.

**Sıra: tek tek, dalga yok** *(kullanıcı, 27 Ekim — "ilk queen ediytor tasklarını yapıcaz bitincebana
haber vericeksin queen anget tasklarına geçiçez"; "sıryaal paralel yapmicaz")*. Bu roadmap, Queen
Editor v11 bitip kullanıcıya haber verildikten sonra başlar. Bir madde birleşince sıradaki başlar;
worktree açılmaz.

1. **v12-5** — sürüm V12, koşunun ilk işi.
2. **v12-3** — dört skill'e birer cümle.
3. **v12-1** — düzenleme kutusu.
4. **v12-2** — yazma kutusu; v12-1'in büyüme parçasını kullanır.
5. **v12-4** — toplu arşiv ve silme.

---

| Numara | İş | Durum |
|---|---|---|
| [v12-1](#v12-1) | Düzenlenen mesajın kutusu büyüsün | `ALIGNED` |
| [v12-2](#v12-2) | Mesaj yazma kutusu büyüsün | `ALIGNED` |
| [v12-3](#v12-3) | SDXL start seçiliyken model sormasın | `ALIGNED` |
| [v12-4](#v12-4) | Projeleri toplu arşivle/sil | `ALIGNED` |
| [v12-5](#v12-5) | Sürüm V12 | `ALIGNED` |

---

<a id="v12-1"></a>
### v12-1 — Düzenlenen mesajın kutusu büyüsün

**Kabul koşulu:** Bir mesaj düzenlenmeye açılınca kutu sohbetin genişliğinde açılıyor ve yazının
tamamını gösteriyor. Yazdıkça kutu büyüyor. Ekranın %40'ına gelince büyümesi duruyor ve yazı kutunun
içinde kayıyor.

**Bugün** *(27 Ekim, ekranda denendi)*: kutu her mesajda yaklaşık 200 × 76 px açılıyor, yani 2 satır.
480 × 569 px'lik bir mesajın balonu düzenlenince yine 200 × 76 px'lik bir kutuya dönüyor ve yazı
büyütmüyor.

**Kullanıcının kararları** *(27 Ekim)*:
- **Genişlik** *(cevap: "2")*: sohbetin genişliğinde, ChatGPT'deki gibi; *"2 güzel ama genişlmeninde
  süt snırı olması alzım yoksa chate geçmişini göremeyiz"*.
- **Üst sınır:** *"Ekranın %40'ı, yaklaşık 11 satır. ChatGPT'ye yakın."*; *"CHAT GPTYE YAKIN OLSUN"*.

<a id="v12-2"></a>
### v12-2 — Mesaj yazma kutusu büyüsün

**Kabul koşulu:** Yazı uzadıkça kutu büyüyor. Ekranın %40'ına gelince büyümesi duruyor ve yazı kutunun
içinde kayıyor. Mesaj gönderilince kutu bugünkü 2 satırlık boyuna dönüyor.

Mesaj yazma kutusu ChatGPT'deki gibi yazı uzadıkça büyür, bir sınırdan sonra kendi içinde kayar.

**Bugün** *(27 Ekim, ekranda denendi)*: kutu 1'den 20 satıra kadar hep 54 px, yani 2 satır. 3. satırdan
sonra yazı içinde kayıyor ve en üstte yarım kesilmiş bir satır görünüyor.

**Kullanıcının kararı** *(27 Ekim)*: *"İkisi de %40 olsun."* Düzenleme kutusuyla (v12-1) aynı sınır.

<a id="v12-3"></a>
### v12-3 — SDXL start seçiliyken model sormasın

**Kabul koşulu:** SDXL start scenario seçilip başlatılınca ajan "Krea mı, SDXL mi?" diye sormuyor.

SDXL start scenario seçilince QueenAgent model sormaz; doğrudan SDXL'le başlar.

**Ne oluyor** *(kullanıcı, 27 Ekim)*: *"İlk cevapta. SDXL start scenario'yu seçip ilk mesajı gönderince
ajan hemen soruyor."* Kodda: Krea'nın iki skill'i işi *"Krea scenario JSON"* diye anıyor, SDXL'in
ikisi yalnız *"scenario JSON"* diyor. Model her turda iki modelin araçlarını da görüyor, ve system
prompt'ta *"emin değilsen sor"* kuralı var.

**Kullanıcının kararları** *(27 Ekim)*:
- *"bu bnece prompt 1 cümleyele çözeriz başta neyin seçildiğini ve düzelir diye düşünüyorum"*: skill'in
  başında hangi modelin seçildiği bir cümleyle yazılır.
- *"bence hepsini ekelyelim krea ve sdxl editler start senayolar vs"*: dört skill'e de; SDXL start
  scenario, SDXL edit, Krea start scenario, Krea edit.
- Kabul koşulu aynı kalır: SDXL start scenario'yla başlatılan sohbette ajan model sormuyor.

<a id="v12-4"></a>
### v12-4 — Projeleri toplu arşivle/sil

**Kabul koşulu:**
- Projects sekmesinde seçilen projeler tek işlemle arşivleniyor ya da siliniyor. Archived sekmesinde
  seçilenler tek işlemle arşivden çıkıyor ya da siliniyor.
- Fare bir satırın üstüne gelince o satırda kutucuk görünüyor. Bir proje seçilince kutucuklar bütün
  satırlarda açık kalıyor.
- Kutucuğa tıklamak, ya da satıra Ctrl ile tıklamak, o projeyi seçiyor ya da seçimini kaldırıyor.
  Shift ile tıklamak, son seçilenle tıklanan arasındaki bütün projeleri seçiyor. Satıra düz tıklamak
  projeyi bugünkü gibi açıyor.
- Toplu silme onay soruyor: *"Delete 3 projects? The 12 chats and 40 files in them are deleted with
  them. This can't be undone."* Toplu arşivleme ve arşivden çıkarma onaysız.

**Bugün** *(27 Ekim, ekranda denendi)*: her proje kendi ⋯ menüsünden tek tek arşivleniyor ya da
siliniyor; ekranın hiçbir yerinde çoklu seçim yok. Projects sekmesi Pinned ve Recent diye iki
bölüm, Archived tek liste. Archive onaysız, Delete onaylı.

**Kullanıcının kararları** *(27 Ekim)*:
- **Ne yapılır** *(cevap: "1")*: Projects'te arşivleme ve silme, Archived'da arşivden çıkarma ve
  silme.
- **Seçim:** *"Her satırda hep bir kutucuk dursun. Kutucuğa tıklamak seçer, satırın geri kalanına
  tıklamak bugünkü gibi projeyi açar. Kutucuk fare satırın üstüne gelince görünsün, ⋯ menüsü gibi.
  Biri seçilince bütün satırlarda görünür hale gelir."*; *"ama biri seçilince kutucuklar açık kalsın
  diğerindede"*.
- **Onay:** *"Yalnız silmede."*
- **Hepsini seç yok, Shift ve Ctrl var:** *"Olmasın. Projeler tek tek seçilir."*; *"ama shift iler
  gurplı seçlebilsin"*; *"yada ctrl ile tek tek"*; *"windwo doyas kullanım ıgibi"*. Tek tıklamanın
  projeyi açması kalır *(cevap: "Evet, böyle.")*.
- Sekme değişince seçim temizlenir, çünkü iki sekmenin düğmeleri farklı. Bu Claude'un önerisi;
  kullanıcı itiraz etmedi.

**Maliyet:** bugün tek bir Archive bir istek atıyor ve ardından bütün proje listesini yeniden okuyor.
Toplu işlem bunu proje başına tekrarlamamalı: 20 proje 20 istek ve 20 liste okuması olur, 446'da
bulunan sorunun aynısı.

<a id="v12-5"></a>
### v12-5 — Sürüm V12

*(Kullanıcı, 27 Ekim — "bir de her roadmapin başında şun uyapmanı istiyorum ui daki sürümü arttıralım
olur mu"; "ilk görev o olsun ynai".)*

**Kabul koşulu:** QueenAgent'ın ekranında "QueenAgent V12" yazıyor; bugün "V11".
