import ProjectLoading from "./features/photo_generation/ProjectLoading.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
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
  const { project, photo } = routeFromPath(useRoute());
  if (!project) return <ProjectsScreen />;
  // The detail page reads the photo list itself, so it does not wait for the project's settings.
  if (photo) return <PhotoDetail project={project} file={photo} />;
  return <ProjectRoute project={project} />;
}
