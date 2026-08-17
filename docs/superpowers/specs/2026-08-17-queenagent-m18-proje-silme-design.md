# Madde 18 — Proje silinir · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 18](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 25, 26, 28 · karar 16 · `HANDOFF.md` §6, §9
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Yol haritasının bıraktığı iki karar

### Çöp düzeni

Projenin dizini **olduğu gibi** `<kök>/trash/<proje-id>/` altına taşınır: `project.json`, `chats/`,
`files/` ve projenin kendi `trash/`i içinde bozulmadan durur.

Gerekçeler:

- **Kök seviyesindeki `trash/` bir projeyle çakışamaz.** Proje id'si `p` + 12 onaltılık karakter ve
  kullanıcı onu seçmiyor.
- **Ayrı bir koruma gerekmiyor.** `FileProjectStore.list_all` zaten `project.json` taşımayan bir
  dizini atlıyor ("anything else living under the root is not ours to read"), ve `trash/` böyle bir
  dizin.
- **Dosya çöpüyle aynı kural.** Aynı id iki kez çöpe giderse üstüne yazılmaz, `unique_name`
  numaralandırır — dosya silmede olduğu gibi.
- **Taşıma, kopyalama değil.** `Store.move` `os.replace` kullanıyor; dizinde de çalışır ve mtime'lar
  korunur.

### Çöpü boşaltma

**Uygulamada yok.** FOUNDATION karar 1 uygulamanın kullanıcının kendi makinesinde çalıştığını
söylüyor: klasör orada duruyor ve dosya yöneticisi bu işi bizden iyi yapıyor. YAGNI — gerçek bir
istek çıkarsa o zaman eklenir.

---

## 2 · Arka uç

`ProjectStore` portuna tek satır ekleniyor:

```
def delete(self, project_id: str) -> str | None:
    """Move the whole project to the trash and answer with the name it took there, or None."""
```

`delete_project` kullanım senaryosu `delete_file`'ın ikizi: `None` dönerse `ProjectNotFound`.

Yol: `DELETE /api/projects/<pid>` → 404 ya da `{"trashed": "..."}`. Dosya silmenin cevabıyla aynı
biçim; **geri yükleme yolu yok** (karar 16), yani `trashed` yalnız ne olduğunu söylüyor.

**Sohbetler ve dosyalar ayrıca silinmiyor** — dizinin içinde oldukları için onunla birlikte
gidiyorlar. Bu, "hiçbir artefakt başka birinin cevabını tekrarlamaz" kuralının silme tarafı.

---

## 3 · İki kapı, tek kutu

**Proje başlığı.** "Rename"in yanında kırmızı çerçeveli "Delete" (`--destructive-line` kenar,
`--destructive` yazı); üstüne gelince kırmızıyla dolar.

**Kenar çubuğu satırı.** Hover'da beliren ⋯ düğmesi, 176px'lik menü: "Rename" ve kırmızı "Delete
project".

**Kenar çubuğu satırı artık tek bir düğme olamaz.** Bugün satırın kendisi `<button>`; içine ikinci
bir düğme koymak geçersiz HTML olurdu. Satır `<div class="sidebar__row">` oluyor, içinde projeyi açan
`<button class="sidebar__row-open">` ve ⋯ düğmesi. Görünüm değişmiyor, kutu değişiyor.

Menü **`position: fixed`** ve ekrana kıstırılıyor: kenar çubuğunun kaydırma alanı onu kırpmasın diye
(`HANDOFF.md` §6). Kıstırma jsdom'da ölçülemiyor — kilit testi ölçüyü, Madde 35 gözü üstleniyor.

---

## 4 · Kutunun cümlesi

Başlık: `Delete "X"?`
Gövde: `The N chats and M files in this project are deleted with it. This can't be undone.`

Tekil hâli tasarımın kendi notu: **"1 chat"**, "1 chats" değil. Aynısı dosya için.

Sayılar kenar çubuğunun okuduğu sayıların aynısı — proje listesindeki `chats` ve `files`. Ayrı bir
istek atılmıyor: cevabı elde olan bir şey sunucuya ikinci kez sorulmaz.

---

## 5 · Silmeden sonra nereye (fark 28)

- **İçinde bulunulan proje silinirse** ekran kalan **ilk** projeye geçer; hiç kalmazsa `/`'a düşer ve
  çatal onu "No projects yet" ekranına götürür. Açık sohbet ve önizleme temizlenir — adresin
  değişmesi ikisini de zaten bırakıyor.
- **Başka bir proje silinirse** hiçbir şey kıpırdamaz: adres aynı, açık sohbet aynı, kaydırma aynı.

**Geri alma yok, şerit de yok** (karar 16). Diskte hiçbir şey kaybolmuyor; FOUNDATION'ın "ya onay ya
geri alma" kuralı onay tarafından karşılanıyor.

---

## 6 · Klavye: sıra tek dinleyicide

App'in tek `keydown` kancası `HANDOFF.md` §9'un sırasını alıyor: **⋯ menüsü → onay kutusu → okuma
paneli.** Madde 17'de ertelenen Esc buraya geliyor; kutu hâlâ kendi dinleyicisini kurmuyor.

Dış tıklama menüyü kapatıyor — bu menünün kendi olayı, klavye değil.

---

## 7 · Başlık satırı sarar (fark 25)

Başlığın yanında artık iki düğme var. Satır sığmazsa sarıyor: sığmayan düğmeler alt satıra iniyor,
ad kesilmiyor.

---

## 8 · Katman denetimi

Arka uç: yeni kullanım senaryosu `domain/usecases/delete_project.py`, port'a bir satır,
`FileProjectStore.delete`, bir yol. Yön korunuyor — `presentation → domain ← data → services`.

Ön yüz: `Sidebar` (satırın kutusu + menü), `ProjectScreen` (başlık düğmesi), `App` (onay durumu,
silme, gidilecek yer, Esc sırası), `useProjects` (`removeProject`).

Menü ayrı bir bileşen (`RowMenu.jsx`) oluyor: kıstırma ve dış tıklama kendi işi, kenar çubuğunun
değil.

---

## 9 · Kabul ölçütü

1. `DELETE /api/projects/<pid>` projeyi `trash/<pid>` altına taşır; içindekiler bozulmadan gelir.
2. Olmayan bir proje 404 verir.
3. İki kapı da aynı kutuyu açar; kutu doğru sayıları ve tekil/çoğul hâli söyler.
4. Onaydan sonra proje listeden düşer.
5. İçinde bulunulan proje silinince kalan ilk projeye, hiç kalmazsa `/`'a gidilir.
6. Başka proje silinince adres kıpırdamaz.
7. Esc önce menüyü, sonra kutuyu, sonra paneli kapatır.
8. Hiçbir yerde geri alma ya da şerit yok.

## 10 · Risk

En büyüğü kenar çubuğu satırının kutusunun değişmesi: bugün satırın kendisi düğme ve testler onu
`getByRole("button", { name: … })` ile buluyor. Ad artık iç düğmenin üstünde olacak; testler bunu
takip ediyor ve davranış aynı kalıyor.
