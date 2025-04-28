import re
import random
import json
from datetime import datetime

INTENCOES = {
    "saudacao": ["oi", "olá", "bom dia", "boa tarde", "boa noite", "hey", "hi"],
    "despedida": ["tchau", "até logo", "falou", "adeus", "até mais", "bye"],
    "ajuda": ["ajuda", "socorro", "como faço", "não sei", "preciso de ajuda", "help"],
    "produto": ["produto", "tem", "vender", "preço", "quanto custa", "disponível"],
    "horario": ["horário", "horario", "aberto", "fechado", "funciona", "atendimento"],
    "localizacao": ["onde fica", "endereço", "endereco", "local", "como chegar"],
    "promocao": ["promoção", "promocao", "desconto", "oferta", "black friday"],
    "duvida": ["dúvida", "duvida", "pergunta", "como funciona", "pode explicar"],
    "feedback": ["feedback", "opinião", "opiniao", "sugestão", "sugestao"],
    "contato": ["contato", "telefone", "email", "whatsapp", "falar com alguém"],
}

RESPOSTAS_TEMPLATES = {
    "saudacao": [
        "Oi, tudo bem? Como posso te ajudar?",
        "Olá! Precisa de alguma coisa?",
        "Oi! Seja bem-vindo :)",
        "Olá! Em que posso ser útil hoje?",
        "Oi! Que bom te ver por aqui!"
    ],
    "despedida": [
        "Tchau! Até a próxima.",
        "Foi bom falar com você. Até logo!",
        "Falou! Qualquer coisa, tô por aqui.",
        "Até mais! Volte sempre!",
        "Tchau! Tenha um ótimo dia!"
    ],
    "ajuda": [
        "Claro, estou aqui para ajudar. O que você precisa?",
        "Você pode me contar melhor o que está acontecendo?",
        "Estou à disposição! Diga o que precisa.",
        "Como posso te ajudar hoje?",
        "Me conte mais sobre o que você precisa."
    ],
    "produto": [
        "Temos vários produtos. Está buscando algo específico?",
        "Sim! Posso te mostrar os mais populares. Qual categoria te interessa?",
        "Você quer saber sobre preços ou sobre disponibilidade?",
        "Temos uma grande variedade. Qual tipo de produto você procura?",
        "Posso te ajudar a encontrar o produto ideal. O que você precisa?"
    ],
    "horario": [
        "Nosso horário de funcionamento é de segunda a sexta, das 9h às 18h.",
        "Estamos abertos de segunda a sexta, das 9h às 18h.",
        "Nosso atendimento é de segunda a sexta, das 9h às 18h.",
        "Funcionamos de segunda a sexta, das 9h às 18h.",
        "Nosso horário é de segunda a sexta, das 9h às 18h."
    ],
    "localizacao": [
        "Estamos localizados na Rua Principal, 123, Centro.",
        "Nosso endereço é Rua Principal, 123, Centro.",
        "Ficamos na Rua Principal, 123, Centro.",
        "Estamos na Rua Principal, 123, Centro.",
        "Nosso endereço é Rua Principal, 123, Centro."
    ],
    "promocao": [
        "Temos várias promoções! Quer que eu te mostre as mais recentes?",
        "Sim! Temos várias ofertas especiais. Qual categoria te interessa?",
        "Temos descontos incríveis! Quer saber mais?",
        "Temos várias promoções! Quer que eu te mostre?",
        "Sim! Temos várias ofertas. Qual categoria te interessa?"
    ],
    "duvida": [
        "Claro! Qual sua dúvida?",
        "Estou aqui para ajudar! Qual sua dúvida?",
        "Me conte sua dúvida que eu te ajudo!",
        "Qual sua dúvida? Estou aqui para ajudar!",
        "Me diga sua dúvida que eu te explico!"
    ],
    "feedback": [
        "Adoraria ouvir seu feedback! O que você achou?",
        "Me conte sua opinião! O que você achou?",
        "Sua opinião é muito importante! O que você achou?",
        "Me diga o que você achou!",
        "Adoraria saber sua opinião! O que você achou?"
    ],
    "contato": [
        "Nosso telefone é (11) 1234-5678.",
        "Você pode nos contatar pelo telefone (11) 1234-5678.",
        "Nosso email é contato@empresa.com.",
        "Você pode nos contatar pelo email contato@empresa.com.",
        "Nosso WhatsApp é (11) 98765-4321."
    ],
    "desconhecida": [
        "Hmmm... não entendi muito bem. Pode tentar dizer de outro jeito?",
        "Desculpa, não peguei. Pode repetir por favor?",
        "Ainda não entendi. Me explica melhor?",
        "Não consegui entender. Pode reformular?",
        "Desculpe, não entendi. Pode tentar de outra forma?"
    ],
}

def detectar_intencao(mensagem):
    mensagem = mensagem.lower()
    melhor_intencao = "desconhecida"
    melhor_confianca = 0.0
    
    for intencao, padroes in INTENCOES.items():
        for padrao in padroes:
            if re.search(rf"\b{re.escape(padrao)}\b", mensagem):
                confianca = len(padrao) / len(mensagem)
                if confianca > melhor_confianca:
                    melhor_confianca = confianca
                    melhor_intencao = intencao
    
    return melhor_intencao, melhor_confianca

def gerar_resposta_dinamica(intencao, contexto=None):
    templates = RESPOSTAS_TEMPLATES.get(intencao, RESPOSTAS_TEMPLATES["desconhecida"])
    template_escolhido = random.choice(templates)
    
    if contexto:
        # Substitui variáveis no template
        for key, value in contexto.items():
            if f"{{{key}}}" in template_escolhido:
                template_escolhido = template_escolhido.replace(f"{{{key}}}", str(value))
    
    return template_escolhido

def processar_midia(mensagem):
    # Detecta URLs de imagens
    urls_imagem = re.findall(r'https?://[^\s<>"]+?\.(?:jpg|jpeg|gif|png)', mensagem)
    if urls_imagem:
        return True, urls_imagem[0]
    return False, None

def responder_com_memoria(mensagem, historico, session_id):
    intencao, confianca = detectar_intencao(mensagem)
    has_media, media_url = processar_midia(mensagem)
    
    # Extrai informações do contexto
    contexto = {}
    for msg in historico:
        if "me chamo" in msg["content"].lower():
            nome_encontrado = re.search(r"me chamo ([a-zA-Zçãáéíóúêô ]+)", msg["content"].lower())
            if nome_encontrado:
                contexto["nome"] = nome_encontrado.group(1).strip().title()
    
    # Adiciona informações de data/hora
    agora = datetime.now()
    contexto["hora"] = agora.strftime("%H:%M")
    contexto["data"] = agora.strftime("%d/%m/%Y")
    
    resposta = gerar_resposta_dinamica(intencao, contexto)
    
    return {
        "intent": intencao,
        "confidence": confianca,
        "response": resposta,
        "has_media": has_media,
        "media_url": media_url,
        "context": contexto
    } 