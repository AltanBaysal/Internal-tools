"""List projects oldest first -- the order both the sidebar and the home cards show."""


def list_projects(store):
    # The id is opaque, so it says nothing about age; createdAt is the only thing that does. The id
    # is the tie-break so two projects created in the same second still come back in a fixed order.
    return sorted(store.list_all(), key=lambda project: (project.created_at, project.id))
