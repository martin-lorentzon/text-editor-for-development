def uninitialized_preference(addon_prefs, prop):
    return addon_prefs.get(
                prop, 
                addon_prefs.bl_rna.properties[prop].default
            )