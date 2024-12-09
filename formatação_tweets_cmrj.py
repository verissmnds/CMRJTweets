import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Ferramenta de Agilização para Tweets da Câmara Municipal do Rio", page_icon="📐", layout="wide")

# Título da página com cor personalizada
st.markdown('<h2 style="text-align: center; color: #7d6436;">Gerador de tweets da Câmara Municipal do Rio</h2>', unsafe_allow_html=True)

# Descrição da ferramenta
st.markdown('<p style="font-size: 18px; text-align: center; color: #7d6436;">Essa ferramenta facilita a criação de tweets para as sessões plenárias, otimizando o tempo e a precisão na comunicação.</p>', unsafe_allow_html=True)

# Instruções com link
st.markdown(
    '<p style="font-size: 18px; font-weight: bold;">'
    'Copie toda a <a href="https://www.camara.rio/atividade-parlamentar/plenario/ordem-do-dia" target="_blank">ordem do dia</a> no site da Câmara e cole-a nesta caixa de inserção.'
    '</p>', unsafe_allow_html=True)

# Capturar o texto inserido pelo usuário
input_text = st.text_area("", height=200)

def processar_ordens(input_text, separador="?"):
    padrao_ordem = r"(\d{1,2}(?:,\d{2})?)\s+EM\s+(.*?)(?=(\d{1,2}(?:,\d{2})?)\s+EM|$)"
    ordens = re.findall(padrao_ordem, input_text, re.DOTALL)
    ordens_formatadas = []
    for ordem in ordens:
        numero = ordem[0]
        tramitação = ordem[1].strip().replace("\n", " ")
        ordem_formatada = f"{numero} EM {tramitação}"
        ordens_formatadas.append(ordem_formatada)
    return f" {separador} ".join(ordens_formatadas)

if input_text:
    output = processar_ordens(input_text, separador="?")

    def formatar_tweets(ordem_dia):
        tweets = []
        ordem_dia_processada = processar_ordens(ordem_dia, separador="?")
        linhas = ordem_dia_processada.split("?")
        
        for linha in linhas:
            linha = linha.strip()
            if "VETO PARCIAL" in linha or "VETO TOTAL" in linha:
                veto_tipo = "parcial" if "VETO PARCIAL" in linha else "total"
                projeto_match = re.search(r"PROJETO DE LEI Nº (\d+/\d+)", linha)
                descricao_match = re.search(r'QUE "(.*?)"', linha)

                if projeto_match and descricao_match:
                    numero_projeto = projeto_match.group(1)
                    descricao = descricao_match.group(1).capitalize().rstrip('.')
                    tweets.append(f"#Ordemdodia Rejeitado o veto {veto_tipo} do Poder Executivo ao PL {numero_projeto}, que {descricao.lower()}.")

            elif "PROJETO DE" in linha or "EMENDA À LEI ORGÂNICA" in linha:
                tipo_match = re.search(r"PROJETO DE (DECRETO LEGISLATIVO|EMENDA À LEI ORGÂNICA|LEI COMPLEMENTAR|LEI)", linha)
                numero_match = re.search(r"Nº (\d+[-A]*/\d+)", linha)
                descricao_match = re.search(r'QUE "(.*?)"', linha)
                discussao_match = re.search(r"EM (\dª DISCUSSÃO|DISCUSSÃO ÚNICA)", linha)

                if tipo_match and numero_match and descricao_match:
                    tipo = tipo_match.group(1)
                    numero_projeto = numero_match.group(1)
                    descricao = descricao_match.group(1).capitalize().rstrip('.')
                    if "LEI COMPLEMENTAR" in tipo:
                        prefixo = "PLC"
                    elif "EMENDA À LEI ORGÂNICA" in tipo:
                        prefixo = "PELOM"
                    else:
                        prefixo = "PL"
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

    tweets = formatar_tweets(input_text)

    if tweets:
        st.markdown('<p style="font-size: 20px; font-weight: bold;">Tweets Gerados:</p>', unsafe_allow_html=True)
        for tweet in tweets:
            st.write(tweet)
    else:
        st.write("Nenhum projeto encontrado. Verifique o formato da entrada.")

logo_url = "https://raw.githubusercontent.com/verissmnds/CMRJTweets/main/logo.png"
st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <img src="{logo_url}" alt="Logo" style="width: 150px;">
    </div>
""", unsafe_allow_html=True)
