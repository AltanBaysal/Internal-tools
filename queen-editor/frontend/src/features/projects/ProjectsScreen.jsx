import { useState } from "react";

import { createProject, deleteProject } from "../../shared/api.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import NewProjectModal from "./NewProjectModal.jsx";
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

export default function ProjectsScreen() {
  const { status, projects, error, reload } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);
  // The name being confirmed for deletion, or null. The name is the whole state: it is what the
  // question on screen has to say and what the request needs.
  const [deletingName, setDeletingName] = useState(null);
  const [busy, setBusy] = useState(false);

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

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
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

      <div style={{ flex: 1, padding: "24px 32px" }}>
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
                           onDelete={() => setDeletingName(p.name)} />
            ))}
          </div>
        )}
      </div>

      {modalOpen && (
        <NewProjectModal onCancel={() => setModalOpen(false)} onCreate={handleCreate} />
      )}

      {deletingName && (
        <ConfirmModal
          width={340}
          title={`"${deletingName}" projesi silinsin mi?`}
          // What goes is the frames and all three of their files, and the running production is
          // part of the answer: the server really does stop it before the folder goes (madde 1).
          body={"İçindeki tüm kareler — fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı "
                + "olarak silinir. Çalışan üretim durdurulur, kuyruktaki işler atılır. "
                + "Bu işlem geri alınamaz."}
          confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
          onCancel={() => setDeletingName(null)} onConfirm={handleDelete}
        />
      )}
    </div>
  );
}
