"""Read the settings. Nothing has to have been saved for this to answer."""


def read_settings(settings_store):
    return settings_store.get()
