# A Clean and Fast macOS Terminal with Ghostty, Starship, and Antidote

My terminal is where I spend most of my working day, yet for years my setup was one long `.zshrc`, a full framework I only used a fraction of, and a home folder full of hidden files I couldn't explain. In the last few weeks, I sat down and rebuilt it from the ground up around three small tools: Ghostty, starship, and antidote.

So, below, you will find a short walkthrough of that setup, along with a few suggestions for keeping your home folder clean without breaking anything. All config files are in my [development-utilities](https://github.com/eugenezimin/development-utilities/tree/main/initial-install) repository. In my experience, reading through a few small config files is still the best way to understand how a shell really starts up.

## How Ghostty, zsh, antidote, and starship fit together

As a small side note, and since these names often get mixed up, here's how the pieces relate.

If we think of the setup as a car, **zsh** is the engine. **antidote** is the parts manager that bolts plugins onto the engine (completion, syntax highlighting, git aliases). **starship** is the dashboard that shows where you are and what state your repo is in. And **Ghostty** is the body around it: the terminal emulator that draws everything quickly on the GPU.

Each of these can be swapped out on its own, which is the main reason I like this combination over an all-in-one framework.

![Terminal greeting and prompt in Ghostty](greeting.png)

*Figure 1: The end result in a new Ghostty tab. A one-table system summary, followed by a two-line starship prompt.*

## Scope and prerequisites

This setup targets macOS (Apple Silicon or Intel) with [Homebrew](https://brew.sh). Installing the tools takes one line each:

```bash
brew install --cask ghostty
brew install antidote starship
```

There's no need to install a patched font for the icons, since Ghostty bundles the Nerd Font symbols. (In iTerm2 or Terminal.app you would need a Nerd Font, otherwise the icons show up as boxes.)

## 1. Ghostty: the terminal

Ghostty is fast, native on macOS, and configured through a single plain-text file. Instead of the default `~/Library/Application Support/com.mitchellh.ghostty/` location, I keep that file at `~/.config/ghostty/config.ghostty`, next to everything else. Here is a trimmed version of mine:

```ini
font-family = "Nordwand Mono"
font-size = 13
background-opacity = 0.92
background-blur-radius = 15
cursor-style = underline

keybind = global:cmd+grave_accent=toggle_quick_terminal

shell-integration = zsh
shell-integration-features = no-title,ssh-terminfo
copy-on-select = clipboard
mouse-hide-while-typing = true
```

Most of these lines are a matter of taste, but two of them changed how I work. The first is the `keybind` line, which turns Ghostty into a drop-down "quick terminal": wherever I am, whether in the browser, the editor, or a PDF, Cmd+` slides a terminal down from the top of the screen, and the same key sends it away again. After a week, I stopped opening terminal windows for quick commands altogether.

The second is the shell integration line. I keep Ghostty's integration on, but switch off its tab titles with `no-title`, because I like my tabs to tell me a little more. A small zsh hook in `conf.d/60-ghostty-title.zsh` names each tab after the folder, the git branch, and the command that's running, so a tab reads, for example, `acme-api - main - cargo`. With five tabs open, that's the difference between finding the right one at a glance and clicking through all of them. The `ssh-terminfo` feature, finally, quietly teaches remote hosts about Ghostty's terminal type, so colours and keys keep working when I SSH into a server.

## 2. Keeping the home folder clean

By default, zsh reads `~/.zshrc`, `~/.zprofile`, `~/.zsh_history`, and friends, all straight from your home folder. The trick is a single variable, `ZDOTDIR`, which tells zsh where to look instead.

The only zsh file left in `~` is a three-line `~/.zshenv`:

```zsh
# zsh reads this file before ZDOTDIR is known; everything else lives in ~/.config/zsh.
export ZDOTDIR="$HOME/.config/zsh"
[[ -r "$ZDOTDIR/.zshenv" ]] && source "$ZDOTDIR/.zshenv"
```

The nice part is that macOS plays along. `/etc/zshrc` sets `HISTFILE=${ZDOTDIR:-$HOME}/.zsh_history`, and Terminal's session files go to `${ZDOTDIR:-$HOME}/.zsh_sessions`, so both follow you into `~/.config/zsh` with no extra config.

Everything else now lives together in `~/.config/zsh`: the `.zshrc` and `.zprofile`, the plugin list, and a `conf.d/` folder with small numbered files for options, environment variables, aliases, and functions. Instead of scrolling through one long file, I open the one file that's about the thing I want to change. API keys and tokens get a file of their own, `.zsh_secrets`, readable only by me (chmod 600) and never copied into the repository, so I can share my dotfiles without worrying about leaking anything. Caches stay out of sight as well: starship and the greeting write to `~/.cache`, and antidote keeps its plugin clones in `~/Library/Caches/antidote`.

There's one catch I ran into myself. After the switch, the old `~/.zsh_history` and `~/.zsh_sessions` are still sitting in your home folder, but nothing reads them anymore, so your shell suddenly seems to have forgotten every command you ever typed. The fix is to move the history over *before* you open your first new shell (`mv ~/.zsh_history ~/.config/zsh/`), and then delete `~/.zsh_sessions`. In the same spirit, keep in mind that an old `~/.zshrc` is silently ignored once `ZDOTDIR` is set, which can be confusing if you forget it's there.

And if you'd like to go further, many other tools can be convinced to move out, too. Rust, for example, reads `CARGO_HOME` and `RUSTUP_HOME`, and npm reads `NPM_CONFIG_CACHE`. The trick is to set these in `$ZDOTDIR/.zshenv` *before* installing the tool. Otherwise, you'll need to move the existing folders yourself.

![A clean home folder](home-clean.png)

*Figure 2: The home folder before (Oh My Zsh and Powerlevel10k, everything in `~`) and after the `ZDOTDIR` switch, where a single `.zshenv` is left. The listings are demo values.*

## 3. Antidote: plugins without a framework

I used Oh My Zsh for years, but I only needed a handful of its files. antidote reads a plain list of plugins, builds a static bundle from it, and only rebuilds that bundle when the list changes, so startup stays fast.

```text
getantidote/use-omz                      # Oh My Zsh pieces, without the framework
ohmyzsh/ohmyzsh path:lib/history.zsh
ohmyzsh/ohmyzsh path:plugins/git
marlonrichert/zsh-autocomplete           # completion menu as you type
zsh-users/zsh-syntax-highlighting        # must stay last
```

The first line, `use-omz`, is what makes this work. It lets me pick individual Oh My Zsh files, like the history settings or the git aliases I've had in my fingers for years, without loading the framework around them.

The order of the list matters more than it looks, though. `zsh-autocomplete` sets up completion on its own, so it needs to come after the Oh My Zsh pieces, and `zsh-syntax-highlighting` wants to see every other plugin first, so it always goes last. I learned both of these the hard way, so I left myself comments in the file.

Day to day, I hardly think about antidote at all. When I add a line to the list, the next shell picks it up, and every few weeks I run `antidote update` to pull the latest version of everything.

## 4. Starship: the prompt

Finally, starship draws a two-line prompt modelled on Powerlevel10k's "lean" style. Line one shows the path and git state. Line two holds the `❯` input marker, with status and project information on the right.

![Prompt in different folders and git states](prompt-gallery.png)

*Figure 3: The prompt in different repos: local changes, a deep subfolder, a detached tag, a rebase in progress, and a read-only folder.*

The first line is where the git information lives, and it's the part I'd miss most. In the top row of the figure, `⇡2 +1 !2 ?1 *1` tells me, without typing `git status`, that I have two commits I haven't pushed, one staged file, two modified files, an untracked file, and something stashed. A clean repo shows nothing but the branch name, so when the line is short, I know I'm done.

The path took the most work to get right. Long paths are hard to read, but cutting them down too far loses track of which project I'm in. So parent folders are shortened to a single letter, while the repo root and the current folder stay whole: deep inside a project, the prompt reads `~/D/acme-api/s/h/auth`. Starship can't do this on its own, so a small pure-zsh function in `prompt.zsh` works out the pieces before each prompt.

The right side stays empty most of the time and only fills in when there's something worth saying, like a failed command's exit code, a command that ran longer than three seconds, or the package and language versions in a project folder. If you ever wonder what a symbol means or why the prompt feels slow, `starship explain` and `starship timings` will tell you.

## Final words

You don't have to adopt all of this at once. In fact, I'd suggest starting with the `ZDOTDIR` change, since it's three lines and immediately tidies up your home folder. Then add antidote and starship one at a time and open a new tab after each step.

If you'd rather not copy files by hand, the installer in the same repo can restore just this part: run `./install-all-macos.sh --dry-run` first, and select only the `shell` step.

Thanks for reading, and I hope you enjoy your new terminal!
