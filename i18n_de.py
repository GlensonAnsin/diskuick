"""German strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("de", "Deutsch", (
    "Übersicht", "Spiele", "Werkzeuge", "Einstellungen",                                               # 1-5
    "Hält dein Laufwerk beim Spielen wach",
    "Letzte Aussetzer", "Laufwerkszustand", "Lag-Check", "Benchmark & Auto-Tuning",
    "Verhalten", "Darstellung", "Wann ausführen", "Standardintensität",                                # 10-14
    "Live-Leselatenz",
    "Aktiv", "Wartet", "Aus", "Fehler", "Deaktiviert", "Leerlauf", "Startet",                          # 16-22
    "Im Akkubetrieb pausiert",
    "Wähle ein Laufwerk in den Einstellungen", "Füge Spiele im Tab „Spiele“ hinzu",
    "Warte auf den Start eines Spiels", "Warte, bis das Spielfenster im Fokus ist",
    "Wachgehalten", "Sitzungen", "Protokollierte Aussetzer", "Aktiviert",                              # 28-31
    "Noch keine Aussetzer aufgezeichnet.",
    "Jeder Punkt ist die langsamste Lesung in dieser Sekunde. Spitzen über der roten Linie sind Aussetzer – Momente, in denen das Laufwerk gezögert hat.",
    "Starte ein Spiel (oder wähle „Immer an“), um die Live-Latenz zu sehen.",
    "Warte auf Daten...",
    "Aussetzer", "jetzt", "Update verfügbar", "Herunterladen",                                         # 36-39
    "Installierte Spiele erkennen", "Suche...", "Laufendes Programm hinzufügen…",
    "oder Programmnamen eingeben, z. B. spiel.exe",
    "Hinzufügen", "Laufwerk", "Intensität", "Standard",                                                # 44-47
    "Noch keine Spiele.\nKlicke auf „Installierte Spiele erkennen“, um sie automatisch zu finden.",
    "Laufendes Programm auswählen", "Öffne zuerst dein Spiel und wähle es dann hier aus.",
    "Suchen...", "Nichts gefunden", "Erkannte Spiele", "Keine neuen Spiele gefunden.",                 # 51-54
    "Gesucht wurde in Steam, Epic Games und GOG. Du kannst ein Spiel trotzdem über „Laufendes Programm hinzufügen“ oder durch Eingabe seines Exe-Namens hinzufügen.",
    "Wähle die Spiele, für die dein Laufwerk wach gehalten werden soll.",
    "Der Programmname ist eine Schätzung – prüfe ihn, wenn ein Spiel nicht auslöst.",
    "Alle auswählen", "Auswahl hinzufügen", "Schließen",                                               # 58-60
    "Zu prüfendes Laufwerk", "Aktualisieren", "Als Administrator neu starten", "Laufwerksinfos werden gelesen...",
    "Was Windows über dieses Laufwerk weiß, mit Hinweisen in einfacher Sprache.",
    "Zustand", "Temperatur", "Verschleiß", "Betriebsstunden", "k. A.",                                 # 66-70
    "{free} GB frei von {total} GB",
    "Misst, wie lange die erste Lesung nach Leerlauf des Laufwerks dauert – mit und ohne Wachhalten – und wählt dann die leichteste hilfreiche Einstellung. Dauert etwa 2 Minuten. Starte währenddessen kein Spiel.",
    "Auto-Tuning starten", "Vorbereitung…", "Abbrechen", "Abgebrochen.", "Test fehlgeschlagen",       # 73-77
    "Wachhalten", "Ø ms", "p95 ms", "max. ms", "Keine",                                                # 78-82
    "Wachhalten beseitigt die Leerlauf-Aussetzer. Empfohlene Einstellung: {p}.",
    "Auf diesem Laufwerk wurden keine Leerlauf-Aussetzer festgestellt – es wacht schnell auf. Wachhalten hilft hier wahrscheinlich nicht.",
    "Dieses Laufwerk zögert nach Leerlauf, aber Wachhalten hat nicht eindeutig geholfen. Die Ursache liegt vielleicht woanders – probiere den Lag-Check.",
    "{p} als Standard verwenden", "Gespeichert.",                                                      # 86-87
    "Wechsle direkt nach dem Klick auf Start zu deinem Spiel. Nach 10 Sekunden beobachtet Diskuick 30 Sekunden lang dein echtes Laufwerk, deine CPU und deinen Arbeitsspeicher und sagt dir, was auffällig ist.",
    "Lag-Check starten", "Start in {s} s – wechsle jetzt zu deinem Spiel…", "Messung läuft… spiele weiter",
    "Nur ein Anhaltspunkt – das Netzwerk wird nicht gemessen.",
    "Nur beim Spielen", "Immer an",                                                                    # 93-94
    "Startet automatisch, wenn eines deiner Spiele geöffnet wird, und stoppt, wenn es geschlossen wird. Füge Spiele im Tab „Spiele“ hinzu.",
    "Läuft die ganze Zeit, solange Diskuick geöffnet ist. Einfach, hält das Laufwerk aber auch im Leerlauf beschäftigt.",
    "Wachzuhaltende Laufwerke",
    "Wie stark das Laufwerk angestoßen wird. Spiele können das überschreiben.",
    "Leicht", "Ausgewogen", "Stark",                                                                   # 99-101
    "Winzige zufällige Lesezugriffe, etwa 10 pro Sekunde. Geringster Aufwand – probiere das zuerst.",
    "Leichte sequenzielle Lesezugriffe, etwa 20 pro Sekunde. Für Laufwerke, die etwas mehr brauchen.",
    "Dauerhafte Lesezugriffe. Stärkste Wirkung, aber das Laufwerk ist ständig beschäftigt.",
    "Sekunden zwischen Lesezugriffen (erweitert)", "Standard",                                         # 105-106
    "Gib eine positive Zahl ein oder lass das Feld für den Standardwert leer.",
    "Im Akkubetrieb pausieren", "Laptops: Laufwerk nicht beschäftigen, wenn der Netzstecker gezogen ist.",
    "Nur wenn das Spiel im Fokus ist", "Pausiert, wenn du mit Alt+Tab das Spiel verlässt.",
    "Benachrichtigen, wenn ein Spiel startet", "Eine kleine Benachrichtigung im Infobereich.",
    "Mit Windows starten", "Läuft bei der Anmeldung unauffällig im Infobereich.",
    "Design", "System", "Dunkel", "Helles Design", "Sprache",                                          # 116-120
    "Nach Updates suchen",
    "Es wird nur der Repository-Name kontaktiert; nichts über dich wird gesendet.",
    "Die Update-Suche ist aus, bis ein Release-Repository festgelegt ist.",
    "Datenordner öffnen", "Aussetzer-Protokoll öffnen",
    "Smarte Intensität ist an: Sie wählt die Stufe für dich. Schalte sie aus, um selbst eine zu wählen.",
    "Smart",                                                                                           # 127
    "Als Administrator neu starten für einen schnellen Scan",
    "Zeigt, was Speicherplatz belegt, das Größte zuerst. Hier wird nichts geändert oder gelöscht. Als Administrator liest es die Dateitabelle des Laufwerks direkt (wie WizTree) und braucht nur Sekunden; sonst liest es Ordner einzeln, was ein bis zwei Minuten dauern kann.",
    "Dauer: {s} s.", "Spiel umbenennen", "Anzuzeigender Name für",                                    # 130-132
    "Latenz-Overlay",
    "Eine kleine Live-Anzeige in einer Bildschirmecke, solange das Laufwerk wachgehalten wird (ein Spiel läuft oder „Immer an“). Es ist ein separates Fenster, das das Spiel nie berührt, und erscheint über Fenster- und rahmenlosen Spielen. Über exklusivem Vollbild (z. B. Battlefield 3) kann es nicht erscheinen: Stelle das Spiel auf rahmenlos oder Fenster um.",
    "Overlay anzeigen, solange ein Spiel läuft", "Position", "Vorschau",                               # 135-137
    "Oben links", "Oben rechts", "Unten links", "Unten rechts",
    "Jetzt aktualisieren", "Wird heruntergeladen… {p} %", "Update fehlgeschlagen", "Erneut versuchen", "Jetzt prüfen", # 142-146
    "Prüfe…", "Du bist auf dem neuesten Stand.", "Update-Suche fehlgeschlagen.", "Update verfügbar: {v}",
    "Diskuick öffnen", "Beenden", "Laufwerk {d}: wird wachgehalten",                                   # 151-153
    "Autostart-Einstellung konnte nicht geändert werden",
    "Letzte Sitzungen", "Lag es am Laufwerk? Eine Zusammenfassung deiner letzten Spielsitzungen.",
    "Noch keine Sitzungen aufgezeichnet. Ein Bericht erscheint, wenn ein Spiel geschlossen wird.",
    "Schlechteste Lesung", "Aussetzer", "Spitze", "Ping",                                              # 158-161
    "Lag-Markierungen",
    "Drücke Strg+Alt+L (oder nutze das Infobereichmenü), sobald ein Spiel laggt. Diskuick speichert, was der PC in diesem Moment getan hat.",
    "Noch kein Lag markiert.", "Lag jetzt markieren", "Lag markiert", "Sitzung beendet",               # 162-167
    "Zur Ressourcenfreigabe geschlossen", "Smarte Intensität",
    "Beginnt mit Leicht und steigert nur, solange das Laufwerk weiter aussetzt, und geht zurück, wenn es ruhig ist. Ignoriert die Auswahl oben (die eigene Einstellung eines Spiels hat weiterhin Vorrang).",
    "Laufwerkswarnungen", "Sag mir Bescheid, wenn das Spiele-Laufwerk fast voll oder nicht mehr gesund ist.", # 171-172
    "Tastenkürzel",
    "Strg+Alt+L markiert einen Lag-Moment. Strg+Alt+O blendet das Overlay ein oder aus.",
    "Overlay anzeigen, solange das Laufwerk wachgehalten wird",
    "Zusätzlich CPU- und GPU-Last anzeigen", "Zusätzlich FPS anzeigen",                                # 176-177
    "Benötigt PresentMon.exe neben Diskuick.exe und Diskuick als Administrator.",
    "Netzwerkprüfung (optional)",
    "Prüft, ob dein Internet hinter dem Lag stecken könnte. Gib 1.1.1.1 ein, um deine allgemeine Verbindung zu prüfen, oder die Adresse eines Servers, auf dem du spielst (der :Port ist optional und standardmäßig 443). Während eines Lag-Checks (und wenn du einen Lag markierst) misst Diskuick Ping (wie lange der Server zur Antwort braucht) und Paketverlust (Antworten, die nie ankommen), damit du ein Netzwerkproblem von einem Laufwerksproblem unterscheiden kannst. Es wird nur eine normale Verbindung geöffnet, ein paar Mal pro Sekunde, und nichts über dich wird gesendet. Leer lassen, um es auszuschalten.",
    "Host", "Gib einen Hostnamen oder eine Adresse ein, optional mit :Port.",
    "Spielmodus (optional)",
    "Wenn eines deiner Spiele startet, werden diese Programme höflich zum Beenden aufgefordert (sie können dich noch zum Speichern auffordern) und nach dem Spiel wieder geöffnet. Nichts wird erzwungen geschlossen.",
    "Keine Programme gewählt.", "Entfernen", "Dieses Programm ist geschützt und kann nicht geschlossen werden.", # 185-187
    "Danach wieder öffnen", "Datenträger", "Zu analysierendes Laufwerk", "Scannen", "Stopp", "Wird gestoppt...", "Hoch", # 188-194
    "Name", "Größe", "Dateien", "% des Übergeordneten", "Im Explorer öffnen", "Diesen Ordner hier öffnen", # 195-200
    "Speicherplatz-Analyse",
    "Zeigt, was Speicherplatz belegt, das Größte zuerst. Es liest Ordner einzeln, daher dauert ein großes Laufwerk ein bis zwei Minuten. Hier wird nichts geändert oder gelöscht.",
    "Drücke Scannen zum Starten.", "Scanne ein Laufwerk, um hier seine Karte zu sehen.",               # 203-204
    "{drive}: wird gescannt ...", "{drive}: wird gescannt: bisher {files} Dateien, {size}",
    "{size} in {files} Dateien und {folders} Ordnern gefunden.", "Laufwerk belegt: {used}.",
    "Vorzeitig gestoppt, daher unvollständig.",
    "Einige Ordner sind geschützt; als Administrator ausführen, um sie einzubeziehen.",
    "Dateitypen", "Welche Dateitypen auf diesem Laufwerk am meisten Platz belegen.",                   # 211-212
    "Datenträgerbereinigung",
    "Entfernt nur sichere, wiederherstellbare Überreste: temporäre Dateien, Caches und Absturzberichte. Deine eigenen Dateien bleiben unberührt. Hake an, was du möchtest, prüfe die Größen und bereinige dann.",
    "Größen prüfen", "Größen werden geprüft...", "Auswahl bereinigen", "Wird bereinigt...",            # 215-218
    "Hake zuerst mindestens einen Eintrag an.", "Die angehakten Einträge würden etwa {size} freigeben.",
    "Der Papierkorb wird endgültig geleert.",
    "Etwa {size} entfernen aus:\n\n{names}{note}\n\nFortfahren?",
    "{size} freigegeben ({files} Dateien). Verwendete Elemente wurden übersprungen.",
    "Temporäre Dateien", "Von Programmen in deinem Temp-Ordner hinterlassen.",                        # 224-225
    "Temporäre Windows-Dateien", "Der eigene Temp-Ordner von Windows. Als Administrator ausführen, um alles zu leeren.",
    "Miniaturansicht-Cache", "Der Explorer erstellt die Bildvorschauen bei Bedarf neu.",
    "Absturzabbilder und Fehlerberichte", "Diagnosedateien von abgestürzten Programmen.",
    "Browser-Caches", "Caches von Chrome, Edge und Brave. Seiten laden einmal etwas langsamer.",
    "Shader-Caches", "GPU-Shader-Caches. Spiele können beim nächsten Start kurz ruckeln, während diese neu aufgebaut werden.",
    "Papierkorb", "Löscht den Inhalt des Papierkorbs endgültig.",
    "In den Papierkorb verschieben", "Ordner", "Datei",                                                # 238-240
    "Diese(n) {kind} in den Papierkorb verschieben?\n\n{path}\n{size}\n\nDu kannst es aus dem Papierkorb wiederherstellen.",
    "Wird in den Papierkorb verschoben...",
    "Konnte nicht in den Papierkorb verschoben werden (in Verwendung, geschützt oder abgebrochen).",
    "{size} in den Papierkorb verschoben. Scanne erneut, um die Dateitypen zu aktualisieren.",
    "Schneller Scan (NTFS-Dateitabelle).",
    "Führe Diskuick als Administrator aus für einen viel schnelleren Scan.",
    "Ordner", "Frei",                                                                           # 246-247
    "z. B. 1.1.1.1",
))
