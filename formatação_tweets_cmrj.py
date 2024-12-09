import streamlit as st
import panda as pd
import re

# Função para reconhecer e extrair o número do projeto, incluindo formatos com "-A"
def reconhecer_numero_projeto(linha):
    """
    Extrai o número completo do projeto, incluindo o formato com "-A".
    Exemplo: '186-A/2024'.
    """
    match = re.search(r"Nº (\d+[-A]?/\d+)", linha)
    if match:
        return match.group(1)
    return None

# Função principal com a lógica aprimorada para leitura de projetos
def formatar_tweets(ordem_dia):
    tweets = []
    linhas = ordem_dia.split("\n")  # Divide o texto em linhas

    for linha in linhas:
        linha = linha.strip()

        # Identificar vetos
        if "VETO PARCIAL" in linha or "VETO TOTAL" in linha:
            veto_tipo = "parcial" if "VETO PARCIAL" in linha else "total"
            numero_projeto = reconhecer_numero_projeto(linha)
            descricao_match = re.search(r'QUE "(.*?)"', linha)

            if numero_projeto and descricao_match:
                descricao = descricao_match.group(1).capitalize().rstrip('.')
                tweets.append(f"#Ordemdodia Rejeitado o veto {veto_tipo} do Poder Executivo ao PL {numero_projeto}, que {descricao.lower()}.")

        # Identificar projetos de lei, decretos e emendas
        elif "PROJETO DE" in linha or "EMENDA À LEI ORGÂNICA" in linha:
            tipo_match = re.search(r"PROJETO DE (LEI|LEI COMPLEMENTAR|DECRETO LEGISLATIVO|EMENDA À LEI ORGÂNICA)", linha)
            numero_projeto = reconhecer_numero_projeto(linha)
            descricao_match = re.search(r'QUE "(.*?)"', linha)
            discussao_match = re.search(r"EM (\dª DISCUSSÃO|DISCUSSÃO ÚNICA)", linha)

            if tipo_match and numero_projeto and descricao_match:
                tipo = tipo_match.group(1)
                descricao = descricao_match.group(1).capitalize().rstrip('.')
                prefixo = {"LEI": "PL", "LEI COMPLEMENTAR": "PLC", "DECRETO LEGISLATIVO": "PDL", "EMENDA À LEI ORGÂNICA": "PELOM"}.get(tipo, "PL")
                discussao = discussao_match.group(1) if discussao_match else "em tramitação"

                if "1ª DISCUSSÃO" in linha:
                    status = "Aprovado, em 1ª discussão"
                elif "2ª DISCUSSÃO" in linha:
                    status = "Aprovado, em 2ª discussão"
                elif "DISCUSSÃO ÚNICA" in linha:
                    status = "Aprovado, em discussão única"
                else:
                    status = "Em tramitação"

                tweets.append(f"#Ordemdodia {status}, o {prefixo} {numero_projeto}, que {descricao.lower()}.")

    return tweets
