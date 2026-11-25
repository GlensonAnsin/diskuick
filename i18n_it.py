"""Italian strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("it", "Italiano", (
    "Pannello", "Giochi", "Strumenti", "Impostazioni",                                                 # 1-5
    "Mantiene attivo il tuo disco mentre giochi",
    "Blocchi recenti", "Salute del disco", "Test del lag", "Benchmark e regolazione automatica",
    "Comportamento", "Aspetto", "Quando eseguire", "Intensità predefinita",                            # 10-14
    "Latenza di lettura in tempo reale",
    "Attivo", "In attesa", "Spento", "Errore", "Disattivato", "Inattivo", "Avvio",                     # 16-22
    "In pausa con la batteria",
    "Scegli un disco in Impostazioni", "Aggiungi giochi nella scheda Giochi",
    "In attesa dell'avvio di un gioco", "In attesa che la finestra del gioco sia in primo piano",
    "Mantenuto attivo", "Sessioni", "Blocchi registrati", "Abilitato",                                 # 28-31
    "Nessun blocco registrato finora.",
    "Ogni punto è la lettura più lenta di quel secondo. I picchi sopra la linea rossa sono blocchi: momenti in cui il disco ha esitato.",
    "Avvia un gioco (o scegli «Sempre attivo») per vedere la latenza in tempo reale.",
    "In attesa di dati...",
    "blocco", "ora", "Aggiornamento disponibile", "Scarica",                                           # 36-39
    "Rileva giochi installati", "Scansione...", "Aggiungi programma in esecuzione…",
    "oppure digita il nome di un programma, es. gioco.exe",
    "Aggiungi", "Disco", "Intensità", "Predefinita",                                                   # 44-47
    "Ancora nessun gioco.\nFai clic su «Rileva giochi installati» per trovarli automaticamente.",
    "Scegli un programma in esecuzione", "Apri prima il tuo gioco, poi sceglilo qui.",
    "Cerca...", "Nessun risultato", "Giochi rilevati", "Nessun nuovo gioco trovato.",                  # 51-54
    "Ho cercato in Steam, Epic Games e GOG. Puoi comunque aggiungere un gioco con «Aggiungi programma in esecuzione» o digitando il nome del suo exe.",
    "Scegli i giochi per cui mantenere attivo il disco.",
    "Il nome del programma è una stima: controllalo se un gioco non si attiva.",
    "Seleziona tutto", "Aggiungi selezionati", "Chiudi",                                               # 58-60
    "Disco da ispezionare", "Aggiorna", "Riavvia come amministratore", "Lettura delle info del disco...",
    "Cosa sa Windows di questo disco, con consigli in linguaggio semplice.",
    "Salute", "Temperatura", "Usura", "Ore di accensione", "n/d",                                      # 66-70
    "{free} GB liberi su {total} GB",
    "Misura quanto dura la prima lettura dopo che il disco è rimasto inattivo, con e senza mantenimento attivo, poi sceglie l'impostazione più leggera che aiuta. Richiede circa 2 minuti. Non avviare un gioco nel frattempo.",
    "Avvia regolazione automatica", "Preparazione…", "Annulla", "Annullato.", "Test non riuscito",    # 73-77
    "Mantenimento attivo", "ms medi", "ms p95", "ms max", "Nessuno",                                   # 78-82
    "Il mantenimento attivo elimina i blocchi da inattività. Impostazione consigliata: {p}.",
    "Nessun blocco da inattività rilevato su questo disco: si sveglia in fretta. Il mantenimento attivo probabilmente qui non aiuterà.",
    "Questo disco esita dopo l'inattività, ma il mantenimento attivo non ha aiutato chiaramente. La causa potrebbe essere altrove: prova il Test del lag.",
    "Usa {p} come predefinita", "Salvato.",                                                            # 86-87
    "Passa al tuo gioco subito dopo aver premuto Avvia. Dopo 10 secondi Diskuick osserva per 30 secondi il tuo disco, la CPU e la memoria reali e ti dice cosa sembra non andare.",
    "Avvia test del lag", "Inizio tra {s} s: passa al tuo gioco adesso…", "Misurazione in corso… continua a giocare",
    "Solo indicativo: la rete non viene misurata.",
    "Solo durante il gioco", "Sempre attivo",                                                          # 93-94
    "Parte automaticamente quando si apre uno dei tuoi giochi e si ferma quando si chiude. Aggiungi giochi nella scheda Giochi.",
    "Funziona per tutto il tempo in cui Diskuick è aperto. Semplice, ma tiene il disco occupato anche a riposo.",
    "Dischi da mantenere attivi",
    "Quanto stimolare il disco. I giochi possono sostituirla.",
    "Leggera", "Bilanciata", "Pesante",                                                                # 99-101
    "Minuscole letture casuali, circa 10 al secondo. Carico minimo: prova prima questa.",
    "Letture sequenziali leggere, circa 20 al secondo. Per dischi che richiedono qualcosa in più.",
    "Letture continue. Effetto più forte, ma il disco è sempre occupato.",
    "Secondi tra le letture (avanzato)", "predefinito",                                                # 105-106
    "Inserisci un numero positivo, oppure lascia vuoto per il valore predefinito.",
    "Pausa con la batteria", "Portatili: non tenere occupato il disco quando è scollegato.",
    "Solo con il gioco in primo piano", "Va in pausa quando esci dal gioco con Alt+Tab.",
    "Avvisa all'avvio di un gioco", "Una piccola notifica nell'area di notifica.",
    "Avvia con Windows", "Funziona in silenzio nell'area di notifica all'accesso.",
    "Tema", "Sistema", "Scuro", "Tema chiaro", "Lingua",                                               # 116-120
    "Controlla aggiornamenti",
    "Viene contattato solo il nome del repository; non viene inviato nulla su di te.",
    "Il controllo aggiornamenti è disattivato finché non viene impostato un repository delle versioni.",
    "Apri cartella dati", "Apri registro dei blocchi",
    "L'intensità intelligente è attiva: sceglie lei il livello. Disattivala per sceglierlo tu.",
    "Intelligente",                                                                                    # 127
    "Riavvia come amministratore per una scansione veloce",
    "Mostra cosa occupa spazio, dal più grande. Qui non si modifica né si elimina nulla. Come amministratore legge direttamente la tabella dei file del disco (come WizTree) in pochi secondi; altrimenti legge le cartelle una per una, il che può richiedere uno o due minuti.",
    "Ci sono voluti {s} s.", "Rinomina gioco", "Nome da mostrare per",                                 # 130-132
    "Overlay di latenza",
    "Una piccola lettura in tempo reale in un angolo dello schermo mentre il disco viene mantenuto attivo (un gioco è in esecuzione, o Sempre attivo). È una finestra separata che non tocca mai il gioco e si vede sopra i giochi in finestra e senza bordi. Non può apparire sopra lo schermo intero esclusivo (ad esempio Battlefield 3): passa quel gioco a senza bordi o in finestra.",
    "Mostra overlay mentre un gioco è in esecuzione", "Posizione", "Anteprima",                        # 135-137
    "In alto a sinistra", "In alto a destra", "In basso a sinistra", "In basso a destra",
    "Aggiorna ora", "Download in corso… {p}%", "Aggiornamento non riuscito", "Riprova", "Controlla ora", # 142-146
    "Controllo…", "Sei aggiornato.", "Impossibile controllare gli aggiornamenti.", "Aggiornamento disponibile: {v}",
    "Apri Diskuick", "Esci", "Mantengo attivo il disco {d}:",                                          # 151-153
    "Impossibile modificare l'avvio automatico",
    "Ultime sessioni", "Era il disco? Un riepilogo delle tue ultime sessioni di gioco.",
    "Nessuna sessione registrata. Un rapporto appare quando un gioco si chiude.",
    "Lettura peggiore", "blocchi", "picco", "ping",                                                    # 158-161
    "Segni di lag",
    "Premi Ctrl+Alt+L (o usa il menu dell'area di notifica) nel momento in cui un gioco laga. Diskuick salva cosa stava facendo il PC in quell'istante.",
    "Nessun lag segnato.", "Segna lag ora", "Lag segnato", "Sessione terminata",                       # 162-167
    "Chiuso per liberare risorse", "Intensità intelligente",
    "Parte da Leggera e sale solo finché il disco continua a bloccarsi, poi scende quando è tranquillo. Ignora la scelta qui sopra (l'impostazione propria di un gioco vince comunque).",
    "Avvisi del disco", "Avvisami quando il disco dei giochi è quasi pieno o non è più in salute.",   # 171-172
    "Scorciatoie da tastiera",
    "Ctrl+Alt+L segna un momento di lag. Ctrl+Alt+O mostra o nasconde l'overlay.",
    "Mostra overlay mentre il disco è mantenuto attivo",
    "Mostra anche il carico di CPU e GPU", "Mostra anche gli FPS",                                     # 176-177
    "Richiede PresentMon.exe accanto a Diskuick.exe e Diskuick eseguito come amministratore.",
    "Controllo di rete (facoltativo)",
    "Verifica se la tua connessione a internet può essere la causa del lag. Digita 1.1.1.1 per controllare la tua connessione generale, o l'indirizzo di un server su cui giochi (la :porta è facoltativa e di default è 443). Durante un Test del lag (e quando segni un lag) Diskuick misura il ping (quanto ci mette il server a rispondere) e la perdita di pacchetti (risposte che non arrivano mai), così puoi distinguere un problema di rete da uno del disco. Viene aperta solo una normale connessione, poche volte al secondo, e non viene inviato nulla su di te. Lascia vuoto per tenerlo disattivato.",
    "Host", "Inserisci un nome host o un indirizzo, facoltativamente con :porta.",
    "Modalità gioco (facoltativo)",
    "Quando parte uno dei tuoi giochi, chiede gentilmente a questi programmi di chiudersi (possono comunque chiederti di salvare) e li riapre quando il gioco finisce. Nulla viene chiuso con la forza.",
    "Nessun programma scelto.", "Rimuovi", "Quel programma è protetto e non può essere chiuso.",        # 185-187
    "Riaprili dopo", "Disco", "Disco da analizzare", "Scansiona", "Ferma", "Arresto...", "Su",          # 188-194
    "Nome", "Dimensione", "File", "% del genitore", "Apri in Esplora risorse", "Apri questa cartella qui", # 195-200
    "Analizzatore dello spazio su disco",
    "Mostra cosa occupa spazio, dal più grande. Legge le cartelle una per una, quindi un disco grande richiede uno o due minuti. Qui non si modifica né si elimina nulla.",
    "Premi Scansiona per iniziare.", "Scansiona un disco per vederne la mappa qui.",                   # 203-204
    "Scansione di {drive}: ...", "Scansione di {drive}: {files} file, {size} finora",
    "Trovati {size} in {files} file e {folders} cartelle.", "Disco usato: {used}.",
    "Interrotto prima della fine, quindi il risultato è parziale.",
    "Alcune cartelle sono protette; esegui come amministratore per includerle.",
    "Tipi di file", "Quali tipi di file occupano più spazio su questo disco.",                        # 211-212
    "Pulizia del disco",
    "Rimuove solo avanzi sicuri e rigenerabili: file temporanei, cache e rapporti di arresto anomalo. I tuoi file non vengono mai toccati. Spunta ciò che vuoi, controlla le dimensioni, poi pulisci.",
    "Controlla dimensioni", "Controllo delle dimensioni...", "Pulisci selezionati", "Pulizia...",       # 215-218
    "Spunta prima almeno un elemento.", "Gli elementi spuntati libererebbero circa {size}.",
    "Il Cestino viene svuotato in modo permanente.",
    "Rimuovere circa {size} da:\n\n{names}{note}\n\nContinuare?",
    "Liberati {size} ({files} file). Gli elementi in uso sono stati saltati.",
    "File temporanei", "Lasciati dai programmi nella tua cartella Temp.",                             # 224-225
    "File temporanei di Windows", "La cartella Temp di Windows. Esegui come amministratore per svuotarla tutta.",
    "Cache delle miniature", "Esplora risorse ricrea le anteprime delle immagini quando serve.",
    "Dump di arresto anomalo e rapporti di errore", "File diagnostici di programmi andati in crash.",
    "Cache dei browser", "Cache di Chrome, Edge e Brave. I siti si caricano un po' più lentamente una volta.",
    "Cache degli shader", "Cache degli shader della GPU. I giochi possono scattare brevemente al prossimo avvio mentre vengono ricostruite.",
    "Cestino", "Elimina in modo permanente ciò che si trova nel Cestino.",
    "Sposta nel Cestino", "cartella", "file",                                                          # 238-240
    "Spostare questo {kind} nel Cestino?\n\n{path}\n{size}\n\nPuoi ripristinarlo dal Cestino.",
    "Spostamento nel Cestino...",
    "Impossibile spostare nel Cestino (in uso, protetto o annullato).",
    "{size} spostati nel Cestino. Scansiona di nuovo per aggiornare i tipi di file.",
    "Scansione veloce (tabella dei file NTFS).",
    "Esegui Diskuick come amministratore per una scansione molto più veloce.",
    "Cartelle", "Libero",                                                                           # 246-247
    "es. 1.1.1.1",
))
