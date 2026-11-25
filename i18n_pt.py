"""Portuguese (Brazil) strings, in the order of i18n_keys.KEYS. Best-effort translation - please have a native speaker review."""
from i18n import register_seq

register_seq("pt", "Português (Brasil)", (
    "Painel", "Jogos", "Ferramentas", "Configurações",                                                 # 1-5
    "Mantém seu drive ativo enquanto você joga",
    "Travadas recentes", "Saúde do drive", "Teste de lag", "Benchmark e ajuste automático",
    "Comportamento", "Aparência", "Quando executar", "Intensidade padrão",                             # 10-14
    "Latência de leitura ao vivo",
    "Ativo", "Aguardando", "Desligado", "Erro", "Desativado", "Ocioso", "Iniciando",                   # 16-22
    "Pausado na bateria",
    "Escolha um drive em Configurações", "Adicione jogos na aba Jogos",
    "Aguardando um jogo iniciar", "Aguardando a janela do jogo ficar em foco",
    "Mantido ativo", "Sessões", "Travadas registradas", "Ativado",                                     # 28-31
    "Nenhuma travada registrada ainda.",
    "Cada ponto é a leitura mais lenta daquele segundo. Picos acima da linha vermelha são travadas: momentos em que o drive hesitou.",
    "Inicie um jogo (ou escolha “Sempre ativo”) para ver a latência ao vivo.",
    "Aguardando dados...",
    "travada", "agora", "Atualização disponível", "Baixar",                                           # 36-39
    "Detectar jogos instalados", "Procurando...", "Adicionar programa em execução…",
    "ou digite o nome de um programa, ex.: jogo.exe",
    "Adicionar", "Drive", "Intensidade", "Padrão",                                                     # 44-47
    "Nenhum jogo ainda.\nClique em “Detectar jogos instalados” para encontrá-los automaticamente.",
    "Escolha um programa em execução", "Abra seu jogo primeiro e depois escolha-o aqui.",
    "Pesquisar...", "Nada encontrado", "Jogos detectados", "Nenhum jogo novo encontrado.",             # 51-54
    "Procurou na Steam, Epic Games e GOG. Você ainda pode adicionar um jogo com “Adicionar programa em execução” ou digitando o nome do exe.",
    "Escolha os jogos para os quais manter seu drive ativo.",
    "O nome do programa é um palpite: confira se um jogo não ativar.",
    "Selecionar tudo", "Adicionar selecionados", "Fechar",                                             # 58-60
    "Drive a inspecionar", "Atualizar", "Reiniciar como administrador", "Lendo informações do drive...",
    "O que o Windows sabe sobre este drive, com conselhos em linguagem simples.",
    "Saúde", "Temperatura", "Desgaste", "Tempo ligado", "n/d",                                         # 66-70
    "{free} GB livres de {total} GB",
    "Mede quanto tempo a primeira leitura leva depois que o drive ficou ocioso, com e sem manutenção ativa, e escolhe a configuração mais leve que ajuda. Leva cerca de 2 minutos. Não abra um jogo enquanto isso.",
    "Executar ajuste automático", "Preparando…", "Cancelar", "Cancelado.", "O teste falhou",          # 73-77
    "Manutenção ativa", "ms méd.", "ms p95", "ms máx.", "Nenhuma",                                     # 78-82
    "A manutenção ativa elimina as travadas por ociosidade. Configuração recomendada: {p}.",
    "Nenhuma travada por ociosidade detectada neste drive: ele acorda rápido. A manutenção ativa provavelmente não ajudará aqui.",
    "Este drive hesita após ficar ocioso, mas a manutenção ativa não ajudou claramente. A causa pode estar em outro lugar: tente o Teste de lag.",
    "Usar {p} como padrão", "Salvo.",                                                                  # 86-87
    "Mude para o seu jogo logo após apertar Iniciar. Após 10 segundos, o Diskuick observa seu disco, CPU e memória reais por 30 segundos e diz o que parece errado.",
    "Iniciar teste de lag", "Começando em {s} s: mude para o seu jogo agora…", "Medindo… continue jogando",
    "Apenas indicativo: a rede não é medida.",
    "Só durante o jogo", "Sempre ativo",                                                               # 93-94
    "Inicia automaticamente quando um dos seus jogos abre e para quando ele fecha. Adicione jogos na aba Jogos.",
    "Roda o tempo todo em que o Diskuick está aberto. Simples, mas mantém o drive ocupado mesmo em repouso.",
    "Drives a manter ativos",
    "Quanto estimular o drive. Os jogos podem substituir isto.",
    "Leve", "Equilibrada", "Pesada",                                                                   # 99-101
    "Pequenas leituras aleatórias, cerca de 10 por segundo. Menor sobrecarga: experimente esta primeiro.",
    "Leituras sequenciais leves, cerca de 20 por segundo. Para drives que precisam de um pouco mais.",
    "Leituras contínuas. Efeito mais forte, mas o drive fica sempre ocupado.",
    "Segundos entre leituras (avançado)", "padrão",                                                    # 105-106
    "Digite um número positivo ou deixe vazio para o padrão.",
    "Pausar na bateria", "Notebooks: não manter o drive ocupado quando desconectado da tomada.",
    "Só com o jogo em foco", "Pausa quando você sai do jogo com Alt+Tab.",
    "Avisar quando um jogo iniciar", "Uma pequena notificação na bandeja.",
    "Iniciar com o Windows", "Roda discretamente na bandeja ao entrar.",
    "Tema", "Sistema", "Escuro", "Tema claro", "Idioma",                                               # 116-120
    "Verificar atualizações",
    "Apenas o nome do repositório é contatado; nada sobre você é enviado.",
    "A verificação de atualizações fica desativada até que um repositório de versões seja definido.",
    "Abrir pasta de dados", "Abrir registro de travadas",
    "A intensidade inteligente está ativa: ela escolhe o nível para você. Desative para escolher um você mesmo.",
    "Inteligente",                                                                                     # 127
    "Reiniciar como administrador para uma varredura rápida",
    "Mostra o que ocupa espaço, do maior para o menor. Nada é alterado ou apagado aqui. Como administrador, lê diretamente a tabela de arquivos do drive (como o WizTree) e leva segundos; caso contrário, lê as pastas uma a uma, o que pode levar um ou dois minutos.",
    "Levou {s} s.", "Renomear jogo", "Nome a exibir para",                                            # 130-132
    "Overlay de latência",
    "Uma pequena leitura ao vivo em um canto da tela enquanto o drive é mantido ativo (um jogo está rodando ou “Sempre ativo”). É uma janela separada que nunca toca no jogo e aparece sobre jogos em janela e sem bordas. Não pode aparecer sobre tela cheia exclusiva (por exemplo, Battlefield 3): mude esse jogo para sem bordas ou em janela.",
    "Mostrar overlay enquanto um jogo roda", "Posição", "Pré-visualizar",                             # 135-137
    "Superior esquerdo", "Superior direito", "Inferior esquerdo", "Inferior direito",
    "Atualizar agora", "Baixando… {p}%", "Falha na atualização", "Tentar de novo", "Verificar agora",  # 142-146
    "Verificando…", "Você está em dia.", "Não foi possível verificar atualizações.", "Atualização disponível: {v}",
    "Abrir o Diskuick", "Sair", "Mantendo o drive {d}: ativo",                                         # 151-153
    "Não foi possível alterar a inicialização com o Windows",
    "Últimas sessões", "Foi o drive? Um resumo das suas últimas sessões de jogo.",
    "Nenhuma sessão registrada ainda. Um relatório aparece quando um jogo fecha.",
    "Pior leitura", "travadas", "pico", "ping",                                                        # 158-161
    "Marcas de lag",
    "Pressione Ctrl+Alt+L (ou use o menu da bandeja) no momento em que o jogo engasgar. O Diskuick salva o que o PC estava fazendo naquele instante.",
    "Nenhum lag marcado ainda.", "Marcar lag agora", "Lag marcado", "Sessão encerrada",                # 162-167
    "Fechado para liberar recursos", "Intensidade inteligente",
    "Começa em Leve e aumenta só enquanto o drive continua travando, depois volta ao normal quando está calmo. Ignora a escolha acima (a configuração própria de um jogo ainda vale).",
    "Alertas do drive", "Avise-me quando o drive de jogos estiver quase cheio ou deixar de estar saudável.", # 171-172
    "Atalhos de teclado",
    "Ctrl+Alt+L marca um momento de lag. Ctrl+Alt+O mostra ou oculta o overlay.",
    "Mostrar overlay enquanto o drive é mantido ativo",
    "Mostrar também a carga de CPU e GPU", "Mostrar também o FPS",                                     # 176-177
    "Requer o PresentMon.exe ao lado do Diskuick.exe e o Diskuick rodando como administrador.",
    "Verificação de rede (opcional)",
    "Verifica se a sua internet pode estar por trás do lag. Digite 1.1.1.1 para verificar sua conexão geral, ou o endereço de um servidor em que você joga (a :porta é opcional e o padrão é 443). Durante um Teste de lag (e quando você marca um lag), o Diskuick mede o ping (quanto tempo o servidor leva para responder) e a perda de pacotes (respostas que nunca chegam), para você distinguir um problema de rede de um problema do drive. Apenas uma conexão normal é aberta, algumas vezes por segundo, e nada sobre você é enviado. Deixe vazio para manter desativado.",
    "Host", "Digite um nome de host ou endereço, opcionalmente com :porta.",
    "Modo jogo (opcional)",
    "Quando um dos seus jogos inicia, pede educadamente a estes programas que fechem (eles ainda podem pedir para você salvar) e os reabre quando o jogo termina. Nada é fechado à força.",
    "Nenhum programa escolhido.", "Remover", "Esse programa é protegido e não pode ser fechado.",       # 185-187
    "Reabri-los depois", "Disco", "Drive a analisar", "Analisar", "Parar", "Parando...", "Subir",      # 188-194
    "Nome", "Tamanho", "Arquivos", "% do pai", "Abrir no Explorer", "Abrir esta pasta aqui",           # 195-200
    "Analisador de espaço em disco",
    "Mostra o que ocupa espaço, do maior para o menor. Lê as pastas uma a uma, então um drive grande leva um ou dois minutos. Nada é alterado ou apagado aqui.",
    "Pressione Analisar para começar.", "Analise um drive para ver o mapa dele aqui.",                 # 203-204
    "Analisando {drive}: ...", "Analisando {drive}: {files} arquivos, {size} até agora",
    "Encontrados {size} em {files} arquivos e {folders} pastas.", "Drive usado: {used}.",
    "Interrompido antes do fim, então o resultado é parcial.",
    "Algumas pastas são protegidas; execute como administrador para incluí-las.",
    "Tipos de arquivo", "Quais tipos de arquivo usam mais espaço neste drive.",                       # 211-212
    "Limpeza de disco",
    "Remove apenas sobras seguras e regeneráveis: arquivos temporários, caches e relatórios de falhas. Seus próprios arquivos nunca são tocados. Marque o que quiser, confira os tamanhos e limpe.",
    "Verificar tamanhos", "Verificando tamanhos...", "Limpar selecionados", "Limpando...",           # 215-218
    "Marque pelo menos um item primeiro.", "Os itens marcados liberariam cerca de {size}.",
    "A Lixeira é esvaziada permanentemente.",
    "Remover cerca de {size} de:\n\n{names}{note}\n\nContinuar?",
    "Liberados {size} ({files} arquivos). Itens em uso foram ignorados.",
    "Arquivos temporários", "Deixados por programas na sua pasta Temp.",                              # 224-225
    "Arquivos temporários do Windows", "A pasta Temp do próprio Windows. Execute como administrador para limpar tudo.",
    "Cache de miniaturas", "O Explorer recria as prévias de imagens quando necessário.",
    "Despejos de falhas e relatórios de erros", "Arquivos de diagnóstico de programas que travaram.",
    "Caches de navegadores", "Caches do Chrome, Edge e Brave. Os sites carregam um pouco mais devagar uma vez.",
    "Caches de shaders", "Caches de shaders da GPU. Os jogos podem engasgar brevemente na próxima vez que iniciarem enquanto eles são recriados.",
    "Lixeira", "Apaga permanentemente o que está na Lixeira.",
    "Mover para a Lixeira", "pasta", "arquivo",                                                        # 238-240
    "Mover {kind} para a Lixeira?\n\n{path}\n{size}\n\nVocê pode restaurá-lo pela Lixeira.",
    "Movendo para a Lixeira...",
    "Não foi possível mover para a Lixeira (em uso, protegido ou cancelado).",
    "{size} movidos para a Lixeira. Analise de novo para atualizar os tipos de arquivo.",
    "Varredura rápida (tabela de arquivos NTFS).",
    "Execute o Diskuick como administrador para uma varredura muito mais rápida.",
    "Pastas", "Livre",                                                                           # 246-247
    "ex.: 1.1.1.1",
))
