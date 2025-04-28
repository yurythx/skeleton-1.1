/*!
 * Recurso de transcrição para interpretação do recurso de fala
 *
 * IPM Sistemas (C) - Atende.net (C) - 2024
 * https://www.ipm.com.br/
 * Direitos Reservados
 * ESTE CÓDIGO FONTE E QUALQUER DOCUMENTAÇÃO QUE O ACOMPANHE SÃO PROTEGIDOS PELA LEI DE DIREITOS AUTORAIS INTERNACIONAIS
 * E NÃO PODE SER REVENDIDO OU REDISTRIBUÍDO. A REPRODUÇÃO OU DISTRIBUIÇÃO NÃO AUTORIZADA ESTÁ SUJEITA A PENALIDADES CIVIS E PENAIS.
 *//**
 * Recurso de Reconhecimento de voz para interpretação do recurso de fala
 */
 var ReconhecimentoVozNativo = function() {
    this.SpeechToTexto = window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.speechApi     = null;
    this.onerror       = null;
    this.onstart       = null;
    this.onend        = null;
    this.onresult      = null;

    /**
     * Inicia o reconhecimento e transcrição da voz
     */
    this.iniciar = ()=> {
        this.speechApi = new window.SpeechRecognition();
        this.speechApi.continuous     = true;   
        this.speechApi.interimResults = false;
        this.speechApi.lang           = 'pt-BR'; 

        this.speechApi.start();

        this.speechApi.onstart = (e) => {
            if (this.onstart){
                this.onstart(e);
            }
        }

        this.speechApi.onend = (e) => {
            if (this.onend) {
                this.onend(e);
            }
        }

        this.speechApi.onerror = (e) => {
            if (this.onerror) {
                this.onerror(e);
            }
        }

        this.speechApi.onresult = (e) => {
            if (this.onresult) {
                this.onresult(e);
            }
        }
    }
    
    /**
     * Para o reconhecimento de voz
     */
    this.parar = ()=> {
        this.speechApi.stop();
    }

    /**
     * 
     * @param {function} oEvento 
     */
    this.setEventoOnStart = (oEvento)=> {
        this.onstart = (e)=> {
            oEvento(e);
        }
    }

    this.setEventoOnEnd = (oEvento)=> {
        this.onend = (e) => {
            oEvento(e);
        }
    }

    this.setEventoOnError = (oVento)=> {
        this.onerror = (e) => {
            oVento(e);
        }
    }

    this.setEventoOnResult = (oEvento) => {
        this.onresult = (e)=> {
            oEvento(e.results[e.resultIndex][0].transcript);
        }
    }
    
    this.abortar = ()=> {
        this.parar();
    }
}

var ReconhecimentoVozInterno = function () {
    this.parteGravacao = [];
    this.emGravacao    = false;
    this.mediaRecorder = null;
    this.onerror       = null;
    this.onstart       = null;
    this.onstop        = null;
    this.onresult      = null;
    this.wavBlov     = null;

    this.iniciar = async () => {
        try {
            if (this.emGravacao) {
                console.warn('Já está gravando.');
                return;
            }

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

            this.mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    this.parteGravacao.push(event.data);
                }
            };

            this.mediaRecorder.onstop = async () => {
                const blob = new Blob(this.parteGravacao, { type: 'audio/webm' });
                const arrayBuffer = await blob.arrayBuffer();
                const audioContext = new AudioContext();
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

                const wavBlob = criaBlobWav(audioBuffer);
                this.wavBlov = wavBlob;
                
                if (this.onresult) {
                    this.onresult(this.wavBlov);
                }

                // Limpa o array de partes após parar a gravação
                this.parteGravacao = [];
                this.emGravacao = false;
            };

            this.mediaRecorder.start();
            this.emGravacao = true;

            if (this.onstart) {
                this.onstart();
            }
        } catch(e) {
            if (this.onerror) {
                this.onerror();
            }
        }
    }

    this.abortar = ()=> {
        if (this.mediaRecorder && this.emGravacao) {
            this.mediaRecorder.onstop = null;
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.mediaRecorder.stop();
            
            if (this.onstop) {
                this.onstop();
            }
        }
    }

    this.parar = ()=> {
        if(this.mediaRecorder){
            this.mediaRecorder.stop();
            if (this.onstop) {
                this.onstop();
            }
        }
    }

    this.setEventoOnStart = (oEvento)=> {
        this.onstart = (e)=> {
            oEvento(e);
        }
    }

    this.setEventoOnEnd = (oEvento)=> {
        this.onstop = (e)=> {
            oEvento(e);
        }
    }

    this.setEventoOnResult = (oEvento) => {
        this.onresult = (e)=> {
            oEvento(e);
        }
    }

    this.setEventoOnError = (oEvento)=> {
        this.onerror = (e)=> {
            oEvento(e);
        }
    }
}

/**
 * Cria um Blob de áudio no formato WAV a partir de um AudioBuffer.
 * 
 * @param {AudioBuffer} audioBuffer - O buffer de áudio que será convertido para WAV.
 * @returns {Blob} - O Blob resultante com o tipo MIME 'audio/wav'.
 */
 function criaBlobWav(audioBuffer) {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const bitsPerSample = 16;
    const bytesPerSample = bitsPerSample / 8;
    const byteRate = sampleRate * numChannels * bytesPerSample;
    const length = audioBuffer.length * numChannels * bytesPerSample;

    const header = new Uint8Array(44);

    // RIFF Chunk Descriptor
    writeString(header, 0, 'RIFF');
    writeUint32(header, 4, 36 + length);
    writeString(header, 8, 'WAVE');

    // fmt sub-chunk
    writeString(header, 12, 'fmt ');
    writeUint32(header, 16, 16); // Subchunk1Size (16 for PCM)
    writeUint16(header, 20, 1); // AudioFormat (1 for PCM)
    writeUint16(header, 22, numChannels);
    writeUint32(header, 24, sampleRate);
    writeUint32(header, 28, byteRate);
    writeUint16(header, 32, numChannels * bytesPerSample);
    writeUint16(header, 34, bitsPerSample);

    // data sub-chunk
    writeString(header, 36, 'data');
    writeUint32(header, 40, length);

    const buffer = new Uint8Array(44 + length);
    buffer.set(header);

    // Write audio data
    const channelData = audioBuffer.getChannelData(0);
    for (let i = 0; i < channelData.length; i++) {
        const sample = Math.max(-1, Math.min(1, channelData[i])) * 32767;
        buffer[44 + i * 2] = sample & 0xff;
        buffer[45 + i * 2] = (sample >> 8) & 0xff;
    }

    return new Blob([buffer], { type: 'audio/wav' });
}

/**
 * Escreve uma string em um Uint8Array.
 * 
 * @param {Uint8Array} view - O Uint8Array onde a string será escrita.
 * @param {number} offset - O offset no Uint8Array onde a string começará.
 * @param {string} string - A string a ser escrita.
 */
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view[offset + i] = string.charCodeAt(i);
    }
}

/**
 * Escreve um valor de 16 bits em um Uint8Array.
 * 
 * @param {Uint8Array} view - O Uint8Array onde o valor será escrito.
 * @param {number} offset - O offset no Uint8Array onde o valor começará.
 * @param {number} value - O valor de 16 bits a ser escrito.
 */
function writeUint16(view, offset, value) {
    view[offset] = value & 0xff;
    view[offset + 1] = (value >> 8) & 0xff;
}

/**
 * Escreve um valor de 32 bits em um Uint8Array.
 * 
 * @param {Uint8Array} view - O Uint8Array onde o valor será escrito.
 * @param {number} offset - O offset no Uint8Array onde o valor começará.
 * @param {number} value - O valor de 32 bits a ser escrito.
 */
function writeUint32(view, offset, value) {
    view[offset] = value & 0xff;
    view[offset + 1] = (value >> 8) & 0xff;
    view[offset + 2] = (value >> 16) & 0xff;
    view[offset + 3] = (value >> 24) & 0xff;
}