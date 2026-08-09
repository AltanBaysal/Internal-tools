import "./shared/app.css";
import "./features/workspace/workspace.css";

import HomeScreen from "./features/workspace/HomeScreen.jsx";
import ProjectScreen from "./features/workspace/ProjectScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useProjects } from "./features/workspace/useProjects.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const { projects, error, createProject, editProject } = useProjects();

  const openProject = (id) => navigate(`/p/${id}`);
  const goHome = () => navigate("/");

  // The screen reads its project out of the list the app already holds; asking the server a second
  // time would be asking for an answer we have.
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  const ask = (question, current, field) => {
    const answer = window.prompt(question, current);
    // An empty answer cancels -- the design's rule. The server refuses an empty name anyway, so
    // this is a convenience rather than the guarantee.
    if (answer && answer.trim()) editProject(route.projectId, { [field]: answer });
  };

  return (
    <div className="app-shell" data-testid="app-shell">
      <Sidebar
        projects={projects}
        activeProjectId={route.projectId}
        onNewChat={goHome}
        onNewProject={createProject}
        onOpenProject={openProject}
      />
      <main className="main">
        {/* Creating a project keeps the user on home: its own screen is Madde 6, and what this item
            has to show is the project appearing in both lists at once. */}
        {route.view === "home" ? (
          <HomeScreen
            projects={projects}
            error={error}
            onNewProject={createProject}
            onOpenProject={openProject}
          />
        ) : null}

        {route.view === "project" ? (
          <ProjectScreen
            project={project}
            onBack={goHome}
            onRename={() => ask("Project name", project?.name, "name")}
            onDescribe={() => ask("Project description", project?.desc, "desc")}
          />
        ) : null}
      </main>
    </div>
  );
}
