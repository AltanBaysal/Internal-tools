# Madde 129 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 129
**Testler kırmızı commit'te (9139eca).**

## Doğan dosya: `domain/context_box.py`

Saf alan mantığı, deposu yok — kayıttan okur, diski bilmez:

- `BOX_LIMIT = 5`
- `files_opened(chat, steps=())` → bu sohbetin okuduğu dosya adları, en yenisi başta, en çok
  `BOX_LIMIT` tane. Kaynak: mesajların `calls`'ı artı bu turun o ana kadarki adımları. Yalnız
  `read_file`, yalnız hedefi olan, ve **bulunamayan okuma girmez** — `outcome`'u
  `No file by that name` olan çağrı bir addır ama arkasında dosya yoktur.
- `schema_was_read(chat, steps=())` → `read_prompt_structure_schema` çağrıldı mı.

Kayıt geriye doğru gezilir: en yeni adım en başa gelir, tekrar eden ad ilk görüldüğü yerde kalır.

## `stream_answer.py`

`_opened(file_store, project_id, chat, steps)` her raundda kabı metne çevirir:

```
Files you have opened in this chat, with their contents as they are now:

--- plan.md ---
<diskteki hâli>
```

Şema çekilmişse aynı metnin sonuna `--- prompt structure schema ---` başlığıyla `SCHEMA` eklenir.
Diskte bulunmayan ad sessizce atlanır. Hiçbir giriş kalmazsa kap **hiç gönderilmez** — boş bir
başlık, okunup boş olduğu anlaşılan bir satırdır.

İsteğin sırası: konuşma → dosya adları *(127)* → kap → skill metni *(93)*.

`steps` olarak turun `made` listesi geçer: tur ortasında okunan dosya bir sonraki raundda kapta
olmalı, ama `made` kayda ancak turun sonunda yazılır.

## Ayakta kalması gerekenler

93'ün sırası, 127'nin adlar satırı, 124'ün önbellek anahtarı *(kap kuyrukta, prefix'e dokunmaz)*,
`read_file`'ın kendisi, disk şeması *(değişmez)*.

## Bilerek yapılmayanlar

Konuşmadaki `tool` mesajları olduğu gibi kalır. Yazma araçları kaba giriş açmaz. Boyut tavanı
yok: sınır sayıdadır *(5)*, ve Madde 92 zaten sohbetin tamamına tavan koyuyor.
