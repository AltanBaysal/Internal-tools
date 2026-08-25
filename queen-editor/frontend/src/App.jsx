import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import ExportScreen from "./features/photo_generation/ExportScreen.jsx";
import PhotoDetail from "./features/photo_generation/PhotoDetail.jsx";
import { routeFromPath, useRoute } from "./shared/router.js";

// The record fills the photo panel's boxes and nothing else on the screen reads it, so the screen
// is drawn whatever became of it and the one panel that asked carries the waiting (madde 31).
// The status is not passed on as a status: what a panel needs to know is whether it has the record,
// and if not, whether something went wrong.
function ProjectRoute({ project }) {
  const { status, settings, error, save, reload } = useProjectSettings(project);
  return (
    <ProjectScreen project={project}
                   settings={status === "ready" ? settings : null}
                   settingsError={status === "error" ? error : null}
                   onRetrySettings={reload}
                   onSaveSettings={save} />
  );
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
