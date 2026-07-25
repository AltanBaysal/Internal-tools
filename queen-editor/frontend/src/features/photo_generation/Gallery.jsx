import { photoUrl } from "../../shared/api.js";
import { Mono, Note } from "../../vendor/kit.jsx";

const GRID = {
  display: "grid",
  gridTemplateColumns: "repeat(5, 1fr)",
  gap: 10,
};

// Five columns, newest number first (the server sorts). New tab on click.
export default function Gallery({ project, photos }) {
  if (!photos.length) {
    return (
      <Note size={13} style={{ color: "var(--ink-3)" }}>
        Henüz foto yok — sağdaki listeyi doldur, Üret'e bas.
      </Note>
    );
  }
  return (
    <div style={GRID}>
      {photos.map((file) => (
        <a key={file} href={photoUrl(project, file)} target="_blank" rel="noreferrer"
           style={{ display: "flex", flexDirection: "column", gap: 4, textDecoration: "none" }}>
          <img src={photoUrl(project, file)} alt={file}
               style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                        border: "1px solid var(--border)", borderRadius: 3 }} />
          <Mono size={10} style={{ color: "var(--ink-3)" }}>{file}</Mono>
        </a>
      ))}
    </div>
  );
}
