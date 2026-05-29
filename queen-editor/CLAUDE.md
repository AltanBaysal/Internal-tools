# queen-editor

Notebook'larla uğraşmadan [collab-toolbox](../collab-toolbox/CLAUDE.md) araçlarını web arayüzünden kullanmak için GUI. ComfyUI gibi ayrı bir web sitesi: ileride backend Colab/sunucuda çalışır, frontend HTTP ile bağlanır. Şu an **statik UI v1** (backend yok).

İlk araç: **Foto Üretici** — video-editör tarzı bir ekran (sahne tabanlı). Tasarım Claude Design'dan birebir alındı (handoff bundle).

## Stack

- React 18 + TypeScript + Vite.
- Stil: tasarımın `styles.css`'i birebir `src/styles/wireframe.css`'e port edildi (token + `.wf-*` sınıfları). Font: IBM Plex Sans/Mono. Tema: **Neutral Charcoal** (`#0f0f10`/`#17171a`/`#202024`, tintsiz gri) + violet accent `#a78bfa` + danger `#c97064`.
- State: şimdilik düz React hook'u (`useEditor`). Backend gelince store'a/HTTP'ye geçilir; view'lar değişmez.

## Komutlar

```bash
cd queen-editor/frontend
npm install
npm run dev        # http://localhost:5173
npm run build      # tsc + vite build → dist/
npm run preview
```

## Colab Hosting

ComfyUI gibi Colab'da çalıştırıp cloudflared tüneliyle tarayıcıdan açılır. İlke: **repo = nasıl yapılır (fonksiyonlar), notebook = çağır + canlı izle.** Notebook ince (sadece import + çağrı); loglar/URL hücrede akar.

- `colab/host.py` — fonksiyonlar: `ensure_cloudflared()`, `build(force=False)` (dist yoksa `npm ci && npm run build`), `serve_with_tunnel(port=8080)` (`dist/`'i `http.server` ile sun + cloudflared tünel, **ham logları + `🌐 trycloudflare.com` URL'sini canlı basar**, foreground/block).
- `host.ipynb` — 1 md + 3 kod hücresi: **bootstrap** (Secrets'tan `GITHUB_TOKEN` → `prod` clone/pull) · **kurulum** (`import host; host.ensure_cloudflared(); host.build()`) · **çalıştır** (`host.serve_with_tunnel()` — canlı, hücre açık kaldıkça tünel yaşar).

**Çalıştırma:** Colab'a `host.ipynb` yükle (bir kez) → 🔑 Secrets'a `GITHUB_TOKEN` → Run all → kurulum/tünel logları + çıkan URL hücrede; URL'yi aç.

> Üretim hâlâ **mock** (gerçek görsel yok). Bu aşama UI'ı tünelle açar; gerçek üretim için FastAPI + ComfyUI köprüsü sonraki adım (o zaman `http.server` → FastAPI `/api`).

## Mimari — separation of concerns

```
frontend/src/
├── styles/wireframe.css   # tasarımdan birebir port edilen tema + primitive sınıfları
├── components/
│   └── primitives.tsx     # tasarım primitive'leri (Hand, Btn, Seq, ImgPH, Segment, Status, Icon, Mono, Note, Grip)
├── tools/                 # her araç kendi klasörü → genişleme buradan
│   └── photo-generator/
│       ├── Editor.tsx     # ekranı kuran ana bileşen (5 durumu state'le yönetir)
│       ├── useEditor.ts   # tek state kaynağı (sahneler, seçim, üretim, mod, sil)
│       ├── types.ts
│       └── parts/         # EditorTopBar, SideComposer, TimelineCard, AddSceneTile, TimelineFooter, FauxScrollbar, DeleteConfirm
├── App.tsx                # v1: tek araç (Editor); ileride araç switcher
└── main.tsx
```

**İlke:** Yeni araç = `tools/<araç>/` klasörü + App'e ekleme. Ortak görsel dil `styles/` + `components/`'te. Bu, collab-toolbox'taki "her araç kendi klasörü" deseninin frontend karşılığı.

## Foto Üretici — ekran ve durumlar

Tek ekran, video-editör layout'u: üstte **top bar** (marka + proje adı), ortada büyük **preview** + sağda 360px **composer** (textarea + Tekil/Liste + Üret), altta yatay **sahne şeridi** (160px kartlar, 001..N, gerçek yatay scroll + faux scrollbar, prev/next + `NNN/NNN` sayaç). Tasarımdaki 5 board tek editörün durumları olarak yaşıyor:

| Durum | Ne görünür |
|---|---|
| Boş editör | preview dashed "preview", şeritte sadece `sahne ekle`, sayaç `000/000` |
| Sahne seçili | preview'da seçili sahne + sol-üst `NNN` + sağ-üst 🗑️; composer o sahnenin prompt'uyla dolu |
| Sahne ekle | preview boş, composer temiz, şeritte `sahne ekle` accent (mor) |
| Üretiliyor | preview'da dairesel spinner + "Çalışıyor"; şeride shimmer'lı kart; composer disabled |
| Sil onayı | editör bulanık, ortada danger modal (sadece sahne numarası) |

**Davranış:** Numara = pozisyon (sil/sırala → otomatik renumber). Sahne seçilince composer o prompt'la dolar; Üret → değiştirmişsen yeni prompt'la, değiştirmemişsen aynı prompt'la yeniden üretir. `sahne ekle` → composer temizlenir, yeni sahne sona eklenir.

**Sıralama (reorder):** İki yöntem — (1) kartı **sürükle-bırak** (ekleme çizgisi + kaldırılmış kart görünümü, bırakınca `useEditor.reorder(from,to)`), (2) kart **numarasına tıkla → yeni pozisyon yaz** (Enter). Seçim taşınan sahnede kalır (id ile); pozisyon=index olduğu için numaralar otomatik güncellenir.

**Mock:** Üretim sahte (gerçek görsel yok) — ~1.3s spinner sonrası placeholder. Gerçek render backend bağlanınca gelecek. Görseller `ImgPH` (diagonal-stripe placeholder).

## Dil konvansiyonu

[collab-toolbox](../collab-toolbox/CLAUDE.md) ile aynı: insana görünen metin (UI string'leri) **Türkçe**, koda bakan metin (kod yorumları, tip/değişken adları) **İngilizce**.

## Tasarım kaynağı

Claude Design handoff bundle'ı `.design-handoff/` altında (repo kökü, git'e girmez). README + chat transcript'leri + `project/` (HTML prototip, `styles.css`, `*.jsx`, ekran görüntüleri). Tasarımı değiştirmeden önce oradaki chat'lere bak — niyet orada.
