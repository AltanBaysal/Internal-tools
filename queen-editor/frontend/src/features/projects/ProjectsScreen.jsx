import { useState } from "react";

import { createProject, deleteProject, renameProject } from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import NameModal from "./NameModal.jsx";
import ProjectCard from "./ProjectCard.jsx";
import { useProjects } from "./useProjects.js";

const CENTERED = {
  minHeight: "70vh",     // the design centres the empty state in ~70% of the body
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
};

// The foot of the list dissolving into the page rather than being cut off (Fark 8). It sits over
// the box rather than in it -- inside, it would scroll away with the cards -- and it takes no
// clicks, so the card underneath still opens.
const FADE = {
  position: "absolute",
  left: 0,
  right: 0,
  bottom: 0,
  height: 40,
  background: "linear-gradient(transparent, var(--bg))",
  pointerEvents: "none",
};

// Two rows of four. The design gives a count rather than a measurement, and a count is also the
// only thing the screen can act on: nothing here reads the layout (karar 45).
const FITS = 8;

export default function ProjectsScreen() {
  const { status, projects, error, reload } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);
  // The name being confirmed for deletion, or null. The name is the whole state: it is what the
  // question on screen has to say and what the request needs.
  const [deletingName, setDeletingName] = useState(null);
  // The name being renamed, or null -- the twin of deletingName. It is what the window opens on and
  // what the request is addressed to.
  const [renamingName, setRenamingName] = useState(null);
  const [busy, setBusy] = useState(false);
  const crowded = projects.length > FITS;

  async function handleDelete() {
    setBusy(true);
    try {
      await deleteProject(deletingName);
    } finally {
      setBusy(false);
      setDeletingName(null);
    }
    // Drive is the single source of truth here too: re-read the list rather than guess which card
    // disappeared.
    await reload();
  }

  // Drive is the single source of truth: after a create we re-read the list instead of guessing
  // the new card, so the date on screen is the folder's own.
  async function handleCreate(name) {
    await createProject(name);
    setModalOpen(false);
    await reload();
  }

  // The same rule: re-read the list rather than guess which card moved and what its date became.
  async function handleRename(name) {
    await renameProject(renamingName, name);
    setRenamingName(null);
    await reload();
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr)",
          alignItems: "center",
          padding: "14px 32px",
          background: "var(--bg-2)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>Projeler</Hand>
        <Btn hl style={{ justifySelf: "end" }} onClick={() => setModalOpen(true)}>
          <Icon.Plus /> Yeni proje
        </Btn>
      </div>

      {/* The header stays put and the projects move under it, the way the app's other four screens
          are built (karar 44). minHeight:0 is what lets the box be shorter than its grid: a flex
          child defaults to min-height:auto and would grow instead of scrolling. */}
      <div style={{ flex: 1, position: "relative", minHeight: 0 }}>
        <div data-list className="qe-thin-scroll"
             style={{ height: "100%", overflowY: "auto", padding: "24px 32px",
                      boxSizing: "border-box" }}>
          {status === "error" ? (
            <div style={CENTERED}>
              <StatusErrorCard text="Projeler yüklenemedi" raw={error} onRetry={reload} />
            </div>
          ) : status === "loading" ? (
            <div style={CENTERED}>
              <span className="wf-spinner" />
            </div>
          ) : projects.length === 0 ? (
            <div style={CENTERED}>
              <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz proje yok</Mono>
              <Note size={13} style={{ color: "var(--ink-3)" }}>
                İlk projeni oluştur, karelerin burada toplansın
              </Note>
              <Btn hl style={{ marginTop: 8 }} onClick={() => setModalOpen(true)}>
                <Icon.Plus /> İlk projeyi oluştur
              </Btn>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
              {projects.map((p) => (
                <ProjectCard key={p.name} name={p.name} modifiedAt={p.modifiedAt}
                             onDelete={() => setDeletingName(p.name)}
                             onRename={() => setRenamingName(p.name)} />
              ))}
            </div>
          )}
        </div>
        {crowded && <div data-fade style={FADE} />}
      </div>

      {modalOpen && (
        // The measure is the window's own: both of these carry the same form, so there is only one
        // of it left to give (Fark 6).
        <NameModal title="Yeni proje" submitLabel="Oluştur" busyLabel="Oluşturuluyor…"
                   onCancel={() => setModalOpen(false)} onSubmit={handleCreate} />
      )}

      {renamingName && (
        // Renaming takes nothing away, so there is no confirm and no red: the window opens straight
        // onto the name (Fark 3).
        <NameModal title="Projeyi yeniden adlandır" value={renamingName}
                   submitLabel="Kaydet" busyLabel="Kaydediliyor…"
                   onCancel={() => setRenamingName(null)} onSubmit={handleRename} />
      )}

      {deletingName && (
        <ConfirmModal
          width={340}
          title={`"${deletingName}" projesi silinsin mi?`}
          // What is running stops first, then what goes with the folder (Fark 9) -- the server
          // really does stop the production before the folder goes (madde 1).
          body={"Çalışan üretim durdurulur, kuyruktaki işler atılır. İçindeki tüm kareler — "
                + "fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı olarak silinir. "
                + "Bu işlem geri alınamaz."}
          confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
          onCancel={() => setDeletingName(null)} onConfirm={handleDelete}
        />
      )}
    </div>
  );
}
