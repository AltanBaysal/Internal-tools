# MMAudio Generate - TODO

## Drive Cache Eksikleri

- [ ] **CLIP ve BigVGAN vocoder modelleri Drive cache'e dahil degil**
  - `open_clip_pytorch_model.bin` (~3.95 GB) ve `bigvgan_generator.pt` (~489 MB) her runtime sifirlandiginda internetten tekrar indiriliyor
  - Mevcut cache sadece `vae.pth`, NSFW model ve `bigvgan_16k.pth` dosyalarini kapsiyor
  - `FeaturesUtils` olusturulurken `open_clip` ve `bigvgan` kutuphaneleri kendi HF Hub cache'ini kullaniyor (`~/.cache/huggingface/`), bu da Colab runtime ile birlikte siliniyor
  - **Cozum:** Bu modelleri de Drive cache mekanizmasina ekle, boylece her seferde ~4.4 GB indirme atlanir
