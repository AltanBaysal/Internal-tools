# Kapanmış yuva: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-kapanmis-yuva-testler-design.md) · commit
`92bf10b` (4 test kırmızı)

## Ne değişiyor

`queue_layer`, kaynak karenin yuvasına iş eklerken o yuvanın **kapanmış** olup olmadığına bakacak;
kapanmışsa açan satırı yazacak:

```
record.mark(project, fid, kind, <yuvanın kendi dosyası>, queue.QUEUED, now())
```

Tek koşul: yuvada bir satır **var** ama katman dolu değil. Dolu olsaydı (`DONE`/`FAILED`) kod zaten
o dala hiç girmiyor — kopya kare yoluna gidiyor. Hiç satır yoksa yazacak bir şey de yok.

## Neden bu biçim

**"Tekrar dene"nin yaptığının aynısı.** `retry_frame` kırmızı katmanı sıraya geri koyarken tam bu
satırı yazıyor, üstelik yuvanın kendi dosya adıyla. Aynı işi ikinci bir biçimde yapmak, kuyruğun
tek kuralını iki lehçeye bölerdi.

**`is_open` gevşetilmiyor.** Deliği "REMOVED de açık sayılsın" diyerek kapatmak daha kısa olurdu ve
yanlış olurdu: o zaman kuyruktan çıkarılmış bir iş, kimse istemeden kendiliğinden geri gelirdi —
"Kuyruğu boşalt" hiçbir şey boşaltmamış olurdu. Açan şey, kullanıcının yeniden istemesidir; kayıt da
bunu yazmalı.

**Yuvanın kendi dosya adı yazılıyor**, karenin fotoğrafı değil. Satır o yuva hakkında; hangi dosyayı
işaret ettiği de o yuvanın son sözüdür.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../domain/usecases/queue_layer.py` | kapanmış yuva, iş eklenmeden önce açılır |

Ön yüz değişmiyor, `dist/` yeniden derlenmiyor.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` → 603 geçen, 0 düşen.
