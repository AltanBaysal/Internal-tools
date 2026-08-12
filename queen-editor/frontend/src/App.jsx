import ProjectLoading from "./features/photo_generation/ProjectLoading.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import ExportScreen from "./features/photo_generation/ExportScreen.jsx";
import PhotoDetail from "./features/photo_generation/PhotoDetail.jsx";
import { routeFromPath, useRoute } from "./shared/router.js";
import { StatusErrorCard } from "./shared/StatusErrorCard.jsx";

function ProjectRoute({ project }) {
  const { status, settings, error, save, reload } = useProjectSettings(project);
  if (status === "loading") return <ProjectLoading project={project} />;
  if (status === "error") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center",
                    justifyContent: "center", padding: 32 }}>
        <StatusErrorCard text="Proje ayarları yüklenemedi" raw={error} onRetry={reload} />
      </div>
    );
  }
  return <ProjectScreen project={project} settings={settings} onSaveSettings={save} />;
}

export default function App() {
  // The photo segment carries the frame's identity: one picture can stand under two frames.
  const { project, photo, exporting } = routeFromPath(useRoute());
  if (!project) return <ProjectsScreen />;
  // The detail page reads the frame list itself, so it does not wait for the project's settings.
  if (photo) return <PhotoDetail project={project} frame={photo} />;
  // So does the export screen: it asks the server what an export would write.
  if (exporting) return <ExportScreen project={project} />;
  return <ProjectRoute project={project} />;
}
