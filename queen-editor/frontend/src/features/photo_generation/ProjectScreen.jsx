import { photoUrl } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";
import GeneratePanel from "./GeneratePanel.jsx";
import { useGeneration } from "./useGeneration.js";

// Part 4 skeleton: header + one prompt + the produced photo. Part 5 replaces the body with
// artboard 03 (prompt list, negative, variants, 5-column gallery).
export default function ProjectScreen({ project }) {
  const { job, error, generate } = useGeneration(project);
  const photo = job.status === "done" && job.project === project ? job.file : null;

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <div style={{
        display: "grid",
        gridTemplateColumns: "1fr auto 1fr",
        alignItems: "center",
        padding: "14px 32px",
        background: "var(--bg-2)",
        borderBottom: "1px solid var(--border)",
      }}>
        <Btn ghost onClick={() => navigate("/")}>← Projeler</Btn>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>

      <div style={{ flex: 1, display: "flex", gap: 32, padding: "24px 32px", alignItems: "flex-start" }}>
        <GeneratePanel job={job} error={error} onGenerate={generate} />

        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
          {photo ? (
            <>
              {/* New tab on click -- the same gesture the gallery will use in Part 5. */}
              <a href={photoUrl(project, photo)} target="_blank" rel="noreferrer">
                <img src={photoUrl(project, photo)} alt={photo}
                     style={{ maxWidth: "100%", border: "1px solid var(--border)", borderRadius: 4 }} />
              </a>
              <Mono size={11} style={{ color: "var(--ink-3)" }}>{photo}</Mono>
            </>
          ) : (
            <Note size={13} style={{ color: "var(--ink-3)" }}>
              Prompt yaz, Üret'e bas — fotoğraf burada belirecek
            </Note>
          )}
        </div>
      </div>
    </div>
  );
}
