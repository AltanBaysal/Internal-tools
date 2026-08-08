const PLACEHOLDER = "Yeni proje";

// A project's name is stored, not derived: unlike a chat title there is nothing inside a project to
// derive it from, and the person who made it is the one who knows what it is for.
export function createProject(projects, rawName) {
  const name = rawName.trim() || PLACEHOLDER;
  const id = projects.reduce((max, project) => Math.max(max, project.id), 0) + 1;
  return { projects: [...projects, { id, name }], id };
}

export function deleteProject(projects, id) {
  return projects.filter((project) => project.id !== id);
}

// Deleting a project takes its files with it and cannot be undone, which is why the confirmation
// counts them out loud instead of asking "are you sure".
export function projectContents(projectId, files, chats) {
  return {
    files: files.filter((file) => file.projectId === projectId).length,
    chats: chats.filter((chat) => chat.projectId === projectId).length,
  };
}
