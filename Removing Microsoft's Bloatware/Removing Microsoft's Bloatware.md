---
title: What Microsoft leaves behind on a Mac, and how to remove all of it
published: false
description: Dragging Office to the Trash leaves an updater, launch agents and a root helper running. This is a tour of where they hide, and of a script that removes them without breaking the apps you keep.
tags: macos, bash, cli, sysadmin
---
# Removing Microsoft's Bloatware

## The updater that outlived its apps

About a year ago I deleted Office from my Mac the way every Mac user is taught to delete anything, by dragging it to the Trash, and two weeks later Microsoft AutoUpdate opened a window to offer me updates for the applications I no longer had. The moment was funny, but it pointed at something real, because the Trash only works as an uninstaller when an app keeps all of itself inside its own bundle, and Microsoft's software does not. What looks like a handful of applications in `/Applications` is the visible top of a platform that installs its own updater, registers background jobs with the system, and parks a helper tool that runs as root, and none of those pieces live inside the apps you can see.

You can check this on your own machine with two commands, and Figure 1 shows what they printed on mine. The first lists Microsoft's entries in the three system folders where software asks macOS to run something on its behalf, and the second opens one of those entries to show when it runs.

![Figure 1. The AutoUpdate agent, daemon and root helper in /Library](fig-01-autoupdate-leftovers.png)
Figure 1. The AutoUpdate agent, its daemon and its root helper sit in /Library, outside every app bundle, and the agent is set to start at login and again every 7,200 seconds.

Each of the three files does a different job. `com.microsoft.update.agent.plist` is a launch agent, a small property list that tells launchd, the process that starts and supervises background work on macOS, to run Microsoft Update Assistant whenever someone logs in (`RunAtLoad`) and every two hours after that (a `StartInterval` of 7,200 seconds). The plist in `LaunchDaemons` describes `com.microsoft.autoupdate.helper`, and because launch daemons run in the system domain rather than inside a user's session, the binary it points to in `PrivilegedHelperTools` runs as root and offers services with names like `install`, `clone` and `cleanup`. That arrangement is how AutoUpdate replaces apps in `/Applications` without asking for your password each time, and it is also why deleting Word does nothing to it. The helper was installed once, by a package you approved, it has no window and no menu, and nothing in the Finder will ever show it to you.

I ended up writing a script, [`ms-uninstall.sh`](https://github.com/eugenezimin/development-utilities/tree/main/ms-uninstall), to find and remove all of this properly. The deleting turned out to be the easy part, since it comes down to `mv` or `rm`, and almost all of the work went into two other questions, namely which files belong to which product, and how to avoid deleting anything that a product you decided to keep still needs. The rest of this article follows the script in the order in which it answers them.

## Finding Microsoft's leftovers

The obvious first move is to search `/Applications` for anything whose name starts with "Microsoft", and it fails almost at once. Remote Desktop is now called Windows App, Teams has shipped as both "Microsoft Teams classic" and plain "Microsoft Teams", and OneDrive has never carried the company's name in its title. Names belong to marketing, and marketing renames things.

What does not change is the bundle identifier, a reverse-DNS string such as `com.microsoft.Word` that every app declares in its `Info.plist` under the key `CFBundleIdentifier`. macOS keys nearly everything about an app on that string, from the location of its sandbox to the name of its preferences file, which makes it the one name worth matching on. Figure 2 sets the two kinds of name side by side for the apps that make the point most clearly.

![Figure 2. Finder names versus bundle identifiers](fig-02-names-vs-ids.png)
Figure 2. Finder names drift with every rebrand, while the bundle identifier that macOS stores data under stays put, so matching on com.microsoft.* finds apps that a search by name would miss.

Reading the identifier takes a single command in principle, and the script wraps it in a small function that tries two different readers in turn.

```bash
bundle_id_of() {
  local plist="$1/Contents/Info.plist"
  [[ -f "$plist" ]] || return 0
  defaults read "$1/Contents/Info" CFBundleIdentifier 2>/dev/null || \
  plutil -extract CFBundleIdentifier raw -o - "$plist" 2>/dev/null || true
}
```

`defaults` reads most property lists without complaint, `plutil` serves as the fallback for the ones it cannot parse, and the closing `|| true` makes an unreadable bundle return an empty string instead of halting a script that runs under `set -euo pipefail`. With that function in hand, the scan walks `/Applications`, `/Applications/Utilities` and `~/Applications`, keeps every bundle whose identifier begins with `com.microsoft.` or `com.skype.`, and adds one last entry for Microsoft data that no installed app claims. Figure 3 is that first screen on my Mac, which currently has Teams and Windows App installed.

![Figure 3. The discovery screen of ms-uninstall.sh](fig-03-discovery.png)
Figure 3. The discovery screen lists each product with its bundle identifier, its total size and the number of paths it owns, followed by leftovers that no installed app claims.

The sizes are the first surprise. The Teams bundle itself weighs 1.1 GB, yet the product comes to 3.4 GB, because its container in `~/Library` holds another 2.3 GB that dragging the app to the Trash would have left exactly where it was. The "12 items" beside it raises the obvious next question, which is where those twelve paths come from.

## Where each app actually lives

A modern Mac app keeps its state in a set of well-known folders, each named after its bundle identifier, so that once you know the identifier you can predict nearly every place the app has written to. Figure 4 maps those places, using Teams as the example and grouping the folders by what they hold rather than by where they sit.

![Figure 4. One bundle identifier spread across ~/Library and /Library](fig-04-one-app-many-places.png)
Figure 4. One bundle identifier spreads across about two dozen locations in ~/Library and /Library, and the red column, the part that keeps running, is the part people forget.

The green column holds the app's real data. `Containers/$id` is the sandbox, a private home directory that macOS gives every sandboxed app, complete with its own `Data/Documents` and `Data/Library`, and it is usually the largest piece by far. The yellow column holds what the app can rebuild on its own, such as caches, web storage, cookies and logs. Those first two columns are the ones people remember when they clean up by hand, and they are also the least harmful to leave behind, since a stale cache takes up space but never does anything.

The red column is different in kind. A launch agent in `~/Library/LaunchAgents` runs as you when you log in, an agent in `/Library/LaunchAgents` runs in the session of every user on the machine, and a launch daemon in `/Library/LaunchDaemons` runs as root from boot, usually pointing at a binary in `PrivilegedHelperTools`. Each of these files is an instruction to launchd, and launchd carries it out whether or not the app that wrote it still exists, which is the entire story behind Figure 1.

In the script, all of this lives in one function that turns an identifier into candidate paths and prints the ones that exist. The excerpt below keeps the pattern and trims the middle of the list.

```bash
paths_for_id() {
  local id="$1" p
  shopt -s nullglob
  local cands=(
    "$HOME_DIR/Library/Containers/$id"
    "$HOME_DIR"/Library/Containers/"$id".*
    "$HOME_DIR/Library/Application Scripts/$id"
    "$HOME_DIR"/Library/Application\ Scripts/"$id".*
    "$HOME_DIR/Library/Preferences/$id.plist"
    # ... caches, cookies, saved state, logs, launch agents ...
    "/Library/LaunchDaemons/$id.plist"
    "/Library/PrivilegedHelperTools/$id"
  )
  shopt -u nullglob
  for p in "${cands[@]+"${cands[@]}"}"; do
    [[ -e "$p" || -L "$p" ]] && printf '%s\n' "$p"
  done
}
```

The `"$id".*` patterns are there because apps ship extensions alongside themselves, and macOS sandboxes each extension separately, so Teams owns `com.microsoft.teams2` together with `com.microsoft.teams2.agent`, `.notificationcenter`, `.respawn` and `.widgetextension`, every one of them with a container and an `Application Scripts` folder of its own. Orphan discovery leans on the same naming rule from the other side, skipping any folder whose name begins with an installed product's identifier, so that a widget extension is never mistaken for a leftover of an app that is gone. The `nullglob` setting, meanwhile, stops a pattern that matches nothing from expanding to itself, since without it bash would hand the literal string `.../com.microsoft.teams2.*` to the loop as though it were a path. The existence test at the bottom would catch that string here, but literal patterns are the most dangerous thing a removal script can produce, and section 8 comes back to them.

## One product under many faces

Prefix matching handles extensions, but it cannot help when a product's helpers carry identifiers that share no prefix with the app. OneDrive is the clearest case. The app you see is `com.microsoft.OneDrive`, while its updater, its standalone updater, the daemon behind that standalone updater, its launcher and its SharePoint integration each have identifiers of their own, and several of them install launch items. Figure 5 shows the whole family.

![Figure 5. OneDrive expanded into seven bundle identifiers](fig-05-onedrive-family.png)
Figure 5. A single visible OneDrive.app expands into seven bundle identifiers, and each one is searched separately for preferences, caches and launch items.

Nothing inside the app bundle mentions these relatives, so the only option is to look them up once and write them down. The script keeps them in a `case` statement that is about as glamorous as a phone book.

```bash
sibling_ids() {
  case "$1" in
    com.microsoft.OneDrive*)
      printf '%s\n' com.microsoft.OneDrive com.microsoft.OneDrive-mac \
        com.microsoft.OneDriveUpdater com.microsoft.OneDriveStandaloneUpdater \
        com.microsoft.OneDriveLauncher com.microsoft.SharePoint-mac \
        com.microsoft.OneDriveStandaloneUpdaterDaemon ;;
    com.microsoft.wdav*)
      printf '%s\n' com.microsoft.wdav com.microsoft.wdav.tray com.microsoft.wdav.epsext \
        com.microsoft.wdav.netext com.microsoft.dlp com.microsoft.dlp.daemon ;;
    # ... Teams, Edge, Outlook, AutoUpdate, Remote Desktop ...
    *) printf '%s\n' "$1" ;;
  esac
}
```

Defender, which identifies itself as `com.microsoft.wdav`, is the other large family, bringing a menu bar app, a network extension, an endpoint security extension and two data loss prevention components along with it. Every discovered app passes through `sibling_ids` first, and every identifier that comes out passes through `paths_for_id`, so the list that finally reaches you covers the whole product rather than only the part with an icon. A table like this goes stale whenever Microsoft ships a new helper, which is the price of knowledge that cannot be derived from the system, and the orphan entry at the bottom of the menu exists partly to catch whatever the table misses.

## Shared parts and the keeper's veto

Removing everything is straightforward. The hard case, and the common one, is removing only some things, Teams but not Word, say, or Office but not the Defender agent your employer requires, because Microsoft's shared components really are shared, and deleting one on behalf of an app you are removing can quietly break an app you are keeping.

The group container is the best example. Apps signed by the same developer can share a folder in `~/Library/Group Containers` named after that developer's Apple team ID, and Microsoft's team ID is `UBF8T346G9`. Word and Excel keep settings and autosave state in those folders, and Outlook keeps its entire local mail store under `UBF8T346G9.Office`, so deleting that folder while Outlook is still installed uninstalls nothing at all and simply empties someone's mailbox. AutoUpdate, which serves every Microsoft product at once, and the fonts in `/Library/Fonts/Microsoft`, which anything that opens a `.docx` relies on, are in the same position.

The script's answer is to make every dependency explicit. Each shared component is registered with the bundle identifier prefixes of the apps that still need it, and each product you decide to keep becomes a keeper that holds a veto over the components it relies on. Here is the registration for the group containers, exactly as it appears in the script.

```bash
shared_add "Office group containers (documents, settings, Outlook mail store)" \
  "com.microsoft.Word com.microsoft.Excel com.microsoft.Powerpoint com.microsoft.Outlook com.microsoft.onenote.mac com.microsoft.OneDrive com.microsoft.teams com.microsoft.rdc com.microsoft.wdav com.microsoft.CompanyPortalMac com.skype." \
  "$HOME_DIR"/Library/Group\ Containers/UBF8T346G9.* \
  "$HOME_DIR"/Library/Application\ Scripts/UBF8T346G9.*
```

The second argument is the list of apps with a claim on the component. Once you have made your selection, the script gathers the identifiers of every product you did not select, and any shared component whose list matches one of them is marked as kept and taken off the menu. Figure 6 traces that logic for a typical case, in which all of Office goes and Teams stays.

![Figure 6. Kept apps veto the shared components they depend on](fig-06-veto.png)
Figure 6. Teams still depends on AutoUpdate and on the group containers, so both stay, while the Office helper data and the fonts, which only Office apps need, are offered for removal.

The dashed lines matter as much as the solid ones. Word, Excel and the others depend on the group containers too, but they are leaving, so their claims no longer count, and the only thing standing between those folders and the Trash is Teams.

A vetoed component is still printed, together with the reason, because hiding it would leave you wondering why a 214 MB folder survived, whereas a line naming the app that holds it back tells you exactly which answer to change if that was not what you meant. Figure 7 is a real dry run on my Mac in which I chose Teams and kept Windows App.

![Figure 7. Shared components marked KEPT during a dry run](fig-07-veto.png)
Figure 7. With Windows App kept, every shared component is marked KEPT and labeled with the app that needs it, so removing Teams touches only Teams' own files.

## Read the plan! Before, not After!

Everything described so far only reads the disk. Nothing changes until the script has shown you the complete plan, and with `--dry-run` it stops at exactly that point, which makes a dry run the right first command on any Mac. Figure 8 shows the plan for the most aggressive choice available, every product and every shared component, trimmed where the lists repeat themselves.

![Figure 8. The removal plan for a full removal](fig-08-plan.png)
Figure 8. The removal plan groups every path by product with its size, warns about files inside containers that are about to go, and ends with a total and the removal method.

The note at the top exists because some apps keep real documents inside their sandbox, in `Data/Documents`, and the script lists them before the plan so that you can copy them out first. Here the only file is a `README.txt` from Windows App's health checks, but on a Mac that has run Office for years the same note can reveal a folder of files you assumed were somewhere else. Lower down, the `[Keychain]` block appears only when no Office app is being kept, and it removes the cached sign-in and license entries that Office stores in the login keychain, at the cost of signing in again if you ever reinstall. The closing lines state the method, and the default is a move to `~/.Trash`.

Without `--dry-run`, the script asks you to type the word `REMOVE` exactly, treats any other answer as a cancellation that exits with code 3, and refuses to continue at all when standard input is not a terminal, so that a confirmation can never be piped in by accident. For automation there are `--select` and `--shared`, which accept the same answers you would type at the two prompts, such as `1,3` or `all`, but even then the final `REMOVE` has to come from a person at the keyboard.

One preparation is easy to miss. macOS shields the data in app containers from other processes, and a terminal without Full Disk Access receives "Operation not permitted" when it tries to read `~/Library/Group Containers/UBF8T346G9.*`. On my Mac that made the group containers appear as 0 MB until I granted Full Disk Access to my terminal in System Settings, under Privacy & Security, and a real removal would have failed on those folders halfway through. Grant the permission before you run the script, and revoke it afterward if you prefer to keep your terminal unprivileged.

## Run it!

Once you confirm, the removal proceeds in four steps, and their order is anything but arbitrary, since each step exists to prevent a specific failure that the next one would otherwise cause. Figure 9 pairs every step with the failure it prevents.

![Figure 9. The four removal steps and what each prevents](fig-09-order-of-operations.png)
Figure 9. The script quits the apps, unloads their launch jobs, moves their files and restarts cfprefsd, in that order, and each box below shows what goes wrong when the step above it is skipped.

The apps go first. The script asks each running app to quit through AppleScript, which gives it the chance to save its work or to ask you to, then checks with `pgrep` two seconds later and aborts the whole run if the app is still alive, because a save dialog left open is precisely the situation in which deleting files would destroy work. The launch jobs come next, unloaded with `launchctl bootout` while their plists still exist, since launchd keeps a loaded job in memory after its plist disappears, and a deleted agent with an interval like AutoUpdate's would go on trying to fire every two hours until the next reboot. Only after both of those steps does any file move.

The final step looks like an afterthought.

```bash
killall cfprefsd >/dev/null 2>&1 || true
```

`cfprefsd` is the daemon through which every app's preferences pass, and it caches the contents of preference files in memory, so if it stays running after the plists are gone it can write the cached values back to disk, which is the usual explanation for a deleted preference that reappears a few minutes later. Killing it is safe, because launchd restarts it at once and the fresh copy reads only what is actually on disk.

## Guard rails

A script that runs `rm -rf` under `sudo` deserves protections beyond a confirmation prompt, however much its author trusts it, and this one has two.

The first is the Trash default. Every path moves to `~/.Trash` unless you pass `--hard-delete`, and when two items share a name, as the three separate folders called `Microsoft` do, the later arrivals receive a timestamped suffix instead of overwriting the earlier ones. Paths that needed `sudo` to move are handed back to your user afterward, so that you can empty the Trash, or drag something back out of it, without a password. Uninstalling is the one operation where you tend to discover an hour later that some container held the only copy of something, and the Trash turns that discovery from a restore from backup into a drag and drop.

The second is a denylist inside `remove_path`, checked against every path immediately before it is touched.

```bash
case "$path" in
  /|/Applications|/Applications/Utilities|/Library|/Library/Fonts|/Library/Caches|\
  /Library/Preferences|/Library/LaunchAgents|/Library/LaunchDaemons|\
  /Library/PrivilegedHelperTools|/Library/Application\ Support|\
  "$HOME_DIR"|"$HOME_DIR"/Library|"$HOME_DIR"/Library/Containers|\
  "$HOME_DIR"/Library/Preferences|"$HOME_DIR"/Library/Caches|\
  "$HOME_DIR"/Library/Group\ Containers|"$HOME_DIR"/Library/LaunchAgents|\
  "$HOME_DIR"/Library/Application\ Support)
    die "internal: refusing to delete $path" ;;
esac
```

None of these paths should ever reach this point, and that is exactly why the check is there. Removal scripts classically go wrong in one of two ways, either through a variable that turns out to be empty, so that a path built as `"$dir/$id"` collapses to `/`, or through a glob that matches nothing and survives as a literal, and in both cases a precise delete becomes the deletion of a parent directory. The script already defends against each of those separately, with `set -u` for unset variables, `nullglob` for patterns, and a refusal to run as root at all, so the denylist serves as the final check, cheap enough to keep even though it should never fire.

## What's left, and what to leave

A completed run ends with a verification sweep that lists any Microsoft items still on disk and any Microsoft processes still running, and on a Mac where you kept something, some of both are expected. A few things fall outside the script's reach even after a full removal, and Figure 10 shows two of them on my machine.

![Figure 10. Package receipts and the Teams audio driver](fig-10-receipts.png)
Figure 10. Package receipts outlive the files they describe, and one of them points to a Teams audio driver in /Library/Audio/Plug-Ins/HAL that the script does not yet look for.

Package receipts come first. macOS records every installer package in a database of its own, so `pkgutil --pkgs` keeps listing Microsoft packages after their files are gone, which is harmless bookkeeping that `sudo pkgutil --forget <package-id>` will clear if it bothers you. The receipts earn their keep in another way, because you can ask any of them what it installed, and that is how I found `MSTeamsAudioDevice.driver`, a virtual audio device that Teams places in `/Library/Audio/Plug-Ins/HAL` so that it can share your computer's sound during a meeting. It belongs to none of the bundle identifiers the script searches, so it survives a Teams removal, and until the script learns about it, two commands remove it by hand.

```bash
sudo rm -rf /Library/Audio/Plug-Ins/HAL/MSTeamsAudioDevice.driver
sudo killall coreaudiod
```

The second command restarts Core Audio, so the device drops out of the sound settings without a reboot.

Edge escapes for a related reason, since it keeps its profile in `~/Library/Application Support/Microsoft Edge`, a folder named after the product rather than its identifier, which the per-identifier search never reaches and the shared `Microsoft` folder does not include. Visual Studio Code genuinely is `com.microsoft.VSCode` and appears in the list like everything else, which is one more reason to read the list before typing `all`. If your employer manages your Mac, leave Defender, Company Portal and the Intune agent alone entirely, because device management will put them back at its next check-in, and the removal is likely to raise a compliance alert along the way.

The gentlest way to begin is `./ms-uninstall.sh --dry-run`, which runs the discovery, prints the plan and changes nothing. That output is worth seeing even if you never remove a thing, because the honest answer to the question of what Microsoft is running on your Mac tends to be longer than you would guess. On mine it came to a 3.4 GB chat app, an agent that wakes every two hours, a helper that runs as root, and an audio driver I had never heard of, and once you can read a list like that, the Trash looks less like an uninstaller and more like the first of several steps.
