import ProjectLoading from "./features/photo_generation/ProjectLoading.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import { projectFromPath, useRoute } from "./shared/router.js";
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
  const project = projectFromPath(useRoute());
  return project ? <ProjectRoute project={project} /> : <ProjectsScreen />;
}
