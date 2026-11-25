"""French strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("fr", "Français", (
    "Tableau de bord", "Jeux", "Outils", "Paramètres",                                                 # 1-5
    "Garde votre disque éveillé pendant que vous jouez",
    "Blocages récents", "État du disque", "Test de lag", "Benchmark et réglage auto",
    "Comportement", "Apparence", "Quand s'exécuter", "Intensité par défaut",                           # 10-14
    "Latence de lecture en direct",
    "Actif", "En attente", "Désactivé", "Erreur", "Désactivé", "Inactif", "Démarrage",                 # 16-22
    "En pause sur batterie",
    "Choisissez un disque dans les Paramètres", "Ajoutez des jeux dans l'onglet Jeux",
    "En attente du lancement d'un jeu", "En attente que la fenêtre du jeu ait le focus",
    "Maintenu éveillé", "Sessions", "Blocages enregistrés", "Activé",                                  # 28-31
    "Aucun blocage enregistré pour l'instant.",
    "Chaque point est la lecture la plus lente de la seconde. Les pics au-dessus de la ligne rouge sont des blocages : des moments où le disque a hésité.",
    "Lancez un jeu (ou choisissez « Toujours actif ») pour voir la latence en direct.",
    "En attente de données...",
    "blocage", "maintenant", "Mise à jour disponible", "Télécharger",                                  # 36-39
    "Détecter les jeux installés", "Analyse...", "Ajouter un programme en cours…",
    "ou saisissez un nom de programme, p. ex. jeu.exe",
    "Ajouter", "Disque", "Intensité", "Par défaut",                                                    # 44-47
    "Aucun jeu pour l'instant.\nCliquez sur « Détecter les jeux installés » pour les trouver automatiquement.",
    "Choisir un programme en cours", "Ouvrez d'abord votre jeu, puis choisissez-le ici.",
    "Rechercher...", "Rien trouvé", "Jeux détectés", "Aucun nouveau jeu trouvé.",                      # 51-54
    "Recherche dans Steam, Epic Games et GOG. Vous pouvez toujours ajouter un jeu avec « Ajouter un programme en cours » ou en saisissant le nom de son exe.",
    "Choisissez les jeux pour lesquels garder votre disque éveillé.",
    "Le nom du programme est une estimation : vérifiez-le si un jeu ne se déclenche pas.",
    "Tout sélectionner", "Ajouter la sélection", "Fermer",                                             # 58-60
    "Disque à inspecter", "Actualiser", "Redémarrer en administrateur", "Lecture des infos du disque...",
    "Ce que Windows sait de ce disque, avec des conseils en langage clair.",
    "Santé", "Température", "Usure", "Durée de fonctionnement", "n/d",                                 # 66-70
    "{free} Go libres sur {total} Go",
    "Mesure le temps de la première lecture après une période d'inactivité du disque, avec et sans maintien d'activité, puis choisit le réglage le plus léger qui aide. Dure environ 2 minutes. Ne lancez pas de jeu pendant ce temps.",
    "Lancer le réglage auto", "Préparation…", "Annuler", "Annulé.", "Échec du test",                    # 73-77
    "Maintien d'activité", "ms moy.", "ms p95", "ms max", "Aucun",                                     # 78-82
    "Le maintien d'activité supprime les blocages dus à l'inactivité. Réglage recommandé : {p}.",
    "Aucun blocage dû à l'inactivité détecté sur ce disque : il se réveille vite. Le maintien d'activité n'aidera probablement pas ici.",
    "Ce disque hésite après une période d'inactivité, mais le maintien d'activité n'a pas clairement aidé. La cause est peut-être ailleurs : essayez le Test de lag.",
    "Utiliser {p} par défaut", "Enregistré.",                                                          # 86-87
    "Passez à votre jeu juste après avoir appuyé sur Démarrer. Après 10 secondes, Diskuick observe votre vrai disque, processeur et mémoire pendant 30 secondes et vous dit ce qui semble poser problème.",
    "Lancer le test de lag", "Démarrage dans {s} s : passez à votre jeu maintenant…", "Mesure en cours… continuez à jouer",
    "À titre indicatif : le réseau n'est pas mesuré.",
    "Seulement en jeu", "Toujours actif",                                                              # 93-94
    "Démarre automatiquement à l'ouverture d'un de vos jeux et s'arrête à sa fermeture. Ajoutez des jeux dans l'onglet Jeux.",
    "Fonctionne tout le temps que Diskuick est ouvert. Simple, mais garde le disque occupé même au repos.",
    "Disques à garder éveillés",
    "Force de la sollicitation du disque. Les jeux peuvent la remplacer.",
    "Légère", "Équilibrée", "Forte",                                                                   # 99-101
    "Minuscules lectures aléatoires, environ 10 par seconde. Charge minimale : essayez celle-ci d'abord.",
    "Lectures séquentielles légères, environ 20 par seconde. Pour les disques qui ont besoin d'un peu plus.",
    "Lectures en continu. Effet le plus fort, mais le disque est toujours occupé.",
    "Secondes entre les lectures (avancé)", "par défaut",                                              # 105-106
    "Saisissez un nombre positif, ou laissez vide pour la valeur par défaut.",
    "Pause sur batterie", "Portables : ne pas occuper le disque une fois débranché.",
    "Seulement quand le jeu est au premier plan", "Se met en pause quand vous quittez le jeu avec Alt+Tab.",
    "Notifier au lancement d'un jeu", "Une petite notification dans la zone de notification.",
    "Démarrer avec Windows", "S'exécute discrètement dans la zone de notification à l'ouverture de session.",
    "Thème", "Système", "Sombre", "Thème clair", "Langue",                                             # 116-120
    "Rechercher les mises à jour",
    "Seul le nom du dépôt est contacté ; rien sur vous n'est envoyé.",
    "La recherche de mises à jour est désactivée tant qu'aucun dépôt de versions n'est défini.",
    "Ouvrir le dossier de données", "Ouvrir le journal des blocages",
    "L'intensité intelligente est activée : elle choisit le niveau pour vous. Désactivez-la pour en choisir un vous-même.",
    "Intelligente",                                                                                    # 127
    "Redémarrer en administrateur pour une analyse rapide",
    "Montre ce qui occupe de la place, du plus gros au plus petit. Rien n'est modifié ni supprimé ici. En administrateur, il lit directement la table des fichiers du disque (comme WizTree) en quelques secondes ; sinon il lit les dossiers un par un, ce qui peut prendre une à deux minutes.",
    "Durée : {s} s.", "Renommer le jeu", "Nom à afficher pour",                                         # 130-132
    "Surimpression de latence",
    "Un petit affichage en direct dans un coin de l'écran pendant que le disque est maintenu éveillé (un jeu tourne, ou « Toujours actif »). C'est une fenêtre séparée qui ne touche jamais au jeu et s'affiche par-dessus les jeux en fenêtré et sans bordure. Elle ne peut pas s'afficher sur le plein écran exclusif (par exemple Battlefield 3) : passez ce jeu en sans bordure ou en fenêtré.",
    "Afficher la surimpression pendant un jeu", "Position", "Aperçu",                                   # 135-137
    "En haut à gauche", "En haut à droite", "En bas à gauche", "En bas à droite",
    "Mettre à jour", "Téléchargement… {p} %", "Échec de la mise à jour", "Réessayer", "Vérifier",      # 142-146
    "Vérification…", "Vous êtes à jour.", "Impossible de vérifier les mises à jour.", "Mise à jour disponible : {v}",
    "Ouvrir Diskuick", "Quitter", "Le disque {d}: est maintenu éveillé",                               # 151-153
    "Impossible de modifier le démarrage avec Windows",
    "Dernières sessions", "Était-ce le disque ? Un résumé de vos dernières sessions de jeu.",
    "Aucune session enregistrée. Un rapport apparaît à la fermeture d'un jeu.",
    "Pire lecture", "blocages", "pic", "ping",                                                         # 158-161
    "Marques de lag",
    "Appuyez sur Ctrl+Alt+L (ou utilisez le menu de la zone de notification) au moment où un jeu lague. Diskuick enregistre ce que faisait le PC à cet instant.",
    "Aucun lag marqué pour l'instant.", "Marquer un lag", "Lag marqué", "Session terminée",            # 162-167
    "Fermé pour libérer des ressources", "Intensité intelligente",
    "Démarre en Légère et monte seulement tant que le disque continue de bloquer, puis redescend quand tout va bien. Ignore le choix ci-dessus (le réglage propre à un jeu reste prioritaire).",
    "Alertes du disque", "Prévenez-moi quand le disque de jeu est presque plein ou n'est plus en bonne santé.", # 171-172
    "Raccourcis clavier",
    "Ctrl+Alt+L marque un moment de lag. Ctrl+Alt+O affiche ou masque la surimpression.",
    "Afficher la surimpression pendant que le disque est maintenu éveillé",
    "Afficher aussi la charge CPU et GPU", "Afficher aussi les FPS",                                   # 176-177
    "Nécessite PresentMon.exe à côté de Diskuick.exe et Diskuick lancé en administrateur.",
    "Vérification réseau (facultatif)",
    "Vérifie si votre connexion internet peut être à l'origine du lag. Saisissez 1.1.1.1 pour vérifier votre connexion générale, ou l'adresse d'un serveur sur lequel vous jouez (le :port est facultatif et vaut 443 par défaut). Pendant un Test de lag (et quand vous marquez un lag), Diskuick mesure le ping (le temps de réponse du serveur) et la perte de paquets (réponses qui n'arrivent jamais), pour distinguer un problème réseau d'un problème de disque. Seule une connexion normale est ouverte, quelques fois par seconde, et rien sur vous n'est envoyé. Laissez vide pour le désactiver.",
    "Hôte", "Saisissez un nom d'hôte ou une adresse, éventuellement avec :port.",
    "Mode jeu (facultatif)",
    "Quand l'un de vos jeux démarre, demande poliment à ces programmes de se fermer (ils peuvent encore vous demander d'enregistrer) et les rouvre à la fin du jeu. Rien n'est fermé de force.",
    "Aucun programme choisi.", "Retirer", "Ce programme est protégé et ne peut pas être fermé.",        # 185-187
    "Les rouvrir ensuite", "Disque", "Disque à analyser", "Analyser", "Arrêter", "Arrêt...", "Remonter", # 188-194
    "Nom", "Taille", "Fichiers", "% du parent", "Ouvrir dans l'Explorateur", "Ouvrir ce dossier ici",  # 195-200
    "Analyseur d'espace disque",
    "Montre ce qui occupe de la place, du plus gros au plus petit. Il lit les dossiers un par un, donc un gros disque prend une à deux minutes. Rien n'est modifié ni supprimé ici.",
    "Appuyez sur Analyser pour commencer.", "Analysez un disque pour voir sa carte ici.",               # 203-204
    "Analyse de {drive} : ...", "Analyse de {drive} : {files} fichiers, {size} jusqu'ici",
    "{size} trouvés dans {files} fichiers et {folders} dossiers.", "Disque utilisé : {used}.",
    "Arrêté prématurément, le résultat est donc partiel.",
    "Certains dossiers sont protégés ; exécutez en administrateur pour les inclure.",
    "Types de fichiers", "Quels types de fichiers occupent le plus de place sur ce disque.",           # 211-212
    "Nettoyage du disque",
    "Supprime uniquement des restes sûrs et régénérables : fichiers temporaires, caches et rapports de plantage. Vos propres fichiers ne sont jamais touchés. Cochez ce que vous voulez, vérifiez les tailles, puis nettoyez.",
    "Vérifier les tailles", "Vérification des tailles...", "Nettoyer la sélection", "Nettoyage...",   # 215-218
    "Cochez d'abord au moins un élément.", "Les éléments cochés libéreraient environ {size}.",
    "La Corbeille est vidée définitivement.",
    "Supprimer environ {size} de :\n\n{names}{note}\n\nContinuer ?",
    "{size} libérés ({files} fichiers). Les éléments en cours d'utilisation ont été ignorés.",
    "Fichiers temporaires", "Laissés par des programmes dans votre dossier Temp.",                    # 224-225
    "Fichiers temporaires de Windows", "Le dossier Temp propre à Windows. Exécutez en administrateur pour tout effacer.",
    "Cache des miniatures", "L'Explorateur reconstruit les aperçus d'images au besoin.",
    "Vidages mémoire et rapports d'erreurs", "Fichiers de diagnostic de programmes qui ont planté.",
    "Caches des navigateurs", "Caches de Chrome, Edge et Brave. Les sites se chargent un peu plus lentement une fois.",
    "Caches de shaders", "Caches de shaders du GPU. Les jeux peuvent saccader brièvement au prochain démarrage le temps de les reconstruire.",
    "Corbeille", "Supprime définitivement ce qui se trouve dans la Corbeille.",
    "Déplacer vers la Corbeille", "dossier", "fichier",                                                # 238-240
    "Déplacer ce {kind} vers la Corbeille ?\n\n{path}\n{size}\n\nVous pourrez le restaurer depuis la Corbeille.",
    "Déplacement vers la Corbeille...",
    "Impossible de le déplacer vers la Corbeille (en cours d'utilisation, protégé ou annulé).",
    "{size} déplacés vers la Corbeille. Analysez à nouveau pour actualiser les types de fichiers.",
    "Analyse rapide (table des fichiers NTFS).",
    "Exécutez Diskuick en administrateur pour une analyse bien plus rapide.",
    "Dossiers", "Libre",                                                                           # 246-247
    "p. ex. 1.1.1.1",
))
