import "./shared/app.css";
import "./features/workspace/workspace.css";

import HomeScreen from "./features/workspace/HomeScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useProjects } from "./features/workspace/useProjects.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const { projects, error, createProject } = useProjects();

  const openProject = (id) => navigate(`/p/${id}`);

  return (
    <div className="app-shell" data-testid="app-shell">
      <Sidebar
        projects={projects}
        activeProjectId={route.projectId}
        onNewChat={() => navigate("/")}
        onNewProject={createProject}
        onOpenProject={openProject}
      />
      <main className="main">
        {/* Creating a project keeps the user on home: its own screen is Madde 6, and the acceptance
            for this one is seeing the project appear in both lists at once. */}
        {route.view === "home" ? (
          <HomeScreen
            projects={projects}
            error={error}
            onNewProject={createProject}
            onOpenProject={openProject}
          />
        ) : null}
      </main>
    </div>
  );
}
