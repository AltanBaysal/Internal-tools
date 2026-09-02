# Madde 145 — Form modelleri anlatmayı bırakır · Tasarım

**Kaynak:** [v6 yol haritası — Madde 145](../plans/2026-09-01-v6-roadmap.md#madde-145--form-modelleri-anlatmayı-bırakır-queen-editor)
**Dal:** `feat/v6` · **Önceki commit:** `cb6d190` *(739 yeşil; ön yüz 28 dosya / 587 yeşil)*

## Problem

144 Colab formundaki iki kutu grubunu ayırdı, ve ayırırken başlığın altına dört satır metin de
koydu. Kullanıcının hükmü *(2 Eylül)*: **"bu detaya gerek yok"** — ve sorulan üç şıkkın 3.'sü
seçildi, yani başlık ile ayraç dışında hepsi kalkıyor.

## Değişen tek şey dört `#@markdown` satırı

```python
#@markdown ---
#@markdown ### Fotoğraf modelleri
PHOTO_NOVA3DCG = False  #@param {type:"boolean"}
```

Giden satırlar kurala, boyuta ve üç modelin stiline dairdi. Yerlerine bir yorum geliyor — kaynağı
okuyan için, forma çizilmeyen: neden gittiklerini ve kutuların neden boş geldiğini söylüyor.

## Bilgi kaybolmuyor, çünkü giden her cümlenin aslı yerinde duruyor

| Formdan giden | Aslı nerede |
|---|---|
| *hiçbirini seçmezsen defter durur* | CONFIG'deki `assert`'in Türkçe mesajı |
| *hepsi boş gelir* | kutuların kendisi — Colab onları boş çiziyor |
| *~2 GiB + her model ~7 GiB, üçü ~23* | indirme hücresi `need` GiB'ı **seçime göre hesaplayıp** basıyor |
| *nova3DCG — 3DCG / 2.5D* … | `PHOTO_MODELS` satırları; tam tablo yol haritasının 140'ında |

Kutu adları formda kalıyor: Colab `#@param` satırının **değişken adını** etiket olarak çiziyor,
yani `PHOTO_NOVAORANGE` görünmeye devam ediyor. Giden şey ad değil, stil tarifi.

Boyut satırı gitmekle **daha da doğrulaşıyor**: formdaki *"üçü birden ~23 GiB"* sabit bir yuvarlama,
hücrenin bastığı sayı ise gerçekten işaretlenenlerin toplamı.

## Bir test gidiyor, çünkü tarif ettiği karar değişti

`test_the_form_says_which_model_each_box_installs` formun üç model adını taşıdığını çiviliyordu.
İstenen tam tersi, ve o testle birlikte defter değiştirilemezdi.

Yerine kalanı ölçen bir test geliyor:

```python
def test_the_form_leaves_the_model_section_at_its_heading():
    drawn = _drawn(_cell("# === CONFIG ===")).splitlines()

    assert "#@markdown ---" in drawn, "Formda iki grubu ayıran çizgi yok"
    tail = drawn[drawn.index("#@markdown ---"):]

    assert tail == ["#@markdown ---", "#@markdown ### Fotoğraf modelleri"], \
        f"Model bölümü başlıktan ibaret değil: {tail}"
```

**Kalanla ölçülüyor, gidenle değil.** *"nova3DCG formda geçmesin"* diyen bir test, yerine üç başka
cümle konmuş bir formda yeşil kalırdı — sorulan soru cümlelerin hangileri olduğu değil, **kaç tane**
olduğu.

**Ayraçtan sonrası okunuyor, hücrenin tamamı değil.** Üretici başlığı ile altındaki satır duruyor:
şikâyet model bölümüneydi, ve `Video ~39 GiB · ses ~9 GiB` orada bir kopya değil — o iki grubun
boyutu hiçbir yerde seçime bağlı hesaplanmıyor.

**Çizgi önce aranıyor, sonra indeksi alınıyor.** `list.index` bulamazsa `ValueError` atar; o bir
iddia değil, bir çökme.

## Değişmeyen

- **Kutular, `assert`'ler, `PHOTO_MODELS`, disk hesabı, uygulama, `dist`.**
- **Giriş hücresi, bilerek.** Defterin açılış metni iki kademeyi hâlâ anlatıyor; orası okumak için
  durulan yer, form ise işaretlemek için.
- **Öteki dört CONFIG testi** — eşleşme, kapalı gelme, kontrol satırı, ayraç/başlık konumu.

## Colab'da görülecek

Sağdaki panelde **Üreticiler** başlığı, bir satır açıklama, üç kutu; yatay çizgi; **Fotoğraf
modelleri** başlığı ve üç kutu. Başka hiçbir şey.

**Takım bunu doğrulayamaz** — yalnız satırların gittiğini söyler. Çizimi gören tek göz kullanıcının
gözü.
