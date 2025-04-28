/*!
 * Componente ChatBot IPM.
 * IPM Sistemas (C) - Atende.net (C) - 2023
 * https://www.ipm.com.br/
 * ESTE CODIGO FONTE E QUALQUER DOCUMENTAÇÃO QUE O ACOMPANHE SÃO PROTEGIDOS PELA LEI DE DIREITOS AUTORAIS INTERNACIONAIS
 * E NÃO PODE SER REVENDIDO OU REDISTRIBUÍDO. A REPRODUÇÃO OU DISTRIBUIÇÃO NÃO AUTORIZADA ESTÁ SUJEITA A PENALIDADES
 * CIVIS E PENAIS.
 */
(($) => {
    let areaMensagens                = null;
    let areaDigitacao                = null;
    let areaVisualizacaoArquivos     = null;
    let areaDropArquivos             = null;
    let areaAlerta                   = null;
    let areaCabecalho                = null;
    let botaoConfirma                = null;
    let campoEnviarArquivos          = null;
    let botaoMinimizar               = null;
    let botaoFechar                  = null;
    let iconeBot                     = null;
    let modal                        = null;
    let aceiteTermosUso              = null;
    let containerRodape              = null;
    let linkTermosUso                = null;
    let linkUsoRodape                = null;
    let conteudoTermosUso            = null;
    let navSubbotoes                 = null;
    let loader                       = null;
    let areaListaArquivosAnexados    = null;
    let areaInfoArquivosAnexados     = null;
    let __timeoutAtual               = null;
    let reconhecimentoVoz            = null;
    let botaoIniciarGravacaoAudio    = null;
    let botaoEnviarAudioGravado      = null;
    let botaoExcluirAudio            = null;
    let containerGravarAudio         = null;
    let iconeIniciarGravacaoAudio    = null;
    let bUsaIaVoz                    = (window.SpeechRecognition || window.webkitSpeechRecognition) ? false : true;
    let tempoGravacaoAudio           = null;
    let bMostraMensagemInicializacao = false;
    
    let isDesenvolvimento            = false;
    let sContexto                    = null;
    let __callbackTempo              = [];
    let workerPdfJS;

    const status = {
        iniciado: false,
        _permiteDigitar: false,
        aceitouTermos: false,
        client: null,
        estadoAtual: null,
        token: '',
        permiteDigitar: null,
        imagemBot: '',
        nomeBot: 'IPM-Bot',
        ultimoRemetente: '',
        ultimaMensagem: [],
        arquivosAnexados: []
    };

    let timeout = null;
    Object.defineProperties(status, {
        permiteDigitar: {
            set: (val) => {
                if (val && status.aceitouTermos) {
                    areaDigitacao.removeAttribute('disabled');
                    areaDigitacao.setAttribute('placeholder', areaDigitacao.getAttribute('data-placeholder'));
                    botaoConfirma.removeAttribute('disabled');
                    botaoIniciarGravacaoAudio.removeAttribute('disabled');
                    campoEnviarArquivos.removeAttribute('disabled')
                    const inputAtual = $('.mensagem_form_input:not(:disabled)');
                    if (inputAtual && inputAtual.focus) {
                        inputAtual.focus();
                    }
                    else {
                        areaDigitacao.focus();
                    }
                    timeout && clearTimeout(timeout);
                    timeout = null;
                }
                else {
                    areaDigitacao.setAttribute('disabled', '');
                    areaDigitacao.setAttribute('placeholder', 'Por favor aguarde um pouco...');
                    timeout && clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        timeout = null;
                        areaDigitacao.setAttribute('placeholder', 'Caso esteja demorando muito, tente atualizar a página....');
                    }, 20000);
                    botaoConfirma.setAttribute('disabled', '');
                    botaoIniciarGravacaoAudio.setAttribute('disabled', '');
                    campoEnviarArquivos.setAttribute('disabled', '');
                }
                status['_permiteDigitar'] = val;
            },
            get: () => {
                return status['_permiteDigitar'];
            }
        }
    });
    window['clientStatus'] = status;

    function updateAlturaAreaDigitacao(){
        if(__timeoutAtual){
            return;
        }
        __timeoutAtual = setTimeout(() => {
            const estilos = getComputedStyle(areaDigitacao);
            const padding = parseInt(estilos.paddingTop) + parseInt(estilos.paddingBottom);
            const alturaLinha = parseInt(estilos.lineHeight);
            areaDigitacao.style.setProperty('height', 0);
            const numLinhas = (areaDigitacao.scrollHeight - padding) / alturaLinha;
            areaDigitacao.style.setProperty('height', '');
            areaDigitacao.style.setProperty('--numero-linhas', numLinhas || 0);
            __timeoutAtual = null;
            if(status.ultimaMensagem.length){
                var bBoxDiv = status.ultimaMensagem[status.ultimaMensagem.length - 1].parentElement.getBoundingClientRect();
                var bBoxArea = areaMensagens.getBoundingClientRect();
                areaMensagens.scrollTop = areaMensagens.scrollTop + bBoxDiv.y + bBoxDiv.height + 100 - bBoxArea.y - bBoxArea.height;
            }
        }, 200);
    }
    
    /**
     * Inicia a conversa, apresentando as mensagens iniciais.
     */
    const iniciaConversa = () => {
        loader.style.display = '';
        if (!status.client) return;
        status.client.emit('iniciar');
        status.iniciado = true;
        setTimeout(() => loader.style.display = 'none', 650);
    }

    /**
     * Adiciona os eventos base dos campos.
     */
    function iniciaEventos() {
        areaDigitacao.setAttribute('disabled', '');
        botaoConfirma.setAttribute('disabled', '');
        botaoIniciarGravacaoAudio.setAttribute('disabled', '');
        campoEnviarArquivos.setAttribute('disabled', '')
        areaDigitacao.addEventListener('input', updateAlturaAreaDigitacao);
        areaDigitacao.addEventListener('keydown', (e) => {
            if (e.key == 'Enter' && !e.shiftKey) {
                botaoConfirma.click();
                e.preventDefault();
            }
        });
        areaDigitacao.addEventListener('keyup', (e) => {
            if(areaDigitacao.value.length == 0) {
                botaoConfirma.classList.add('botao_minimizado');
                if(botaoIniciarGravacaoAudio.classList.contains('botao_minimizado')){
                    botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
                }
            }
            else {
                areaDigitacao.removeAttribute('disabled');
                botaoIniciarGravacaoAudio.classList.add('botao_minimizado');
                if(botaoConfirma.classList.contains('botao_minimizado')){
                    botaoConfirma.classList.remove('botao_minimizado');    
                }
            }
        });
        botaoConfirma.addEventListener('click', (e) => {
            const texto = areaDigitacao.value;
            enviaMensagem(texto);
        });
        botaoIniciarGravacaoAudio.addEventListener('click', () => {
            if(!areaDigitacao.classList.contains('gravando')){
                iniciarGravacao();
            }
        });
        botaoMinimizar.addEventListener('click', () => {
            //Maximizar
            if (areaMensagens.classList.contains('area_mensagens_minimizada')) {
                if(!status.iniciado) {
                    iniciaCliente();
                    setTimeout(() => {
                        iniciaConversa();
                    }, 500);
                }
                maximizar();
            }
            //Minimizar
            else {
                containerRodape.classList.add('area_rodape_minimizada');
                areaMensagens.classList.add('area_mensagens_minimizada');
                areaDigitacao.classList.add('area_digitacao_minimizada');
                botaoConfirma.classList.add('botao_minimizado');
                botaoIniciarGravacaoAudio.classList.add('botao_minimizado');
                areaCabecalho.classList.add('cabecalho_chatbot_minimizado');
                botaoMinimizar.firstChild.classList.remove('fa-window-minimize');
                botaoMinimizar.firstChild.classList.add('fa-angle-double-up');
                botaoMinimizar.title = 'Maximizar Conversa';
                window.parent && window.parent.postMessage(['chatbot', status.id, 'minimizar'], '*');
                containerBase.classList.add('minimizado');
            }
        });
        botaoFechar.addEventListener('click', () => {
            exibeAlertaConfirma('Deseja realmente finalizar esta conversa?').then((confirma) => {
                if (confirma) {
                    window.parent && window.parent.postMessage(['chatbot', status.id, 'finalizar'], '*');
                    status.client.emit('finalizar');
                    botaoFechar.style.display = 'none';
                    areaDigitacao.style.display = 'none';
                    botaoConfirma.style.display = 'none';
                    botaoIniciarGravacaoAudio.style.display = 'none';
                    areaAlerta.style.display = 'none';
                    areaCabecalhoMinimizado.style.pointerEvents = 'none';
                    setTimeout(() => botaoMinimizar.click(), 2000); // Aguarda a mensagem final e minimiza o chat.
                }
            });
        });
        $('#modal .modal_confirmar').addEventListener('click', () => {
            confirmaModalAtual(true);
        });
        $('#modal .modal_rejeitar').addEventListener('click', () => {
            confirmaModalAtual(false);
        });
        $('#modal .modal_aceite').addEventListener('click', () => {
            confirmaModalAtual(false);
        });

        // Limpa os eventos nativos de drag DEIXAR ESCONDIDO POR ENQUANTO
        // useMultipleEventsListeners(containerBase, (e) => {
        //     e.stopPropagation();
        //     e.preventDefault();
        // }, 'drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop')

        // //Mostra a drop area
        // useMultipleEventsListeners(containerBase, () => {
        //     areaDropArquivos.style.setProperty('--drag-area-view', 10)
        // }, 'dragover', 'dragenter')

        //  //Esconde a Drop area
        //  useMultipleEventsListeners(containerBase, () => {
        //     areaDropArquivos.style.setProperty('--drag-area-view', -1)
        // }, 'dragleave', 'dragend', 'drop')

        // containerBase.addEventListener('drop', e => {
        //     addArquivoAnexo(...e.dataTransfer.files)
        // })

        // areaVisualizacaoArquivos.querySelector('#btn_limpar_arquivos').addEventListener('click', limpaArquivosAnexados)
        // campoEnviarArquivos.addEventListener('change', () => {
        //     addArquivoAnexo(...campoEnviarArquivos.files)
        // })
    }

    /**
     * Alteração do layout necessarias para a abertura do chat
     */
    function maximizar() {
        if(containerMensagemInicializacao.classList.contains('hover')){
            escondeMensagemInicializacao();
        }
        containerRodape.classList.remove('area_rodape_minimizada');
        areaMensagens.classList.remove('area_mensagens_minimizada');
        areaDigitacao.classList.remove('area_digitacao_minimizada');
        botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
        areaCabecalho.classList.remove('cabecalho_chatbot_minimizado');
        botaoMinimizar.firstChild.classList.add('fa-window-minimize');
        botaoMinimizar.firstChild.classList.remove('fa-angle-double-up');
        botaoMinimizar.title = 'Minimizar Conversa';
        window.parent && window.parent.postMessage(['chatbot', status.id, 'maximizar'], '*');
        containerBase.classList.remove('minimizado');
        setTimeout(() => {
            if (status.ultimaMensagem.length) {
                var bBoxDiv = status.ultimaMensagem[status.ultimaMensagem.length - 1].parentElement.getBoundingClientRect();
                var bBoxArea = areaMensagens.getBoundingClientRect();
                areaMensagens.scrollTop = areaMensagens.scrollTop + bBoxDiv.y + bBoxDiv.height + 100 - bBoxArea.y - bBoxArea.height;
            }
        });
    }

    /**
     * Verifica o aceite as informações do termo de uso.
     */
    function verificaAceiteTermosUso() {
        aceiteTermosUso.style.display = '';
        const botaoAceitar = $('#termos_uso .aceite_termos_uso_aceitar');
        const botaoRejeitar = $('#termos_uso .aceite_termos_uso_rejeitar');
        botaoAceitar.focus();
        botaoRejeitar.addEventListener('click', () => {
            window.parent && window.parent.postMessage(['chatbot', status.id, 'finalizar'], '*');
            status.client.emit('finalizar');
            botaoFechar.style.display = 'none';
            areaDigitacao.style.display = 'none';
            botaoConfirma.style.display = 'none';
            botaoIniciarGravacaoAudio.style.display = 'none';
            areaAlerta.style.display = 'none';
            aceiteTermosUso.remove();
            setTimeout(() => {
                botaoMinimizar.click();
                botaoMinimizar.focus();
                botaoMinimizar.remove();
            });
        });
    }

    /**
     * Hook para resgate dos arquivos anexados no formato item de anexo de mensagem.
     * @returns {Promise<MensagemAnexo[]>>}
     */
    const useArquivosAnexadosAsAnexo = async () => {
        let anexos = [];
        if (!status.arquivosAnexados.length) {
            return anexos;
        }
        async function lerArquivo(arquivo) {
            const reader = new FileReader();
            return new Promise((resolve) => {
                reader.onload = (event) => {
                    const base64Content = event.target.result.split(',')[1];
                    resolve(base64Content);
                };
                reader.readAsDataURL(arquivo);
            });
        }
        anexos = await Promise.all(status.arquivosAnexados.map(async arquivo => {
            let conteudoArquivoBase64 = await lerArquivo(arquivo)
            return {
                tipo: 'anexo',
                dados: conteudoArquivoBase64,
                conteudo: arquivo.name,
                mime: arquivo.type
            };
        }));
        return anexos;
    }

    /**
     * Envia uma mensagem.
     * @param {string} conteudo 
     * @returns 
     */
    async function enviaMensagem(conteudo) {
        if (!status.permiteDigitar) {
            return false;
        }
        status.permiteDigitar = false;
        if (!conteudo.length) {
            status.permiteDigitar = true;
            return false;
        }
        areaAlerta.innerHTML = '';
        areaAlerta.classList.remove('area_alerta_visivel');

        const arquivosAnexados = []; // Deixar escondido por enquanto
        // const arquivosAnexados = await useArquivosAnexadosAsAnexo()
        adicionaMensagem('usuario', conteudo, arquivosAnexados);
        // limpaArquivosAnexados();  //Deixar escondido por enquanto

        areaDigitacao.value = '';
        areaDigitacao.style.setProperty('--numero-linhas', '');

        /** @type {Mensagem} */
        const message = {
            autor: 'usuario',
            anexos: arquivosAnexados,
            conteudo
        }
        status.client.emit('ipmmessage', message);
        return true;
    }

    /**
     * Exibe um texto de alerta.
     * @param {string} conteudo 
     */
    function exibeAlerta(conteudo, tipo = 'atencao', tempo = 10000){
        let p = document.createElement('p');
        p.classList.add('alerta');
        p.innerText = conteudo;
        areaAlerta.classList.add('area_alerta_visivel');
        areaAlerta.classList.add(tipo);
        areaAlerta.append(p);
        function fnRemove(){
            if (areaAlerta.classList.contains('aviso')) {
                p.style.setProperty('opacity', 0);
                areaAlerta.classList.remove('area_alerta_visivel');
                areaAlerta.classList.remove(tipo);
                p.remove();
            }
            if(p.previousSibling){
                p.style.setProperty('opacity', 0);
                setTimeout(() => {
                    p.remove();
                }, 500);
            }
            else {
                setTimeout(fnRemove, tempo);
            }
        }
        setTimeout(fnRemove, tempo);
    }

    let fnModalAtual = false;
    /**
     * Exibe um alerta solicitando confirmação do usuário.
     * @param {string} texto 
     * @returns {Promise<boolean>}
     */
    function exibeAlertaConfirma(texto) {
        return new Promise((resolve) => {
            $('#modal > .modal_texto').innerText = texto;
            modal.classList.remove('modal_oculto');
            modal.removeAttribute('aria-hidden');
            modal.setAttribute('tabindex', '0');
            fnModalAtual = resolve;
        });
    }

    /**
     * Confirma o estado do modal.
     * @param {boolean} status 
     */
    function confirmaModalAtual(status) {
        fnModalAtual && fnModalAtual(status);
        fnModalAtual = null;
        modal.classList.add('modal_oculto');
        modal.setAttribute('aria-hidden', true);
        modal.setAttribute('tabindex', '-1');
    }

    /**
     * Adiciona uma mensagem em tela.
     * @param {string} origem 
     * @param {string} textoMensagem 
     * @param {MensagemAnexo} anexos
     * @returns 
     */
    function adicionaMensagem(origem, textoMensagem, anexos, tempo) {
        if (!textoMensagem) {
            return;
        }
        if (status.ultimoRemetente != origem) {
            navSubbotoes.innerHTML = '';
            navSubbotoes.classList.remove('mensagem_subbotoes_collapsavel');
            navSubbotoes.classList.remove('mensagem_subbotoes_expandido');
            status.ultimaMensagem.forEach(mensagem => {
                if (mensagem.__form) {
                    mensagem.__form.__fieldset.disabled = true;
                }
                if (mensagem.__navBotoes) {
                    mensagem.__navBotoes.classList.add('mensagem_botoes_desativados');
                    mensagem.__navBotoes.__botoesAcoes.forEach(botao => {
                        if (botao.classList.contains('mensagem_botao_opcao')) {
                            // Clona o elemento e substitui, isto remove todos os listeners dele.
                            const novoBotao = botao.cloneNode(true);
                            botao.parentElement.replaceChild(novoBotao, botao);
                            mensagem.__navBotoes = null;
                        }
                    });
                }
            });
            status.ultimaMensagem = [];
        }
        status.ultimoRemetente = origem;
        navSubbotoes.style.display = 'none';
        const div = document.createElement('div');
        const icone = document.createElement('span');
        icone.classList.add('mensagem_icone');
        div.append(icone);
        const p = document.createElement('p');
        p.__origem_mensagem = origem;
        p.__conteudo_mensagem = textoMensagem;
        p.__anexos_mensagem = anexos;
        p.classList.add('mensagem');
        p.classList.add('mensagem_' + origem.replace(/\W+/g, ''));
        p.setAttribute('tabindex', '0');
        p.innerText = textoMensagem;
        let titulo = document.createElement('span');
        titulo.classList.add('usuario_mensagem');
        if (origem == 'usuario') {
            titulo.innerText = 'Você: ';
            icone.style.display = 'none';
        }
        else if (origem.startsWith('atendente')) {
            titulo.innerText = 'Atendente ' + origem.replace('atendente', '') + ': ';
            icone.classList.add('fa-solid');
            icone.classList.add('fa-message');
        }
        else if (origem == 'ipmbot') {
            titulo.innerText = status.nomeBot + ':';
            if (status.imagemBot) {
                const img = document.createElement('img');
                img.classList.add('imagem_bot');
                img.src = status.imagemBot;
                img.ariaLabel = 'Imagem do Assistente Virtual'
                icone.append(img);
            }
            else {
                icone.classList.add('fa-solid');
                icone.classList.add('fas fa-spinner fa-pulse');
            }
        }
        else if (origem != 'sistema') {
            titulo.innerText = origem + ': ';
            icone.style.display = 'none';
        }
        if (titulo.innerText) {
            titulo.ariaLabel = 'Mensagem de ' + titulo.innerText;
            p.prepend(titulo);
        }
        p.innerHTML = p.innerHTML.replace(/(https?:\/\/[^\s\[]+)(?:\[([^\]]+)\])?/, (_, $1, $2) => {
            function escapeHtml(v) {
                return v.replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }
            return '<a href="' + escapeHtml($1) + '" target="_blank">' + escapeHtml($2 ? $2 : $1) + '</a>';
        });
        let criouBotoes = false;
        let criouSubbotoes = false;
        let criouForm = false;
        let navBotoes = null;
        let form = null;
        if (anexos && anexos.length) {
            navBotoes = document.createElement('nav');
            form = document.createElement('form');
            const fieldset = document.createElement('fieldset');
            form.append(fieldset);
            form.__fieldset = fieldset
            anexos.forEach((anexo) => {
                switch (anexo.tipo) {
                    case 'link':
                    case 'card_link':
                        criaAnexoLink(p, anexo, anexo.tipo == 'card_link');
                        break;
                    case 'anexo':
                        criaAnexoDownload(p, anexo);
                        break;
                    case 'campo':
                        criouForm = true;
                        criaAnexoCampo(fieldset, anexo);
                        break;
                }
            });
            navBotoes.__botoesAcoes = anexos.map((anexo) => {
                if (anexo.tipo != 'opcao' && anexo.tipo != 'botao') {
                    return;
                }
                const botao = criaAnexoBotoes(anexo);
                if (anexo.tipo == 'botao' && anexo.acao != 'link' && !anexo.inline) {
                    navSubbotoes.append(botao);
                    navSubbotoes.style.display = '';
                    criouSubbotoes = true;
                }
                else {
                    criouBotoes = true;
                    navBotoes.append(botao);
                }
                return botao;
            }).filter(e => e);
            navBotoes.classList.add('mensagem_botoes');
        }
        if (criouForm) {
            const botao = document.createElement('button');
            botao.innerText = 'Confirmar';
            const icone = document.createElement('i');
            icone.classList.add('fas');
            icone.classList.add('fa-arrow-right');
            botao.prepend(icone);
            botao.classList.add('mensagem_form_confirmar');
            botao.type = 'submit';
            form.__fieldset.append(botao);
            form.classList.add('mensagem_form');
            form.addEventListener('submit', (e) => {
                enviaMensagem(Array.from(form.querySelectorAll('input')).map(e => e.value).join(', '));
                e.preventDefault();
                return false;
            });
            p.append(form);
            p.__form = form;
        }
        if (criouBotoes) {
            p.append(navBotoes);
            p.__navBotoes = navBotoes;
        }
        if (tempo) {
            let spanTempo = document.createElement('span');
            spanTempo.classList.add('tempo_mensagem');
            const date = new Date(tempo);
            spanTempo.innerText = ('' + date.getHours()).padStart(2, '0') + ':' + ('' + date.getMinutes()).padStart(2, '0');
            p.append(spanTempo);
            const localeDate = date.toLocaleString('pt-BR', {
                'timeZone': 'America/Sao_Paulo',
                'timeZoneName': 'short'
            });
            spanTempo.ariaLabel = 'Mensagem enviada em: ' + localeDate;
            spanTempo.setAttribute('data-tempo-completo', localeDate);
        }
        else {
            const tempoInicio = new Date().getTime();
            getTempo().then((tempo) => {
                tempo = tempo - (new Date().getTime() - tempoInicio);
                let spanTempo = document.createElement('span');
                spanTempo.classList.add('tempo_mensagem');
                const date = new Date(tempo);
                spanTempo.innerText = ('' + date.getHours()).padStart(2, '0') + ':' + ('' + date.getMinutes()).padStart(2, '0');
                p.append(spanTempo);
                const localeDate = date.toLocaleString('pt-BR', {
                    'timeZone': 'America/Sao_Paulo',
                    'timeZoneName': 'short'
                });
                spanTempo.ariaLabel = 'Mensagem enviada em: ' + localeDate;
                spanTempo.setAttribute('data-tempo-completo', localeDate);
            });
        }
        div.append(p);
        div.classList.add('base_mensagem');
        div.classList.add('base_mensagem_' + origem.replace(/\W+/g, ''));
        if (areaMensagens.lastChild && areaMensagens.lastChild.previousSibling) {
            div.style.setProperty('--altura-mensagem-anterior', areaMensagens.lastChild.previousSibling.clientHeight || 0);
        }
        areaMensagens.append(div);
        areaMensagens.append(navSubbotoes);
        const bBoxDiv = div.getBoundingClientRect();
        const bBoxArea = areaMensagens.getBoundingClientRect();
        areaMensagens.scrollTop = areaMensagens.scrollTop + bBoxDiv.y + bBoxDiv.height + 100 - bBoxArea.y - bBoxArea.height + areaVisualizacaoArquivos.clientHeight;
        status.ultimaMensagem.push(p);
        if (criouSubbotoes) {
            if (navSubbotoes.scrollHeight > navSubbotoes.clientHeight) {
                navSubbotoes.classList.add('mensagem_subbotoes_collapsavel');
                const buttonAbrir = document.createElement('button');
                buttonAbrir.classList.add('mensagem_botao');
                buttonAbrir.classList.add('mensagem_botao_botao');
                buttonAbrir.classList.add('mensagem_botao_botao_mais');
                buttonAbrir.innerText = '+';
                let aberto = false;
                const oNavRect = navSubbotoes.getBoundingClientRect();
                const aOcultos = Array.from(navSubbotoes.children).filter((el, i) => (el.getBoundingClientRect().top / 2) >= oNavRect.bottom)
                function atualizaEstadosSubBotoes() {
                    aOcultos.forEach((e, i) => {
                        if (aberto) {
                            e.style.setProperty('transition-delay', (i * 0.05) + 's');
                            e.setAttribute('tabindex', '');
                            e.setAttribute('aria-hidden', 'false');
                            e.style.setProperty('opacity', '1');
                        }
                        else {
                            e.style.setProperty('transition-delay', ((aOcultos.length - i) * 0.05) + 's');
                            e.setAttribute('tabindex', '-1');
                            e.setAttribute('aria-hidden', 'true');
                            e.style.setProperty('opacity', '0');
                        }
                    });
                }
                buttonAbrir.addEventListener('click', (e) => {
                    aberto = !aberto;
                    if (aberto) {
                        buttonAbrir.innerText = '-';
                        navSubbotoes.classList.add('mensagem_subbotoes_expandido');
                    }
                    else {
                        buttonAbrir.innerText = '+';
                        navSubbotoes.classList.remove('mensagem_subbotoes_expandido');
                    }
                    atualizaEstadosSubBotoes();
                });
                atualizaEstadosSubBotoes();
                navSubbotoes.appendChild(buttonAbrir);
            }
        }
        botaoConfirma.classList.add('botao_minimizado');
        if(botaoIniciarGravacaoAudio.classList.contains('botao_minimizado')){
            botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
        }
        if(iconeIniciarGravacaoAudio.classList.contains('fa-pulse')){
            iconeIniciarGravacaoAudio.classList.remove('fas');
            iconeIniciarGravacaoAudio.classList.remove('fa-spinner');
            iconeIniciarGravacaoAudio.classList.remove('fa-pulse');
            iconeIniciarGravacaoAudio.classList.add('fa-solid');
            iconeIniciarGravacaoAudio.classList.add('fa-microphone');
            botaoIniciarGravacaoAudio.removeAttribute('disable');
        }
        return p;
    }

    /**
     * Cria um anexo de link.
     * @param {HTMLParagraphElement} p
     * @param {MensagemAnexo} anexo
     * @param {boolean} card 
     */
    function criaAnexoLink(p, anexo, card) {
        const link = document.createElement('a');
        link.href = anexo.link;
        link.target = '_blank'
        link.classList.add('mensagem_anexo_link');
        link.addEventListener('click', (e) => {
            abreAnexoLink(anexo.link);
            e.preventDefault();
            e.stopPropagation();
        });
        if (card) {
            link.classList.add('mensagem_anexo_link_card');
            const titulo = document.createElement('p');
            const dataAtualizacao = document.createElement('sup')
            dataAtualizacao.innerText = (new Date(anexo.data)).toLocaleDateString('pt-BR', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
            dataAtualizacao.classList.add('mensagem_anexo_link_card_data')
            titulo.classList.add('mensagem_anexo_link_card_titulo');
            titulo.innerText = anexo.titulo.replace(/[\r\n]+/g, ' ');
            link.setAttribute('title', anexo.titulo.replace(/[\r\n]+/g, ' '));
            const descricao = document.createElement('sub');
            descricao.innerHTML = anexo.conteudo.replace(/[\r\n]+/g, ' ');
            descricao.classList.add('mensagem_anexo_link_descricao');
            const categoria = document.createElement('sup');
            categoria.classList.add('mensagem_anexo_link_categoria');
            switch (anexo.categoria) {
                case 'wpo_noticia':
                    categoria.innerText = 'Notícia';
                    break;
                case 'wpo_servico':
                    categoria.innerText = 'Serviço';
                    break;
                case 'wpo_pagina':
                    categoria.innerText = 'Página';
                    break;
                default:
                    categoria.innerText = 'Outros';
                    break;
            }
            link.append(dataAtualizacao, titulo, descricao, categoria);
        }
        else {
            link.innerText = anexo.conteudo;
            link.setAttribute('title', anexo.conteudo);
        }
        p.append(link);
    }

    /**
     * Cria um anexo para um download.
     * 
     * @param {HTMLParagraphElement} p
     * @param {MensagemAnexo} anexo
     */
    function criaAnexoDownload(p, anexo) {
        const chars = atob(anexo.dados)
        const data = new Array(chars.length);
        for (let i = 0; i < chars.length; i++) {
            data[i] = chars.charCodeAt(i);
        }
        dataArray = new Uint8Array(data);

        const blob = new Blob([dataArray], { type: anexo.mime });
        const container = document.createElement('div');
        container.classList.add('anexo_preview_container');
        container.setAttribute('tabindex', 0);
        const btnPreview = document.createElement('div');
        btnPreview.classList.add('anexo_preview_download');
        btnPreview.classList.add('fas');
        btnPreview.classList.add('fa-download');
        const labelPreview = document.createElement('span');
        labelPreview.classList.add('anexo_preview_label');
        const linkPreview = document.createElement('a');
        linkPreview.classList.add('anexo_preview_link');
        linkPreview.setAttribute('tabindex', -1);

        labelPreview.innerText = anexo.conteudo;

        linkPreview.href = URL.createObjectURL(blob);
        linkPreview.download = anexo.conteudo;
        linkPreview.innerText = 'Baixar';

        let podePreview = false;
        criaPreviewBlob(blob).then(url => {
            if (url) {
                podePreview = true;
                const imgPreview = document.createElement('img');
                imgPreview.classList.add('anexo_preview_preview');
                imgPreview.width = 256;
                imgPreview.height = 256;           
                imgPreview.src = url;
                container.appendChild(imgPreview);
                container.classList.add('anexo_preview_container_preview');
            }
        });

        container.append(btnPreview);
        container.append(labelPreview);
        container.append(linkPreview);
        container.addEventListener('keypress', (e) => {
            if (e.key == 'Enter') {
                linkPreview.click();
            }
        });
        container.addEventListener('click', (e) => {
            if (podePreview && e.target != btnPreview && e.target != linkPreview) {
                window.parent && window.parent.postMessage(['chatbot', status.id, 'abrir-anexo', {
                    blob
                }], '*');
            }
            else if (e.target != linkPreview) {
                linkPreview.click();
            }
            e.stopPropagation();
        });
        p.append(container);
    }

    async function criaPreviewBlob(blob) {
        const url = URL.createObjectURL(blob);
        let canvas = null;
        try {
            if (blob.type == 'application/pdf') {
                pdf = await pdfjsLib.getDocument({ url, worker: workerPdfJS }).promise;
                const page = await pdf.getPage(1);
                let scale;
                let viewport = page.getViewport({ scale: 1 });
                if (viewport.width > viewport.height) {
                    scale = 256 / viewport.height;
                }
                else {
                    scale = 256 / viewport.width;
                }
                viewport = page.getViewport({ scale });
                canvas = document.createElement('canvas');
                canvas.width = 256;
                canvas.height = 256;
                const ctx = canvas.getContext('2d');
                await page.render({
                    canvasContext: ctx,
                    viewport: viewport
                }).promise;
            }
            else if (/^image\//.test(blob.type)) {
                canvas = document.createElement('canvas');
                canvas.width = 256;
                canvas.height = 256;
                const ctx = canvas.getContext('2d');
                const img = await (new Promise(resolve => {
                    const imgTag = new Image();
                    imgTag.onload = () => { resolve(imgTag) };
                    imgTag.src = url;
                }));
                if (img.width > img.height) {
                    ctx.drawImage(img, 0, 0, (256 / img.height) * img.width, 256);
                }
                else {
                    ctx.drawImage(img, 0, 0, 256, (256 / img.width) * img.height);
                }
            }
        }
        catch (e) {
            console.error(e);
        }
        URL.revokeObjectURL(url);
        if (canvas) {
            return canvas.toDataURL();
        }
        return null;
    }

    /**
     * @type {FuncoesValidacao}
     */
    const funcoesValidacao = {
        validaData: (input) => {
            const data = new Date(input.value.split('/').reverse().join('-') + ' 00:00:00');
            const novaData = data.getDate().toString().padStart(2, 0) + '/' + (data.getMonth() + 1).toString().padStart(2, 0) + '/' + data.getFullYear();
            if (input.value == novaData) {
                input.setCustomValidity('');
            }
            else {
                input.setCustomValidity('A data informada é inválida.');
            }
        },
        validaDataHora: (input) => {
            const data = new Date(input.value.split('/').reverse().join('-').split(' ').reverse().join(' '));
            const novaData = data.getDate().toString().padStart(2, 0) + '/' + (data.getMonth() + 1).toString().padStart(2, 0) + '/' + data.getFullYear() + ' ' +
                data.getHours().toString().padStart(2, 0) + ':' + data.getMinutes().toString().padStart(2, 0) + ':' + data.getSeconds().toString().padStart(2, 0);
            if (input.value == novaData) {
                input.setCustomValidity('');
            }
            else {
                input.setCustomValidity('A data informada é inválida.');
            }
        },
        validaAno: (input) => {
            const ANO_MINIMO = 1800,
                ANO_MAXIMO = 2200;
            const iAnoInformado = parseInt(input.value);
            if ((String(iAnoInformado).length != 4) || (iAnoInformado < ANO_MINIMO || iAnoInformado > ANO_MAXIMO)) {
                return input.setCustomValidity('O Ano informado é inválido');
            }
            input.setCustomValidity('')
        }
    };

    /**
     * Cria anexo de campo.
     * @param {HTMLFieldSetElement} fieldset
     * @param {MensagemAnexo} anexo
     */
    function criaAnexoCampo(fieldset, anexo) {
        const id = 'input_' + crypto.randomUUID();
        const label = document.createElement('label');
        label.innerText = anexo.conteudo;
        label.setAttribute('for', id);
        label.classList.add('mensagem_form_label');
        const input = document.createElement('input');
        input.id = id;
        input.name = id;
        input.type = 'text';
        input.required = true
        input.classList.add('mensagem_form_input');
        let titulo = anexo.formato == 'numeric' ? 'Informe números' : 'Informe um texto';
        if (anexo.formato) {
            input.inputmode = anexo.formato;
        }

        if (anexo.formatoCampo == 'numeric') { // Mascara para númerico
            input.oninput = () => input.value = input.value.replace(/[^0-9.,]/g, '');
        }

        if (anexo.mascara) {
            input.placeholder = anexo.mascara.join(' ou ');
            criaMascara(input, anexo.mascara);
        }
        if (anexo.validaPadrao) {
            input.pattern = anexo.validaPadrao;
            if (anexo.mascara) {
                titulo += ' no formato ' + input.placeholder;
            }
        }
        if (anexo.validaFuncao && funcoesValidacao[anexo.validaFuncao]) {
            input.addEventListener('input', () => { funcoesValidacao[anexo.validaFuncao](input); })
        }
        input.title = titulo + '.';
        if (anexo.autocomplete) {
            input.autocomplete = anexo.autocomplete;
        }
        fieldset.append(label);
        fieldset.append(input);
    }

    /**
     * Cria a mascara para o input.
     * @param {HTMLInputElement} input 
     * @param {string[]} mascara 
     */
    function criaMascara(input, mascara) {
        input.addEventListener('input', () => {
            const valInput = input.value;
            const vals = mascara.map(() => []);
            const idxs = mascara.map(() => 0);
            const validos = mascara.map(() => 0);
            function processaVal(e) {
                const matchesI = mascara.map((e, i) => e[idxs[i]]);
                function processaMatch(match, idxMascara) {
                    if (!match) {
                        return;
                    }
                    switch (match) {
                        case '9':
                            if (!/[0-9]/.test(e)) {
                                return;
                            }
                            idxs[idxMascara]++;
                            vals[idxMascara].push(e);
                            validos[idxMascara]++;
                            return;
                        case 'Z':
                            if (!/[a-zA-Z]/.test(e)) {
                                return;
                            }
                            idxs[idxMascara]++;
                            vals[idxMascara].push(e);
                            validos[idxMascara]++;
                            return;
                        case 'X':
                            idxs[idxMascara]++;
                            vals[idxMascara].push(e);
                            validos[idxMascara]++;
                            return;
                    }
                    idxs[idxMascara]++;
                    vals[idxMascara].push(match);
                    processaMatch(mascara[idxMascara][idxs[idxMascara]], idxMascara);
                }
                matchesI.forEach((match, idx) => processaMatch(match, idx));
            }
            valInput.split('').forEach(processaVal);
            let idx = 0;
            validos.forEach((e, i) => {
                if (e > validos[idx]) {
                    idx = i;
                }
            });
            input.value = vals[idx].join('');
        });
    }

    /**
     * Cria anexo de botão.
     * @param {MensagemAnexo} anexo
     */
    function criaAnexoBotoes(anexo) {
        const botao = document.createElement('button');
        botao.classList.add('mensagem_botao');
        botao.classList.add('mensagem_botao_' + anexo.tipo);
        botao.innerText = anexo.conteudo;
        botao.title = anexo.conteudo;
        botao.addEventListener('click', (e) => {
            switch (anexo.tipo) {
                case 'opcao':
                    botao.classList.add('mensagem_botao_selecionado');
                    if (!enviaMensagem(anexo.conteudo)) {
                        botao.classList.remove('mensagem_botao_selecionado');
                    }
                    break;
                case 'botao':
                    switch (anexo.acao) {
                        case 'link':
                            abreAnexoLink(anexo.link);
                            break;
                        default:
                            enviaMensagem(anexo.conteudo);
                            break;
                    }
                    break;
            }
        });
        if (anexo.tipo == 'botao' && anexo.acao == 'link') {
            const icone = document.createElement('i');
            icone.classList.add('fa-solid');
            icone.classList.add('fa-external-link');
            botao.append(icone);
        }
        return botao;
    }

    /**
     * Abre um anexo de link.
     */
    function abreAnexoLink(link) {
        if (link && /^data:[^;,]+;base64,/.test(link)) {
            const data = atob(link.split(',').slice(1).join(','));
            const bytes = new Array(data.length)
            for (i = 0; i < data.length; i++) {
                bytes[i] = data.charCodeAt(i);
            }
            window.open(
                URL.createObjectURL(
                    new Blob([new Uint8Array(bytes)], { type: link.split(':').slice(1).join(':').split(';').slice(0, 1).join(';') })
                )
            );
        }
        else {
            window.open(link, '_blank');
        }
    }

    function getTempo() {
        const promise = new Promise((resolve) => {
            __callbackTempo.push(resolve);
            status.client.emit('time');
        })
        return promise;
    }

    function getConfiguracoes(sIdentificadorConversa){
        fetch(location.origin + location.pathname.replace(/\/[^\/]*$/, '') + '/configuracao/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({idConversa: sIdentificadorConversa})
            
        }).then(response => response.json())
          .then(data => {
                Object.entries(data.data).map(([prop, valor]) => {
                    switch (prop) {
                        case 'urlImagemBot':
                            status.imagemBot = valor;
                            if (status.imagemBot) {
                                $('#base > .area_cabecalho > .imagem_chatbot > .imagem_bot').remove();
                                const img = document.createElement('img');
                                img.classList.add('imagem_bot');
                                img.src = status.imagemBot;
                                img.ariaLabel = 'Imagem do Assistente Virtual'
                                iconeBot.append(img);
                                iconeBot.classList.remove('fa-solid');
                            }
                            else {
                                iconeBot.firstChild && icone.firstChild.remove();
                                iconeBot.classList.add('fa-solid');
                            }
                            break;
                        case 'nomeBot':
                            status.nomeBot = valor;
                            $('#nome_assistente').innerText = valor ? ' - ' + valor : '';
                            break;
                        case 'corDestaque':
                            document.body.style.setProperty('--cor-destaque', valor || '');
                            document.body.style.setProperty('--cor-destaque-transparente', valor ? valor + '99' : '');
                            break;
                        case 'utilizaMensagemInicializacao':
                            bMostraMensagemInicializacao = valor;
                            break;
                        case 'mensagemInicializacao':
                            if (bMostraMensagemInicializacao && !isContextoAtendenet()) {
                                iniciaMensagemInicializacao(valor);
                            }
                            break;
                        case 'isDesenvolvimento':
                            isDesenvolvimento = valor;
                           break;
                        case 'contexto':
                            sContexto = valor;
                            break;
                    }
                })
        })
        .catch(error => console.error('Erro ao buscar dados:', error));
    }

    /**
     * Inicia o cliente do WS.
     */
    function iniciaCliente() {
        if (status.token) {
            iniciado = true;
            // Monta a conexão com o socket.io.
            status.client = io('wss://' + location.host + location.pathname.replace(/\/[^\/]*$/, '') + '/chat/', {
                path: location.pathname.replace(/\/[^\/]*$/, '') + '/chat/',
                transports: ['websocket'],
                query: { token: status.token }
            });
            // Ouvintes:
            status.client
            .on('connect', () => {
                areaMensagens.innerHTML = '';
                areaMensagens.append(navSubbotoes);
                areaAlerta.innerHTML = '';
                areaAlerta.classList.remove('area_alerta_visivel');
                if (!status.iniciado) {
                    status.aceitouTermos = true;
                    status.permiteDigitar = status._permiteDigitar;
                    aceiteTermosUso.remove();
                    areaMensagens.classList.remove('termos_uso_visivel');
                }
                else {
                    status.permiteDigitar = false;
                }
            })
            .on('conteudotermos', (conteudo) => {
                if (!conteudo) {
                    conteudo = 'Houve um erro ao carregar os termos de uso. Tente novamente mais tarde...';
                }
                linkUsoRodape.setAttribute('href', '#');
                conteudoTermosUso.innerHTML = conteudo;
                const botaoVoltar = document.createElement('button');
                botaoVoltar.classList.add('fas');
                botaoVoltar.classList.add('fa-arrow-left');
                botaoVoltar.classList.add('aceite_termos_uso_conteudo_voltar');
                botaoVoltar.title = 'Voltar';
                botaoVoltar.addEventListener('click', (e) => {
                    conteudoTermosUso.style.display = 'none';
                });
                conteudoTermosUso.append(botaoVoltar);
                linkUsoRodape.addEventListener('click', (e) => {
                    conteudoTermosUso.style.display = '';
                    e.preventDefault();
                    return false;
                });
                document.querySelectorAll('a', conteudoTermosUso).forEach(e => e.target = '_blank')
            })
            .on('time', (t) => {
                __callbackTempo.forEach(e => {
                    e(t);
                });
                __callbackTempo = [];
            }).on('disconnect', (e) => {
                console.error(e);
                exibeAlerta('Você foi Desconectado');
                status.permiteDigitar = false;
                campoEstadoInicial();
            }).on('connect_error', (ex) => {
                console.error(ex);
                if (ex.message && ex.message.startsWith && ex.message.startsWith('IPM-ERROR')) {
                    exibeAlerta(ex.message.replace('IPM-ERROR: ', ''));
                }
                else {
                    exibeAlerta('Erro na conexão com o servidor.');
                }
                campoEstadoInicial();
                status.permiteDigitar = false;
            })
            .on('ipmmessage', recebeMensagem)
            .on('reconhecimentovoz', processaReconhecimentoVoz);
        }
        else {
            exibeAlerta('Falha no carregamento (Token de autenticação inválido).');
        }
    }

    function campoEstadoInicial() {
        areaDigitacao.removeAttribute('disabled');
        botaoIniciarGravacaoAudio.removeAttribute('disable');
        
        if (areaDigitacao.classList.contains('processando_audio')){
            areaDigitacao.classList.remove('processando_audio');
        }
        areaDigitacao.setAttribute('placeholder', areaDigitacao.getAttribute('data-placeholder'));
        
        if (iconeIniciarGravacaoAudio.classList.contains('fa-spinner')) {
            iconeIniciarGravacaoAudio.classList.remove('fas');
            iconeIniciarGravacaoAudio.classList.remove('fa-spinner');
            iconeIniciarGravacaoAudio.classList.remove('fa-pulse');
            iconeIniciarGravacaoAudio.classList.add('fa-solid');
            iconeIniciarGravacaoAudio.classList.add('fa-microphone');
        }


        if(areaDigitacao.value.length == 0) {
            botaoConfirma.classList.add('botao_minimizado');
            if(botaoIniciarGravacaoAudio.classList.contains('botao_minimizado')){
                botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
            }
        }
        else {
            areaDigitacao.removeAttribute('disabled');
            botaoIniciarGravacaoAudio.classList.add('botao_minimizado');
            if(botaoConfirma.classList.contains('botao_minimizado')){
                botaoConfirma.classList.remove('botao_minimizado');    
            }
        }
    }

    /**
     * Recebe a mensagem do chatbot e mostra ao usuário.
     * 
     * @param {Mensagem} mensagem 
     */
    const recebeMensagem = (mensagem) => {
        if (mensagem.error) {
            exibeAlerta(mensagem.error);
            status.ultimaMensagem.forEach(mensagem => {
                mensagem.classList.add('mensagem_erro');
                mensagem.parentElement.classList.add('base_mensagem_erro');
                mensagem.addEventListener('click', (e) => {
                    e.target.__conteudo_mensagem && enviaMensagem(e.target.__conteudo_mensagem);
                });
                if (mensagem) {
                    var bBoxDiv = mensagem.parentElement.getBoundingClientRect();
                    var bBoxArea = areaMensagens.getBoundingClientRect();
                    areaMensagens.scrollTop = areaMensagens.scrollTop + bBoxDiv.y + bBoxDiv.height + 100 - bBoxArea.y - bBoxArea.height;
                }
            });
        }
        else {
            adicionaMensagem(mensagem.autor, mensagem.conteudo, mensagem.anexos, mensagem.tempo);
            areaAlerta.innerHTML = '';
            areaAlerta.classList.remove('area_alerta_visivel');
        }
        if (mensagem.parcial || mensagem.autor == 'usuario') {
            status.permiteDigitar = false;
        }
        else {
            status.permiteDigitar = true;
            botaoConfirma.classList.add('botao_minimizado');
            if(botaoIniciarGravacaoAudio.classList.contains('botao_minimizado')){
                botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
            }
        }
    }

    const processaReconhecimentoVoz = (oRetorno) => {
        campoEstadoInicial();

        //Verifica o retorno
        if (oRetorno.tipo == 'sucesso') {
            areaDigitacao.value += oRetorno.conteudo;
            areaDigitacao.focus();
            updateAlturaAreaDigitacao();
            areaDigitacao.removeAttribute('disabled');

            setTimeout(() => {
                botaoIniciarGravacaoAudio.classList.add('botao_minimizado');
                if(botaoConfirma.classList.contains('botao_minimizado')){
                    botaoConfirma.classList.remove('botao_minimizado');    
                }
            }, 200);
        }
        else {
            exibeAlerta(oRetorno.conteudo);
        }
    }

    /**
     * Limpa todos os arquivos anexados da DOM e do estado de gerenciamento.
     */
    const limpaArquivosAnexados = () => removeArquivoAnexo(...status.arquivosAnexados)

    /**
     * Remove um ou mais arquivos de anexo da DOM e do estado de gerenciamento.
     * 
     * @param {File[]} arquivos 
     */
    const removeArquivoAnexo = (...arquivos) => {
        const idArquivos = arquivos.map(arq => arq.id);
        status.arquivosAnexados = status.arquivosAnexados.filter(arquivoAnexado => !idArquivos.includes(arquivoAnexado.id));
        Array.from(areaListaArquivosAnexados.childNodes).forEach(arquivoAnexado => {
            if (idArquivos.includes(arquivoAnexado.id)) {
                areaListaArquivosAnexados.removeChild(arquivoAnexado)
            }
        })
        atualizaAreaVisualizacaoArquivosAnexados();
    }

    /**
     * Atualiza a area de visualização dos arquivos anexados.
     */
    const atualizaAreaVisualizacaoArquivosAnexados = () => {
        const arquivos = Array.from(status.arquivosAnexados)
        const qtd = arquivos.length;
        if (qtd == 0) {
            return areaVisualizacaoArquivos.style.display = 'none';
        }
        areaVisualizacaoArquivos.style.display = 'flex';
        areaInfoArquivosAnexados.querySelector('p').innerText = (qtd > 1 ? `${qtd} arquivos anexados` : '1 arquivo anexado');
        areaMensagens.scrollTop = areaMensagens.scrollHeight + areaVisualizacaoArquivos.clientHeight
    }

    /**
     * Adiciona um ou mais arquivos de anexo na DOM e ao estado de gerenciamento.
     * 
     * @param {File[]} arquivos 
     */
    const addArquivoAnexo = (...arquivos) => {
        status.arquivosAnexados.push(...arquivos)
        areaListaArquivosAnexados.append(...Array.from(arquivos).map(arquivo => {
            arquivo.id = crypto.randomUUID()
            const arquivoAnexo = document.createElement('span')
            const btnRemove = document.createElement('button')
            const nomeArquivo = document.createElement('h6');
            nomeArquivo.innerText = arquivo.name
            arquivoAnexo.title = arquivo.name
            arquivoAnexo.id = arquivo.id;
            arquivoAnexo.classList.add('arquivo_anexado');
            arquivoAnexo.innerHTML = '<i class="fas fa-file-import"></i>'
            btnRemove.innerHTML = '<i class="fas fa-times"></i>'
            btnRemove.title = 'Remover arquivo anexado';
            btnRemove.onclick = () => removeArquivoAnexo(arquivo)
            arquivoAnexo.append(nomeArquivo, btnRemove)
            return arquivoAnexo
        }))
        areaDigitacao.focus();
        atualizaAreaVisualizacaoArquivosAnexados()
    }

    /**
     * Hook para ouvintes de eventos multiplos.
     * 
     * @param {HTMLElement} el 
     * @param {function} handler 
     * @param  {(keyof HTMLElementEventMap)[]} events 
     */
    const useMultipleEventsListeners = (el, handler, ...events) => {
        events.forEach(ev => el.addEventListener(ev, handler))
    }

    const escondeComponenteGravacao = ()=> {        
        areaDigitacao.classList.remove('gravando');
        botaoIniciarGravacaoAudio.classList.remove('botao_minimizado');
        botaoIniciarGravacaoAudio.setAttribute('disable', '');
        containerGravarAudio.style.display = 'none';
        clearInterval(tempoGravacaoAudio);
        tempoGravacaoAudio = null;
    }

    /**
     * Inicia a classe responsável pela gravação de áudio juntamente com suas estilizações
     */
    const iniciarGravacao = ()=> {
        let onstart = () => {
            areaDigitacao.setAttribute('disabled', '');
            areaDigitacao.classList.add('gravando');
            botaoIniciarGravacaoAudio.classList.add('botao_minimizado');
            containerGravarAudio.style.display = '';    

            iniciaContador();
        }

        let onerror = () => {
            let oBotaoConfirmar = $(".modal_confirmar");
            oBotaoConfirmar.style.display = 'none';
            let oBotaoRejeitar  = $(".modal_rejeitar");
            oBotaoRejeitar.style.display = 'none';
            let oBotaoOk        = $(".modal_aceite");
            oBotaoOk.style.display = '';

            exibeAlertaConfirma('Verifique se o microfone está instalado corretamente e foi concedido acesso a ele pelo navegador.').then((confirma) => {
                oBotaoConfirmar.style.display = '';
                oBotaoRejeitar.style.display = '';
                oBotaoOk.style.display = 'none';
            });
            
            escondeComponenteGravacao();
            campoEstadoInicial();
        }

        let onend = (e) => {
            if (bUsaIaVoz || isDesenvolvimento) {
                if(areaDigitacao.classList.contains('gravando')) {
                    areaDigitacao.setAttribute('disabled', '');
                    areaDigitacao.classList.add('processando_audio');
                    
                    areaDigitacao.setAttribute('placeholder', 'Processando áudio...');
                    areaDigitacao.setAttribute('data-placeholder', 'Digite aqui para responder...');
    
                    iconeIniciarGravacaoAudio.classList.remove('fa-solid');
                    iconeIniciarGravacaoAudio.classList.remove('fa-microphone');
                    iconeIniciarGravacaoAudio.classList.add('fas');
                    iconeIniciarGravacaoAudio.classList.add('fa-spinner');
                    iconeIniciarGravacaoAudio.classList.add('fa-pulse');

                    escondeComponenteGravacao();
                }
            }
         else {
            campoEstadoInicial();
            escondeComponenteGravacao();
         }   
        }
        
        let onresult = async (xAudio) => {
            if (bUsaIaVoz || isDesenvolvimento) {
                async function lerArquivo(arquivo) {
                    const reader = new FileReader();
                    return new Promise((resolve) => {
                        reader.onload = (event) => {
                            const base64Content = event.target.result.split(',')[1];
                            resolve(base64Content);
                        };
                        reader.readAsDataURL(arquivo);
                    });
                }
                
                let conteudoArquivoBase64 = await lerArquivo(xAudio);
                compactarBase64(conteudoArquivoBase64).then(audioComprimido => {
                    status.client.emit('reconhecimentovoz', audioComprimido.split(',')[1]);
                });
            }
            else {
                processaReconhecimentoVoz({conteudo: xAudio, tipo: 'sucesso'});
            }
        }

        reconhecimentoVoz = bUsaIaVoz || isDesenvolvimento ? new ReconhecimentoVozInterno() : new ReconhecimentoVozNativo();
        reconhecimentoVoz.setEventoOnStart(onstart);
        reconhecimentoVoz.setEventoOnResult(onresult);
        reconhecimentoVoz.setEventoOnEnd(onend);
        reconhecimentoVoz.setEventoOnError(onerror);
        reconhecimentoVoz.iniciar();

        botaoExcluirAudio.addEventListener('click', () => {
            reconhecimentoVoz.abortar();
            campoEstadoInicial();
        })

        botaoEnviarAudioGravado.addEventListener('click', () => {
            reconhecimentoVoz.parar();
        });
    }
    
    /**
     * Inicia o timer da gravação de áudio
     */
    const iniciaContador = ()=> {
        let iSegundos = 0;
        containerTempoGravacao.textContent = '0:00';
        tempoGravacaoAudio = setInterval(() => {
            //Limita o áudio a 15 segundos
            if (iSegundos < 14) {
                iSegundos++;
                containerTempoGravacao.textContent = atualizaTempoGravacao(iSegundos);
            }
            else {
                exibeAlerta('O limite de 15 segundos para gravação de áudio foi atingido', 'aviso', 5000);
                clearInterval(tempoGravacaoAudio);
                tempoGravacaoAudio = null;
                botaoEnviarAudioGravado.click();
            }

        }, 1000);
    }

    /**
     * Atualiza em segundos o tempo da gravação de áudio
     */
    const atualizaTempoGravacao = (iTempo) => {
        const iMinutos  = Math.floor(iTempo / 60);
        const iSegundos = iTempo % 60;
        return `${iMinutos}:${iSegundos < 10 ? '0' : ''}${iSegundos}`;
    }

    /**
     * Compactar o base64
     * @param {string} base64String 
     * @returns 
     */
    const compactarBase64 = async (base64String) => {
        const uint8Array = base64ParaUint8Array(base64String);
        const compressedBlob = await compactarDado(uint8Array);
        const compressedBase64 = await converteBlobParaBase64(compressedBlob);
    
        return compressedBase64;
    }
    
    /**
     * Converte o Blob em Base64
     */
    const converteBlobParaBase64 = async (blob) => {
        const reader = new FileReader();
        return new Promise((resolve, reject) => {
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }

    /**
     * Compacta o blob
     */
    const compactarDado = async (data) => {
        const cs = new CompressionStream('gzip');
        const compressedStream = new Blob([data]).stream().pipeThrough(cs);
        const compressedBlob = await new Response(compressedStream).blob();
    
        return compressedBlob;
    }
    
    /**
     * Converte o base64 para Uint8Array
     */
    const base64ParaUint8Array = (base64) => {
        const binaryString = atob(base64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
    
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
    
        return bytes;
    }

    const iniciaMensagemInicializacao = (sMensagem) => {
        let iIndex = 0;
        
        //Deixa a mensagem de inicialização visível
        containerMensagemInicializacao.classList.add('hover');
        
        //Para obter a altura do container da mensagem | E seta a mensagem temporariamente
        containerMensagemInicializacao.style.opacity = '0';
        mensagemInicializacao.innerHTML = sMensagem; 
        let sHeight = getComputedStyle(containerMensagemInicializacao).getPropertyValue('height');
        
        let iTamanhoContainer = parseInt(sHeight) + 85;
        mostraMensagemInicializacao(iTamanhoContainer);

        mensagemInicializacao.innerHTML = '';
        containerMensagemInicializacao.style.opacity = '';
        containerMensagemInicializacao.style.height = sHeight;
        let iValorDiferenca = -26.444;
        containerMensagemInicializacao.style.top = (-Math.abs(parseInt(sHeight)) + iValorDiferenca) + "px";
        
        //Seta o evento de click para esconder a mensagem de iniciaização, antes que ela finalize de escrever
        containerMensagemInicializacao.addEventListener('click', () =>{
            escondeMensagemInicializacao();
        });
        //Seta o evento de click para esconder a mensagem de iniciaização, antes que ela finalize de escrever
        mensagemInicializacao.addEventListener('click', () =>{
            escondeMensagemInicializacao();
        });

        //Seta os eventos para mostrar a mensagem
        areaCabecalhoMinimizado.addEventListener('mouseenter', ()=> {
            if (containerBaseMinimizado.classList.contains('minimizado')) {
                mostraMensagemInicializacao(iTamanhoContainer);
            }
        });
        areaCabecalhoMinimizado.addEventListener('mouseleave', ()=> {
            if (containerBaseMinimizado.classList.contains('minimizado')) {
                escondeMensagemInicializacao();
            }
        });
        
        //Escreve a mensagem configurada no balão
        function escrever() {
            if (iIndex < sMensagem.length) {
                mensagemInicializacao.innerHTML = sMensagem.slice(0, iIndex) + `<span class="cursor-blink">|</span>`;
                iIndex++;
                setTimeout(escrever, Math.random() * 57);
            }
            else { 
                mensagemInicializacao.innerHTML = sMensagem.slice(0, iIndex);
                containerMensagemInicializacao.classList.remove('cursor-blink');

                setTimeout(() => {
                    if (containerBaseMinimizado.classList.contains('minimizado')) {
                        escondeMensagemInicializacao();
                    }
                }, 8000);
            }
        }
        escrever();
    }

    /**
     * Esconde a mensagem de inicialização e envia para o front Atende.net para readequar o tamanho do container
     */
    const escondeMensagemInicializacao = () => {
        containerMensagemInicializacao.classList.remove('hover');
        window.parent && window.parent.postMessage(['chatbot', status.id, 'esconde-mensagem-inicializacao'], '*');
    }

    /**
     * Mostra a mensagem de inicialização e envia para o front Atende.net para readequar o tamanho do container
     */
    const mostraMensagemInicializacao = (iTamanhoContainer) => {
        containerMensagemInicializacao.classList.add('hover');
        window.parent && window.parent.postMessage(['chatbot', status.id, 'mostra-mensagem-inicializacao', iTamanhoContainer], '*');
    }

    const isContextoAtendenet = () => {
        return sContexto === 'ATENDENET';
    }
    
    window.onload = () => {
        containerBase                  = $('#base');
        containerBaseMinimizado        = $('#base.minimizado');
        areaMensagens                  = $('#base > .area_mensagens > .mensagens');
        areaVisualizacaoArquivos       = $("#base > #area_visualizacao_arquivos");
        areaDropArquivos               = $("#base > #area_drop_arquivos");
        areaDigitacao                  = $('#base > .area_digitacao');
        areaAlerta                     = $('#base > .area_alertas');
        areaCabecalho                  = $('#base > .area_cabecalho');
        botaoConfirma                  = $('#base > .botao_enviar');
        botaoIniciarGravacaoAudio      = $('#base > .botao_gravar');
        botaoEnviarAudioGravado        = $('#base > .container_gravar_audio > .botao_enviar_audio');
        iconeIniciarGravacaoAudio      = $('#base > .botao_gravar i');
        botaoExcluirAudio              = $('#base > .container_gravar_audio > .botao_excluir');
        containerGravarAudio           = $('#base > #container_gravar_audio');
        containerTempoGravacao         = $('#base > #container_gravar_audio > #contador_tempo');
        campoEnviarArquivos            = $('#base > #anexar_arquivos');
        botaoMinimizar                 = $('#base > .area_cabecalho > .botao_minimizar');
        botaoFechar                    = $('#base > .area_cabecalho > .botao_fechar');
        iconeBot                       = $('#base > .area_cabecalho > .imagem_chatbot');
        containerMensagemInicializacao = $('#mensagem_inicial');
        mensagemInicializacao          = $('#mensagem_inicial > #info-type > .texto');
        areaCabecalhoMinimizado        = $('#base > .area_cabecalho.cabecalho_chatbot_minimizado > .botao_minimizar');
        modal                          = $('#modal');
        aceiteTermosUso                = $('#termos_uso');
        containerRodape                = $('footer.rodape_base');
        linkTermosUso                  = $('#link_termos_uso')
        linkUsoRodape                  = $('#rodape_termos_uso');
        conteudoTermosUso              = $('#base > .aceite_termos_uso_conteudo');
        navSubbotoes                   = $('#base > .area_mensagens > .mensagens > .mensagem_subbotoes');
        loader                         = $('#base > .bloqueio_carregamento');
        areaListaArquivosAnexados      = areaVisualizacaoArquivos.querySelector('#area_listagem_arquivos');
        areaInfoArquivosAnexados       = areaVisualizacaoArquivos.querySelector('#area_informacao_arquivos');

        if (navigator.vendor && navigator.vendor.indexOf && navigator.vendor && navigator.vendor.indexOf('Apple') > -1) {
            containerBase.classList.add('safari');
        }

        pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
        workerPdfJS = new pdfjsLib.PDFWorker();

        iniciaEventos();

        window.addEventListener('message', (event) => {
            const [ sEvento, sId, props ] = event.data;
            const dominiosValidos = [/ipm\.com\.br/, /atende\.net$/, /\.nfs-e\.net$/];
            const dominio = event.origin.split('/')[2];
            if (dominio && dominiosValidos.some(valido => valido.test(dominio))) {
                switch (sEvento) {
                    case 'INIT':
                        areaDigitacao.placeholder = 'Inicializando...';
                        const match = (location.search || '').match(/token=([^&]+)/);
                        status.token = (match && match[1]) || '';
                        status.id = sId
                        if (props) {
                            Object.entries(props).forEach(([prop, valor]) => {
                                switch (prop) {
                                    case 'estilos':
                                        const style = document.createElement('style');
                                        style.innerText = valor || '';
                                        document.body.append(style);
                                    break;
                                    case 'idConversa':
                                        getConfiguracoes(valor);
                                    break;
                                }
                            })
                        }
                    break;            
                    case 'FOCUS':
                        areaDigitacao.focus();
                        break;
                }
            }
            else {
                console.error('Domínio não permitido: ' + dominio);
            }
        });

        {
            const canvas = document.getElementById('aceite_termos_uso_particulas');
            canvas.height = 100;
            canvas.width = 500;
            const ctx = canvas.getContext('2d');
            ctx.aOnRedraw = [];
            ctx.imageSmoothingEnabled = false;

            const atualizaCanvas = function () {
                const fillStyle = document.body.style.getPropertyValue('--cor-destaque');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                for (var iFn in ctx.aOnRedraw) {
                    ctx.beginPath();
                    ctx.fillStyle = fillStyle;
                    ctx.aOnRedraw[iFn].call();
                    ctx.closePath();
                }
                setTimeout(atualizaCanvas, 33);
            }

            const fnRedrawQuadrado = function (i, x, y, ang, tam) {
                ctx.fillStyle = ctx.fillStyle + parseInt(Math.max(0, canvas.height - y)).toString(16).padStart(2, 0);

                ctx.translate(x, canvas.height - y + tam / 2);
                ctx.rotate((ang * Math.PI) / 180);
                ctx.translate(-x, -(canvas.height - y + tam / 2));

                ctx.fillRect(x - tam / 2, canvas.height - y, tam, tam);

                ctx.setTransform(1, 0, 0, 1, 0, 0)
            }
            const desenhaQuadrado = function (i, x, tam, mod) {
                let y = Math.random() * canvas.height;
                let ang = Math.random() * 90;
                ctx.aOnRedraw.push(function () {
                    y = y < 100 + tam ? y + 0.25 * mod : 0;
                    ang = ang < 90 ? ang + mod : 0;
                    fnRedrawQuadrado(i, x, y, ang, tam);
                });
            }

            for (var i = 0; i < 50; i++) {
                desenhaQuadrado(i, i * (canvas.width / 50) + (canvas.width / 100), Math.random() * 7 + 3, Math.random() + 0.5);
            }

            atualizaCanvas();
        }
    }
})(document.querySelector.bind(document));