# Queen Editor — Yol Haritası v9

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` · **Durum:** kullanıcı kararı, koşu başlıyor.
**Öncesi:** [v8](2026-08-13-queen-editor-v8-roadmap.md) — 3 görev kapandı, Colab turunda kurulum çalışmadı.

## Neden bu koşu var

Colab turunda üç üreticinin üçü de kurulamadı: foto ve video Civitai'nin yönlendirmesinde **403**,
ses ise kurulup süreçte görünmedi. Kullanıcı kararını verdi: **kurulum uygulamadan çıkacak,
Colab'da yapılacak** — `collab-toolbox`'ta yıllardır çalışan yöntemle.

Bu, v7 ve v8'in yönünü tersine çeviriyor. Sebebi de yazılı olsun: uygulamanın indiricisi
kanıtlanmış hücrenin bildiği bir şeyi bilmiyordu ve öğrenmesi yeni iş demekti; kullanıcı o işi
yapmak yerine çalışan yöntemi kullanmayı seçti.

## Kapsam sınırı

- **Şimdilik yalnız fotoğraf.** Video ve ses modelleri bu koşuda kurulmuyor; sıraları gelince.
- **Panel kalıyor, ama sadece söylüyor.** Neyin kurulu olduğunu göstermeye devam eder; kurulu
  olmayan için "Colab'dan kur" der. Uygulama artık hiçbir şey indirmiyor.

## Görevler

### Görev 1 · Kurulum uygulamadan kalksın

**Ne olacak:** İndirme, kurulum, iptal — hepsi backend'den ve arayüzden silinir. Geriye tek soru
kalır: "bu üretici kurulu mu?" Panel onu cevaplamaya devam eder, ama artık bir şey yapamaz;
kurulu olmayan satır kullanıcıyı Colab defterine yollar.

**Bağımlılık:** Yok.

**Bitti sayılır:** Uygulamada indirme yapan tek satır kod yok; panel üç üreticinin durumunu doğru
gösteriyor ve kurulmamış olan için ne yapılacağını söylüyor.

### Görev 2 · Fotoğraf modelleri defterde kurulsun

**Ne olacak:** Defter fotoğraf grubunun beş dosyasını kurar — `collab-toolbox`'taki çalışan
hücrenin yöntemiyle, birebir. Ağır indirmeden önce kapılı erişim yoklanır, her dosya indikten
sonra doğrulanır, bozuk dosya silinmez. Kurulum **Flask'tan önce** gelir: uygulama açıldığında
her şey yerinde olsun, panel de doğru cevabı bir kez okusun.

**Bağımlılık:** Görev 1 — önce uygulamadaki ikinci yol kalkmalı, yoksa yine iki kurulum yolu olur.

**Bitti sayılır:** Temiz makinede Run all sonunda fotoğraf üreticisi kurulu görünüyor ve bir foto
üretiliyor.

## Sonraki koşuya kalanlar

Video ve ses modellerinin defterde kurulması. Kullanıcı önce fotoğrafın uçtan uca çalıştığını
görmek istiyor.

## Nasıl çalışacağız

Görev başına spec → plan → TDD → tek commit. Ön yüz değişirse `dist/` aynı commit'te.
