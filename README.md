![Featured Image](https://github.com/martin-lorentzon/text-editor-for-development/blob/main/images/featured_image.png?raw=true)

# Text Editor for Development (Blender Add-on)
> *Text Editor enhancements for add-on development*

> ❓ ***Is this a complete IDE?***  
> No, we still recommend using a program such as VSCode for any serious add-on development  
> This extension exists to improve the usability of Blender’s text editor—especially when starting out in Blender may be more feasible due to, for example, imposed time constraints

# Report Issues [Here](https://github.com/martin-lorentzon/text-editor-for-development/issues)

## Features
- VSCode-style folder-view/explorer
- Clone [multi-file add-on template](https://github.com/martin-lorentzon/clean-blender-addon-template) to a local directory

## Usage
- Explorer: `Text Editor → Sidebar → Dev → Explorer`  
- Add-on Template: `Text Editor → Templates → New Add-on`  

## Preferences
- **Default File Name:** The default name for new files  
- **Default Folder Name:** The default name for new folders
- **Show Hidden Items:** Shows hidden items in the folder view
- **Unlink on File Deletion:** Removes texts from the current blend-file once deleted

## Requirements
- [**Git**](https://git-scm.com/downloads) added to PATH (to clone remote content/repositories)  
    (This can be accomplished during the installataion of Git)

## Compatibility
The extension has been tested using Blender 4.5.1 LTS  
Please report any problems around backward compatibility using [GitHub Issues](https://github.com/martin-lorentzon/text-editor-for-development/issues), same link as above

## Permissions
- **Network:** Prompt the user to download/install Git and clone remote repositories
- **Files:** Open folder for viewing/editing/renaming/sending files to trash

## Roadmap
| Feature                                            | Status     | Priority |
| -------------------------------------------------- | ---------- | -------- |
| VSCode-like folder view                            | ✅ Done     | –        |
| Cloning of remote content (e.g., add-on templates) | ✅ Done     | –        |
| BPY self-paced learning material                   | ⬜ Not Done | ⚡⚡⚡  |
| Reuse of code snippets + Context menu redesign     | ⬜ Not Done | ⚡       |
| ❔                                                 | ⬜ Not Done | –        |
