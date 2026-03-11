# mmaudio-generate

MMAudio modeli ile metin açıklamasından ses dosyası üreten Colab notebook'u.

## File

- `mmaudio_generate.ipynb` — Text-to-audio generation (MMAudio large_44k_v2)

## Usage

1. [Google Colab](https://colab.research.google.com/) açın
2. **File → Upload notebook** ile `mmaudio_generate.ipynb` dosyasını yükleyin
3. **Runtime → Change runtime type → T4 GPU** seçin
4. Hücreleri sırayla çalıştırın (Shift + Enter)
5. PROMPT ve DURATION değerlerini değiştirip tekrar çalıştırabilirsiniz

## Notes

- Model ağırlıkları ilk çalıştırmada otomatik indirilir (~2-3 dk)
- T4 GPU yeterlidir (~6GB VRAM), float16 kullanılır (T4 bfloat16 desteklemez)
- Çıktı formatı: `.flac` (44kHz)
- Model lisansı: CC-BY-NC 4.0 (yalnızca ticari olmayan kullanım)
