import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import { projectFromPath, useRoute } from "./shared/router.js";

const EMPTY_SETTINGS = { prompts: "", negative: "", variants: null };

// The join lives here: settings belong to the projects feature, the gallery and the batch to
// photo_generation, and neither imports the other.
// Rendering waits for the settings so the panel's fields can start from them -- mounting empty and
// filling in afterwards would overwrite whatever the user had begun typing.
function ProjectRoute({ project }) {
  const { status, settings, error, save } = useProjectSettings(project);
  if (status === "loading") return null;
  return (
    <ProjectScreen
      project={project}
      settings={settings || EMPTY_SETTINGS}
      settingsError={error}
      onSaveSettings={save}
    />
  );
}

export default function App() {
  const project = projectFromPath(useRoute());
  return project ? <ProjectRoute project={project} /> : <ProjectsScreen />;
}
