import { ImgPH, Btn, Icon, Mono, Seq } from "../../components/primitives";
import { useEditor } from "./useEditor";
import EditorTopBar from "./parts/EditorTopBar";
import SideComposer from "./parts/SideComposer";
import TimelineFooter from "./parts/TimelineFooter";
import DeleteConfirm from "./parts/DeleteConfirm";

const PROJECT_NAME = "İstanbul Film Notları";

/** Photo-generator editor — the single screen from the design, with all five
    states (empty · scene selected · add · generating · delete confirm) wired to
    real React state instead of separate artboards. */
export default function Editor() {
  const ed = useEditor();
  const { scenes, selection, selectedIdx, generating, deleteId } = ed;

  const isNew = generating?.kind === "new";
  const previewSeq = isNew ? scenes.length + 1 : selectedIdx + 1;
  const showImage = selection.kind === "scene" || generating != null;
  const deleteIdx = deleteId ? scenes.findIndex((s) => s.id === deleteId) : -1;

  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
      {/* Editor (blurred when the delete dialog is open) */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
          minHeight: 0,
          filter: deleteId ? "blur(2px)" : "none",
          opacity: deleteId ? 0.5 : 1,
          transition: "opacity .12s",
        }}
      >
        <EditorTopBar title={PROJECT_NAME} />

        <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
          <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
            <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
              {showImage ? (
                <>
                  <ImgPH
                    loading={generating != null}
                    style={{ width: "100%", height: "100%" }}
                    label={`scene ${previewSeq} preview`}
                  />
                  <div style={{ position: "absolute", top: 12, left: 12 }}>
                    <Seq n={previewSeq} xl hl />
                  </div>
                  {/* Trash only when a settled scene is selected (not while generating). */}
                  {selection.kind === "scene" && !generating && (
                    <div style={{ position: "absolute", top: 12, right: 12, display: "flex", gap: 6 }}>
                      <Btn sm ghost icon style={{ color: "var(--danger)", borderColor: "var(--danger)" }} onClick={() => ed.requestDelete(selection.id)}>
                        <Icon.Trash />
                      </Btn>
                    </div>
                  )}
                </>
              ) : (
                <div
                  className="wf-stroke wf-stroke--dashed"
                  style={{ width: "100%", height: "100%", background: "var(--bg-2)", display: "flex", alignItems: "center", justifyContent: "center" }}
                >
                  <Mono size={11} style={{ color: "var(--ink-3)" }}>
                    preview
                  </Mono>
                </div>
              )}
            </div>
          </section>

          <SideComposer
            value={ed.draft}
            onChange={ed.setDraft}
            onGenerate={ed.generate}
            mode={ed.mode}
            onModeChange={ed.setMode}
            disabled={generating != null}
          />
        </main>

        <TimelineFooter
          scenes={scenes}
          selectedIdx={selectedIdx}
          loadingAtEnd={isNew}
          addSelected={selection.kind === "add" && !generating}
          onSelect={ed.selectScene}
          onAdd={ed.startAdd}
          onPrev={() => ed.goto(-1)}
          onNext={() => ed.goto(1)}
          onReorder={ed.reorder}
        />
      </div>

      {deleteId && deleteIdx >= 0 && (
        <DeleteConfirm n={deleteIdx + 1} onCancel={ed.cancelDelete} onConfirm={ed.confirmDelete} />
      )}
    </div>
  );
}
