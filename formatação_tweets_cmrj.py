import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ferramenta de Agilização para Tweets da Câmara Municipal do Rio", page_icon="📐", layout="wide")
st.caption('Essa ferramenta facilita a criação de tweets para as sessões plenárias, otimizando o tempo e a precisão na comunicação.')

def capitalizar_nomes_proprios(texto):
    # Palavras que devem começar com letra minúscula em nomes próprios
    palavras_excecao = ["da", "de", "do", "e", "em", "a", "o", "as", "os"]
    palavras = texto.split()
    texto_formatado = " ".join([
        palavra.capitalize() if palavra.lower() not in palavras_excecao else palavra.lower()
        for palavra in palavras
    ])
    return texto_formatado

def formatar_tweets(ordem_dia):
    tweets = []
    linhas = ordem_dia.split("\n")  # Divide o texto por linhas

    for linha in linhas:
        linha = linha.strip()
        
        # Detectar vetos
        if "VETO PARCIAL" in linha or "VETO TOTAL" in linha:
            veto_tipo = "parcial" if "VETO PARCIAL" in linha else "total"
            projeto_match = re.search(r"PROJETO DE LEI Nº (\d+[A-Z]?/\d+)", linha)
            descricao_match = re.search(r'QUE "(.*?)"', linha)

            if projeto_match and descricao_match:
                numero_projeto = projeto_match.group(1)
                descricao = capitalizar_nomes_proprios(descricao_match.group(1).capitalize().rstrip('.'))
                tweets.append(f"#Ordemdodia Rejeitado o veto {veto_tipo} do Poder Executivo ao PL {numero_projeto}, que {descricao.lower()}.")

        # Detectar projetos de lei
        elif "PROJETO DE" in linha or "EMENDA À LEI ORGÂNICA" in linha:
            tipo_match = re.search(r"PROJETO DE (LEI|LEI COMPLEMENTAR|DECRETO LEGISLATIVO|EMENDA À LEI ORGÂNICA)", linha)
            numero_match = re.search(r"Nº (\d+[A-Z]?/\d+)", linha)
            descricao_match = re.search(r'QUE "(.*?)"', linha)
            discussao_match = re.search(r"EM (\dª DISCUSSÃO|DISCUSSÃO ÚNICA)", linha)

            if tipo_match and numero_match and descricao_match:
                tipo = tipo_match.group(1)
                numero_projeto = numero_match.group(1)
                descricao = capitalizar_nomes_proprios(descricao_match.group(1).capitalize().rstrip('.'))
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

# Interface Streamlit
input_text = st.text_area("Cole aqui o texto da Ordem do Dia:")

if input_text:
    st.write("Texto Processado (Ordem do Dia):")
    tweets = formatar_tweets(input_text)

    if tweets:
        for tweet in tweets:
            st.write(tweet)
    else:
        st.write("Nenhum projeto encontrado. Verifique o formato da entrada.")
