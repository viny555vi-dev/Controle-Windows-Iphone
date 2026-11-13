# Controle Remoto do PC pelo iPhone

Transforma o iPhone em touchpad + controle de mídia para o computador, via Wi-Fi.
Não precisa instalar nada no iPhone: ele usa uma página no Safari.

> Bluetooth não é possível: a Apple não permite que o iPhone se passe por mouse/teclado Bluetooth.

## Requisitos

- **Windows 10 ou 11, 64 bits** (não funciona em Windows 10 de 32 bits).
- Mac com macOS recente (opcional).
- PC e iPhone na **mesma rede Wi-Fi**.

## Como usar

1. Baixe o arquivo da aba **Releases** (à direita nesta página):
   - Windows: `ControleRemoto-Windows.exe`
   - Mac: `ControleRemoto-macOS.zip` (descompacte antes)
2. Abra o programa. Vai aparecer uma janela preta com um ou mais endereços, tipo:
   `http://192.168.0.10:8765/?pin=1234`
3. No **Safari do iPhone**, abra esse endereço. Se houver mais de um, teste o outro.
4. Opcional: Compartilhar > **Adicionar à Tela de Início** para virar um ícone.

O PIN muda toda vez que o programa é aberto. Para parar, feche a janela.

## Problemas comuns no Windows 10

| Problema | Solução |
|---|---|
| "O Windows protegeu o computador" (SmartScreen) | Clique em **Mais informações > Executar assim mesmo**. Acontece com qualquer programa sem assinatura paga. |
| Antivírus/Defender bloqueia o .exe | É um falso positivo comum em programas feitos com PyInstaller. Restaure o arquivo na quarentena e adicione uma exceção. O código-fonte está neste repositório. |
| O iPhone não abre a página | Na janela do Firewall, marque **Redes privadas** e permita. Se já negou: Painel de Controle > Firewall > Permitir um aplicativo. Confirme também que a rede do PC está como "Privada" (Configurações > Rede e Internet > Wi-Fi > Propriedades). |
| Wi-Fi de visitantes / "isolamento de AP" no roteador | Alguns roteadores impedem aparelhos de se enxergarem. Use a rede principal. |
| Funciona, mas não controla Gerenciador de Tarefas/janelas de administrador | Clique com o botão direito no .exe > **Executar como administrador**. |
| Mouse anda "errado" na tela | Já corrigido para telas com escala 125%/150%. Se persistir, abra um Issue. |

## Mac

Clique com o botão direito no programa > *Abrir*. Depois libere em
*Ajustes > Privacidade e Segurança > Acessibilidade* (e *Monitoramento de Entrada*).

## Controles

- 1 dedo: mover o mouse · toque: clique
- 2 dedos: rolar · toque com 2 dedos: botão direito
- Botões: play/pause, próximo, anterior, volume, mudo, tela cheia, ±10s, Esc, Enter...
- Campo de texto: digite e aperte Enter para enviar ao PC.

## Para o dono do repositório: como gerar uma nova versão

Releases > **Draft a new release** > crie uma tag (ex.: `v1.1`) > **Publish release**.
Em ~3 minutos o GitHub compila, testa e anexa os executáveis na release (acompanhe na aba **Actions**).
Se o teste automático do .exe falhar, a release não recebe o arquivo.
