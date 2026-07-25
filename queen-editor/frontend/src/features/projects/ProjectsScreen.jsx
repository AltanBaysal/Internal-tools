import { useState } from "react";

import { createProject } from "../../shared/api.js";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import NewProjectModal from "./NewProjectModal.jsx";
import ProjectCard from "./ProjectCard.jsx";
import { useProjects } from "./useProjects.js";

const CENTERED = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 10,
};

export default function ProjectsScreen() {
  const { status, projects, error, reload } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);

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
          gridTemplateColumns: "1fr auto 1fr",
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
            <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
              <Icon.Warn />
              <Note size={14} style={{ color: "var(--danger)", fontWeight: 500 }}>
                Projeler yüklenemedi
              </Note>
            </span>
            {/* The server's raw message -- we never guess the cause. */}
            <Mono
              size={11}
              style={{
                color: "var(--ink-3)",
                background: "var(--bg)",
                border: "1px solid var(--border)",
                borderRadius: 3,
                padding: "6px 8px",
                maxWidth: 640,
                wordBreak: "break-word",
              }}
            >
              {error}
            </Mono>
            <Btn onClick={reload}><Icon.Regen /> Tekrar dene</Btn>
          </div>
        ) : status === "loading" ? null : projects.length === 0 ? (
          <div style={CENTERED}>
            <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz proje yok</Mono>
            <Note size={13} style={{ color: "var(--ink-3)" }}>
              İlk projeni oluştur, fotoğrafların burada toplansın
            </Note>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            {projects.map((p) => (
              <ProjectCard key={p.name} name={p.name} modifiedAt={p.modifiedAt} />
            ))}
          </div>
        )}
      </div>

      {modalOpen && (
        <NewProjectModal onCancel={() => setModalOpen(false)} onCreate={handleCreate} />
      )}
    </div>
  );
}
