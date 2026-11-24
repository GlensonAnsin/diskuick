"""Filipino (Tagalog) strings. Best-effort translation - please have a native speaker review.

Keys are the exact English UI strings; anything missing simply shows in English.
Keep {placeholders} unchanged.
"""
from i18n import FIL

FIL.update({
    # tabs / headings
    "Dashboard": "Dashboard", "Games": "Mga Laro", "Tools": "Mga Gamit", "Settings": "Mga Setting",
    "Keeps your drive awake while you play": "Pinapanatiling gising ang drive mo habang naglalaro",
    "Recent stalls": "Mga kamakailang pagtigil", "Drive health": "Kalusugan ng drive",
    "Lag check": "Pagsusuri ng lag", "Benchmark & auto-tune": "Benchmark at auto-tune",
    "Behaviour": "Pag-uugali", "Appearance": "Itsura", "When to run": "Kailan tatakbo",
    "Default intensity": "Default na lakas", "Live read latency": "Live na bilis ng pagbasa",
    # status
    "Active": "Aktibo", "Waiting": "Naghihintay", "Off": "Patay", "Error": "Error",
    "Disabled": "Naka-disable", "Idle": "Walang ginagawa", "Starting": "Nagsisimula",
    "Paused while on battery": "Naka-pause habang naka-baterya",
    "Choose a drive in Settings": "Pumili ng drive sa Settings",
    "Add games in the Games tab": "Magdagdag ng laro sa tab na Mga Laro",
    "Waiting for a game to start": "Naghihintay na magsimula ang laro",
    "Waiting for a game window to be in focus": "Naghihintay na nasa harapan ang window ng laro",
    # dashboard
    "Kept awake": "Oras na gising", "Sessions": "Mga session", "Stalls logged": "Naitalang pagtigil",
    "Enabled": "Naka-on", "No stalls recorded yet.": "Wala pang naitalang pagtigil.",
    "Each point is the slowest read in that second. Spikes above the red line are stalls - moments the drive hesitated.":
        "Ang bawat tuldok ay ang pinakamabagal na pagbasa sa segundong iyon. Ang pagtaas sa itaas ng pulang linya ay pagtigil - mga sandaling nag-atubili ang drive.",
    "Start a game (or choose “Always on”) to see live latency.":
        "Magsimula ng laro (o piliin ang “Laging naka-on”) para makita ang live na bilis.",
    "Waiting for data...": "Naghihintay ng datos...", "stall": "tigil", "now": "ngayon",
    "Update available": "May bagong bersyon", "Download": "I-download",
    # games
    "Detect installed games": "Hanapin ang mga naka-install na laro", "Scanning...": "Naghahanap...",
    "Add running program…": "Magdagdag ng tumatakbong programa",
    "or type a program name, e.g. game.exe": "o i-type ang pangalan ng programa, hal. game.exe",
    "Add": "Idagdag", "Drive": "Drive", "Intensity": "Lakas", "Default": "Default",
    "No games yet.\nClick “Detect installed games” to find them automatically.":
        "Wala pang laro.\nI-click ang “Hanapin ang mga naka-install na laro” para awtomatikong makita ang mga ito.",
    "Pick a running program": "Pumili ng tumatakbong programa",
    "Open your game first, then pick it here.": "Buksan muna ang laro mo, saka piliin dito.",
    "Search...": "Maghanap...", "Nothing found": "Walang nakita", "Detected games": "Mga nakitang laro",
    "No new games found.": "Walang bagong larong nakita.",
    "Looked in Steam, Epic Games and GOG. You can still add a game with “Add running program” or by typing its exe name.":
        "Hinanap sa Steam, Epic Games at GOG. Maaari mo pa ring idagdag ang laro gamit ang “Magdagdag ng tumatakbong programa” o sa pag-type ng pangalan ng exe nito.",
    "Choose the games to keep your drive awake for.": "Piliin ang mga larong gusto mong panatilihing gising ang drive.",
    "The program name is a best guess - check it if a game doesn't trigger.":
        "Hula lang ang pangalan ng programa - suriin ito kung hindi gumana ang isang laro.",
    "Select all": "Piliin lahat", "Add selected": "Idagdag ang napili", "Close": "Isara",
    # tools
    "Drive to inspect": "Drive na susuriin", "Refresh": "I-refresh", "Restart as administrator": "I-restart bilang administrator", "Reading drive info...": "Binabasa ang impormasyon ng drive...",
    "What Windows knows about this drive, with plain-language advice.":
        "Ang alam ng Windows tungkol sa drive na ito, kasama ang simpleng payo.",
    "Health": "Kalusugan", "Temperature": "Temperatura", "Wear": "Pagkasira", "Powered on": "Oras na bukas",
    "n/a": "wala", "{free} GB free of {total} GB": "{free} GB ang libre sa {total} GB",
    "Measures how long the first read takes after the drive has been idle, with and without keep-alive, then picks the lightest setting that helps. Takes about 2 minutes. Don't run a game meanwhile.":
        "Sinusukat kung gaano katagal ang unang pagbasa pagkatapos magpahinga ng drive, mayroon at walang keep-alive, saka pipiliin ang pinakamagaan na setting na nakakatulong. Tumatagal ng mga 2 minuto. Huwag munang maglaro habang tumatakbo ito.",
    "Run auto-tune": "Patakbuhin ang auto-tune", "Preparing…": "Naghahanda…", "Cancel": "Kanselahin",
    "Cancelled.": "Nakansela.", "Test failed": "Pumalya ang pagsusuri", "Keep-alive": "Keep-alive",
    "avg ms": "avg ms", "p95 ms": "p95 ms", "max ms": "max ms", "None": "Wala",
    "Keep-alive removes the idle stalls. Recommended setting: {p}.":
        "Inaalis ng keep-alive ang mga pagtigil kapag idle. Inirerekomendang setting: {p}.",
    "No idle stalls detected on this drive - it wakes up fast. Keep-alive probably won't help here.":
        "Walang nakitang pagtigil sa drive na ito - mabilis itong magising. Malamang hindi makakatulong ang keep-alive dito.",
    "This drive hesitates after idling, but keep-alive didn't clearly help. The cause may be elsewhere - try the Lag check.":
        "Nag-aatubili ang drive na ito pagkatapos mag-idle, pero hindi malinaw na nakatulong ang keep-alive. Maaaring nasa iba ang sanhi - subukan ang Pagsusuri ng lag.",
    "Use {p} as default": "Gamitin ang {p} bilang default", "Saved.": "Na-save.",
    "Switch to your game right after pressing Start. After 10 seconds Diskuick watches your real disk, CPU and memory for 30 seconds and tells you what looks wrong.":
        "Lumipat sa laro mo pagkatapos pindutin ang Start. Pagkalipas ng 10 segundo, babantayan ng Diskuick ang totoong disk, CPU at memory mo sa loob ng 30 segundo at sasabihin kung ano ang mukhang may problema.",
    "Start lag check": "Simulan ang pagsusuri ng lag",
    "Starting in {s}s - switch to your game now…": "Magsisimula sa {s}s - lumipat na sa laro mo…",
    "Measuring… keep playing": "Sumusukat… ituloy ang paglalaro",
    "Indicative only - network isn't measured.": "Pahiwatig lang - hindi nasusukat ang network.",
    # settings
    "Only while gaming": "Habang naglalaro lang", "Always on": "Laging naka-on",
    "Starts automatically when one of your games opens and stops when it closes. Add games in the Games tab.":
        "Awtomatikong nagsisimula kapag may nabuksang laro at humihinto kapag isinara ito. Magdagdag ng laro sa tab na Mga Laro.",
    "Runs the whole time Diskuick is open. Simple, but keeps the drive busy even when idle.":
        "Tumatakbo habang bukas ang Diskuick. Simple, pero laging may ginagawa ang drive kahit idle.",
    "Drives to keep awake": "Mga drive na papanatilihing gising",
    "How hard to nudge the drive. Games can override this.": "Gaano kalakas gigisingin ang drive. Maaaring baguhin ito ng bawat laro.",
    "Light": "Magaan", "Balanced": "Katamtaman", "Heavy": "Mabigat",
    "Tiny random reads, about 10 per second. Least overhead - try this first.":
        "Maliliit na random na pagbasa, mga 10 kada segundo. Pinakamagaan - subukan ito muna.",
    "Light sequential reads, about 20 per second. For drives that need a bit more.":
        "Magagaan na sunud-sunod na pagbasa, mga 20 kada segundo. Para sa mga drive na kailangan ng kaunti pa.",
    "Non-stop reads, like HD Tune. Strongest effect, but the drive is always busy.":
        "Tuloy-tuloy na pagbasa, tulad ng HD Tune. Pinakamalakas ang epekto, pero laging abala ang drive.",
    "Seconds between reads (advanced)": "Segundo sa pagitan ng pagbasa (advanced)", "default": "default",
    "Enter a positive number, or leave empty for the default.": "Maglagay ng positibong numero, o iwanang blangko para sa default.",
    "Pause on battery": "I-pause kapag naka-baterya", "Laptops: don't keep the drive busy when unplugged.":
        "Para sa laptop: huwag panatilihing abala ang drive kapag hindi nakasaksak.",
    "Only while the game is focused": "Kapag nasa harapan lang ang laro",
    "Pauses when you alt-tab away from the game.": "Napo-pause kapag nag-alt-tab ka palayo sa laro.",
    "Notify when a game starts": "Magpaalam kapag nagsimula ang laro", "A small tray notification.": "Maliit na abiso sa tray.",
    "Start with Windows": "Magsimula kasabay ng Windows", "Runs quietly in the tray at login.": "Tahimik na tumatakbo sa tray pag-login.",
    "Theme": "Tema", "System": "Sistema", "Dark": "Madilim", "Light theme": "Maliwanag", "Language": "Wika",
    "Check for updates": "Tingnan kung may update",
    "Only the repository name is contacted; nothing about you is sent.":
        "Pangalan lang ng repository ang kinokontak; walang ipinapadalang impormasyon tungkol sa iyo.",
    "Update checks are off until a release repository is set.": "Naka-off ang pagtingin ng update hanggang may nakatakdang release repository.",
    "Open data folder": "Buksan ang folder ng datos", "Open stall log": "Buksan ang log ng pagtigil",
    # overlay
    "Latency overlay": "Overlay ng latency",
    "A small live readout in a screen corner while the drive is being kept awake (a game is running, or Always on). It's a separate window that never touches the game, and shows over windowed and borderless games (not exclusive fullscreen).":
        "Maliit na live na pagbasa sa sulok ng screen habang pinapanatiling gising ang drive (may tumatakbong laro, o naka-Always on). Hiwalay itong window na hindi ginagalaw ang laro, at lumalabas sa windowed at borderless na laro (hindi sa exclusive fullscreen).",
    "Show overlay while a game runs": "Ipakita ang overlay habang may laro", "Position": "Posisyon", "Preview": "Pasilip",
    "Top left": "Kaliwang itaas", "Top right": "Kanang itaas", "Bottom left": "Kaliwang ibaba", "Bottom right": "Kanang ibaba",
    # updates
    "Update now": "I-update na", "Downloading… {p}%": "Dina-download… {p}%", "Update failed": "Pumalya ang update",
    "Retry": "Subukan muli", "Check now": "Tingnan ngayon", "Checking…": "Tinitingnan…",
    "You're up to date.": "Napapanahon na ang bersyon mo.", "Couldn't check for updates.": "Hindi nakapag-check ng update.",
    "Update available: {v}": "May bagong bersyon: {v}",
    # tray
    "Open Diskuick": "Buksan ang Diskuick", "Quit": "Isara", "Keeping drive {d}: awake": "Pinapanatiling gising ang drive {d}:",
    "Could not change startup setting": "Hindi mabago ang setting ng pagsisimula",
    # 1.3 features (best-effort)
    "Last sessions": "Mga huling session",
    "Was it the drive? A summary of your last play sessions.":
        "Drive ba ang may sala? Buod ng mga huli mong session ng paglalaro.",
    "No sessions recorded yet. A report appears when a game closes.":
        "Wala pang naitalang session. May lalabas na ulat kapag nagsara ang laro.",
    "Worst read": "Pinakamabagal na read", "stalls": "pagtigil", "peak": "pinakamataas", "ping": "ping",
    "Lag marks": "Mga markang lag",
    "Press Ctrl+Alt+L (or use the tray menu) the moment a game lags. Diskuick saves what the PC was doing right then.":
        "Pindutin ang Ctrl+Alt+L (o gamitin ang tray menu) sa mismong oras na nag-lag ang laro. "
        "Sine-save ng Diskuick ang ginagawa ng PC sa sandaling iyon.",
    "No lag marked yet.": "Wala pang namarkahang lag.",
    "Mark lag now": "Markahan ang lag ngayon", "Lag marked": "Namarkahan ang lag",
    "Session ended": "Natapos ang session", "Closed to free resources": "Isinara para magkaroon ng espasyo",
    "Smart intensity": "Matalinong lakas",
    "Starts Light and steps up only while the drive keeps stalling, then steps back down when it's calm. "
    "Ignores the choice above (a game's own setting still wins).":
        "Nagsisimula sa Light at tumataas lang habang patuloy na tumitigil ang drive, saka bumababa kapag "
        "kalmado na. Hindi pinapansin ang pinili sa itaas (mas mataas pa rin ang setting ng mismong laro).",
    "Drive alerts": "Mga babala sa drive",
    "Tell me when the game drive is nearly full or no longer healthy.":
        "Sabihan ako kapag halos puno na ang drive ng laro o hindi na malusog.",
    "Keyboard shortcuts": "Mga shortcut sa keyboard",
    "Ctrl+Alt+L marks a lag moment. Ctrl+Alt+O shows or hides the overlay.":
        "Minamarkahan ng Ctrl+Alt+L ang sandali ng lag. Ipinapakita o itinatago ng Ctrl+Alt+O ang overlay.",
    "Show overlay while the drive is kept awake": "Ipakita ang overlay habang gising ang drive",
    "Also show CPU and GPU load": "Ipakita rin ang load ng CPU at GPU",
    "Also show FPS": "Ipakita rin ang FPS",
    "Needs PresentMon.exe next to Diskuick.exe and Diskuick running as administrator.":
        "Kailangan ng PresentMon.exe sa tabi ng Diskuick.exe at ng Diskuick na tumatakbo bilang administrator.",
    "Network check (optional)": "Pagsusuri ng network (opsyonal)",
    "Adds ping and packet loss to the Lag check and lag marks. Type a server you play on, or any host such as "
    "1.1.1.1. Diskuick only opens a normal connection to it, a few times a second during a check. Leave empty "
    "to keep it off.":
        "Nagdaragdag ng ping at packet loss sa Lag check at mga markang lag. Mag-type ng server na nilalaro mo, "
        "o anumang host tulad ng 1.1.1.1. Normal na koneksyon lang ang binubuksan ng Diskuick, ilang beses "
        "bawat segundo habang may pagsusuri. Iwanang walang laman para patayin.",
    "Host": "Host",
    "Enter a host name or address, optionally with :port.":
        "Maglagay ng pangalan o address ng host, maaaring may :port.",
    "Game mode (optional)": "Game mode (opsyonal)",
    "When one of your games starts, politely ask these programs to close (they can still ask you to save), and "
    "reopen them when the game ends. Nothing is force-closed.":
        "Kapag nagsimula ang isa sa mga laro mo, magalang na hihilingin sa mga programang ito na magsara "
        "(maaari pa rin silang magtanong kung ise-save), at bubuksan muli pagkatapos ng laro. "
        "Walang pwersahang isinasara.",
    "No programs chosen.": "Walang napiling programa.", "Remove": "Alisin",
    "That program is protected and can't be closed.": "Protektado ang programang iyon at hindi maisasara.",
    "Reopen them afterwards": "Buksan muli pagkatapos",
})
