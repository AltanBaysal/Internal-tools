import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import { projectFromPath, useRoute } from "./shared/router.js";

export default function App() {
  const project = projectFromPath(useRoute());
  return project ? <ProjectScreen project={project} /> : <ProjectsScreen />;
}
