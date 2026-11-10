// Base das APIs do backend Python
console.log('utils.js carregado');
const API_BASE = '/api';

async function apiPost(endpoint, payload) {
    const response = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        let message = 'Erro ao comunicar com o servidor';
        try {
            const data = await response.json();
            if (data && data.error) {
                message = data.error;
            }
        } catch (_) {
            // ignora erro de parse
        }
        throw new Error(message);
    }

    return response.json();
}

// ---- Funções de integração com o backend ----

// Identificar aluno por CPF
async function identificarAlunoBackend(cpf) {
    const data = await apiPost('identificar', { cpf });
    if (!data.success || !data.aluno) {
        throw new Error(data.error || 'Não foi possível identificar o aluno');
    }
    return data.aluno;
}

// Verificar/registrar ocorrência
// tipos aceitos: 'esquecimento', 'perda', 'uniforme'
async function registrarOcorrenciaBackend(cpf, tipo) {
    const data = await apiPost('ocorrencia', { cpf, tipo });
    if (!data.success) {
        throw new Error(data.error || 'Erro ao registrar ocorrência');
    }
    return {
        permitido: data.permitido,
        mensagem: data.mensagem || null
    };
}

// Gerar ticket
// tipo: 'entrada', 'saida', 'saida_apoio', 'saida_esporte', 'saida_biblioteca',
//       'saida_tutor', 'cracha_esquecimento', 'cracha_perda', 'uniforme'
async function gerarTicketBackend(cpf, tipo, motivo, hora) {
    const data = await apiPost('ticket', { cpf, tipo, motivo, hora });
    if (!data.success || !data.ticket) {
        throw new Error(data.error || 'Erro ao gerar ticket');
    }
    return data.ticket;
}

// Storage para dados temporários entre telas
const storage = {
    set: function(key, value) {
        sessionStorage.setItem(key, JSON.stringify(value));
    },
    get: function(key) {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },
    remove: function(key) {
        sessionStorage.removeItem(key);
    },
    clear: function() {
        sessionStorage.clear();
    }
};

// Função para formatar CPF
function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Função para validar CPF
function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.length !== 11) return false;
    
    // Verifica se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;
    
    // Validação dos dígitos verificadores
    let soma = 0;
    for (let i = 0; i < 9; i++) {
        soma += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let digito1 = 11 - (soma % 11);
    if (digito1 >= 10) digito1 = 0;
    
    if (digito1 !== parseInt(cpf.charAt(9))) return false;
    
    soma = 0;
    for (let i = 0; i < 10; i++) {
        soma += parseInt(cpf.charAt(i)) * (11 - i);
    }
    let digito2 = 11 - (soma % 11);
    if (digito2 >= 10) digito2 = 0;
    
    return digito2 === parseInt(cpf.charAt(10));
}

// Função para obter data e hora formatadas
function obterDataHora() {
    const agora = new Date();
    const data = agora.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' });
    const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    return { data, hora, agora };
}

// Função para gerar QR Code
function gerarQRCode(codigo, container) {
    container.innerHTML = '';
    QRCode.toCanvas(container, codigo.toString(), {
        width: 200,
        height: 200,
        colorDark: '#000000',
        colorLight: '#FFFFFF',
        correctLevel: QRCode.CorrectLevel.H
    }, function (error) {
        if (error) {
            console.error('Erro ao gerar QR Code:', error);
            container.innerHTML = `<div style="padding: 20px; color: #E30613;">Erro ao gerar QR Code<br>Código: ${codigo}</div>`;
        }
    });
}

