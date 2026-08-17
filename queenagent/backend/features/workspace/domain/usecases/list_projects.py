"""List projects oldest first -- the sidebar's order, and so the first one the app opens on."""


def list_projects(store):
    # The id is opaque, so it says nothing about age; createdAt is the only thing that does. The id
    # is the tie-break so two projects created in the same second still come back in a fixed order.
    return sorted(store.list_all(), key=lambda project: (project.created_at, project.id))
