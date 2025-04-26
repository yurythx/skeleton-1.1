import re
import random

INTENCOES = {
    "saudacao": ["oi", "olá", "bom dia", "boa tarde"],
    "despedida": ["tchau", "até logo", "falou"],
    "ajuda": ["ajuda", "socorro", "como faço", "não sei"],
    "produto": ["produto", "tem", "vender", "preço"],
}

RESPOSTAS_TEMPLATES = {
    "saudacao": [
        "Oi, tudo bem? Como posso te ajudar?",
        "Olá! Precisa de alguma coisa?",
        "Oi! Seja bem-vindo :)"
    ],
    "despedida": [
        "Tchau! Até a próxima.",
        "Foi bom falar com você. Até logo!",
        "Falou! Qualquer coisa, tô por aqui."
    ],
    "ajuda": [
        "Claro, estou aqui para ajudar. O que você precisa?",
        "Você pode me contar melhor o que está acontecendo?",
        "Estou à disposição! Diga o que precisa."
    ],
    "produto": [
        "Temos vários produtos. Está buscando algo específico?",
        "Sim! Posso te mostrar os mais populares. Qual categoria te interessa?",
        "Você quer saber sobre preços ou sobre disponibilidade?"
    ],
    "desconhecida": [
        "Hmmm... não entendi muito bem. Pode tentar dizer de outro jeito?",
        "Desculpa, não peguei. Pode repetir por favor?",
        "Ainda não entendi. Me explica melhor?"
    ],
}

def detectar_intencao(mensagem):
    mensagem = mensagem.lower()
    for intencao, padroes in INTENCOES.items():
        for padrao in padroes:
            if re.search(rf"\b{re.escape(padrao)}\b", mensagem):
                return intencao
    return "desconhecida"

def gerar_resposta_dinamica(intencao, contexto=None):
    templates = RESPOSTAS_TEMPLATES.get(intencao, RESPOSTAS_TEMPLATES["desconhecida"])
    template_escolhido = random.choice(templates)
    
    # Aqui podemos usar dados do contexto para preencher
    if contexto and "{nome}" in template_escolhido:
        nome = contexto.get("nome", "amigo")
        return template_escolhido.format(nome=nome)
    
    return template_escolhido

def responder_com_memoria(mensagem, historico):
    intencao = detectar_intencao(mensagem)

    # Exemplo: detectar nome se o usuário disser "me chamo X"
    nome = None
    match = re.search(r"me chamo ([a-zA-Zçãáéíóúêô ]+)", mensagem.lower())
    if match:
        nome = match.group(1).strip().title()

    # Armazena o nome no histórico (simples — pode ser salvo em contexto real)
    contexto = {}
    for msg in historico:
        if "me chamo" in msg["content"].lower():
            nome_encontrado = re.search(r"me chamo ([a-zA-Zçãáéíóúêô ]+)", msg["content"].lower())
            if nome_encontrado:
                contexto["nome"] = nome_encontrado.group(1).strip().title()
    if nome:
        contexto["nome"] = nome

    return gerar_resposta_dinamica(intencao, contexto)