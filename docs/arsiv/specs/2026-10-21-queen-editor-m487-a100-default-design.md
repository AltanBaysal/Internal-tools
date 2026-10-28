# Madde 487 · Queen Editor notebook'u varsayılan olarak A100 açar — tasarım

**Tarih:** 21 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
487 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Yol haritasında madde `UNALIGNED`; ana ajanın brief'i 21 Ekim'de ne yapılacağını ve GPU
kontrolünün bugünkü kadar basit kalacağını söyledi.

## Ne, neden

Kullanıcının sözü (21 Ekim): *"notebook dediğin queen editor notebook'uysa default a100 seçsin"*.

`queen-editor/queeneditor.ipynb` Colab'da açılınca runtime A100 GPU olarak gelir, ve notebook'ta
T4 öneren bir yazı kalmaz. Sebep: Krea 2 Turbo'nun int8 DiT'i tek başına ~13,5 GB (madde 482) ve
T4'e sığmaz.

## Bugün — koddan okunanlar

- Notebook'un `metadata`'sında yalnız `kernelspec` ve `language_info` var; Colab'a hangi runtime'ı
  istediğini söyleyen bir şey yok, bu yüzden Colab varsayılanını (CPU) açıyor.
- CONFIG hücresinin GPU kontrolü yalnız bir GPU olup olmadığına bakar (`nvidia-smi`); yoksa
  `"❌ GPU yok — Runtime → Change runtime type → T4 GPU seç …"` der. Notebook'ta T4'ü anan tek yazı
  bu.
- Repodaki diğer notebook'lar (ör. `collab-toolbox/photo_experiments/krea-2/turbo.ipynb`,
  `collab-toolbox/queen-tools/photo_to_video.ipynb`) A100'ü aynı biçimde ister:
  `"accelerator": "GPU"` ve `"colab": {"gpuType": "A100", "provenance": []}`.
- `queen-editor/README.md` "video wants more disk than a T4 has" diyerek runtime'ı kullanıcıya
  bırakıyordu.

## Ne değişir

1. **Notebook metadata:** `"accelerator": "GPU"` ve `"colab": {"gpuType": "A100", "provenance": []}`
   eklenir — collab-toolbox notebook'larının biçimi. Colab bunu dosyayı açarken okur.
2. **GPU kontrolünün mesajı:** "T4 GPU seç" → "A100 GPU seç". Kontrol aynı kalır: yalnız GPU'nun
   varlığına bakar. A100 olmayan bir kartı reddetmez, uyarmaz da — brief kontrolün bugünkü kadar
   basit kalmasını istedi.
3. **README:** runtime cümlesi "The notebook opens on an A100, because Krea 2 Turbo does not fit a
   T4." olur.

Bir hücre koduna ya da `colab/`'a dokunulmaz; notebook'un boyutu yalnız iki harf büyür (tavan,
madde 239, etkilenmez).

## Maliyet

Disk ve ağ: yok. Metadata'yı Colab notebook'u açarken bir kez okur; çalışan hiçbir kod değişmez.

## Ne bozulabilir, sınırlar

- A100, Colab'ın ücretli planlarında vardır. Hesapta A100 yoksa ya da o an boşta değilse Colab
  kullanıcıya söyler ve başka bir runtime önerir; notebook o durumda da bugünkü gibi çalışır, Krea
  seçildiyse ComfyUI'nin kendi bellek hatasıyla durur. Bunu notebook yakalamaz ("Ne değişir", 2).
- Colab notebook'u kaydederken metadata'ya kendi alanlarını ekleyebilir; `gpuType` kalır.

## Test

`queen-editor/backend/tests/test_notebook_opens_on_an_a100.py`, komşu notebook testlerinin
biçiminde, notebook'u okur, çalıştırmaz:

- metadata `accelerator == "GPU"` ve `colab.gpuType == "A100"`;
- hiçbir hücrenin kaynağı `T4` adını geçmiyor.

## Bitti sayılır

- İki test yeşil, `python -m pytest queen-editor -q` yeşil, notebook JSON olarak okunuyor.
- Notebook'ta T4 geçmiyor; GPU yok mesajı A100 diyor.
- Colab'da açılınca runtime A100 geliyor — bu, koşunun sonundaki Colab denemesinde görülür.
