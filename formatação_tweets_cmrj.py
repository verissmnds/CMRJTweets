import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Ferramenta de Agilização para Tweets da Câmara Municipal do Rio", page_icon="📐", layout="wide")
st.caption('Essa ferramenta facilita a criação de tweets para as sessões plenárias, otimizando o tempo e a precisão na comunicação. DIFERENTE')

def processar_ordens(input_text, separador="?"):
    # Expressão regular para encontrar os números de tramitação seguidos das informações
    padrao_ordem = r"(\d{1,2}(?:,\d{2})?)\s+EM\s+(.*?)(?=(\d{1,2}(?:,\d{2})?)\s+EM|$)"

    # Encontrando todas as ordens no texto
    ordens = re.findall(padrao_ordem, input_text, re.DOTALL)

    # Processar as ordens encontradas e gerar uma lista formatada
    ordens_formatadas = []
    for ordem in ordens:
        numero = ordem[0]
        tramitação = ordem[1].strip().replace("\n", " ")  # Remove quebras de linha e espaços extras
        ordem_formatada = f"{numero} EM {tramitação}"
        ordens_formatadas.append(ordem_formatada)

    # Retornar as ordens formatadas como uma única string separada pelo separador
    return f" {separador} ".join(ordens_formatadas)

st.caption('Primeiro, copie toda a ordem do dia no site da Câmara e cole-a nesta caixa de inserção. Em seguida, cole o texto retornado para o próximo passo.')

# Capturar o texto inserido pelo usuário
input_text = st.text_area("Cole aqui o texto da Ordem do Dia:")

if input_text:
    # Chamando a função com o texto de entrada e o separador "?"
    output = processar_ordens(input_text, separador="?")

    # Exibindo a saída no Streamlit
    st.write("Texto Processado (Ordem do Dia):")
    st.text(output)

    def formatar_tweets(ordem_dia):
        tweets = []
        # Utilizando a função processar_ordens para tratar o texto da Ordem do Dia
        ordem_dia_processada = processar_ordens(ordem_dia, separador="?")
        linhas = ordem_dia_processada.split("?")  # Separa por blocos de ordens

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

            # Identificar projetos de lei, decretos e emendas
            elif "PROJETO DE" in linha or "EMENDA À LEI ORGÂNICA" in linha:
                tipo_match = re.search(r"PROJETO DE (LEI|DECRETO LEGISLATIVO|EMENDA À LEI ORGÂNICA|LEI COMPLEMENTAR)", linha)
                numero_match = re.search(r"Nº (\d+[-A]?/\d+)", linha)
                descricao_match = re.search(r'QUE "(.*?)"', linha)
                discussao_match = re.search(r"EM (\dª DISCUSSÃO|DISCUSSÃO ÚNICA)", linha)

                if tipo_match and numero_match and descricao_match:
                    tipo = tipo_match.group(1)
                    numero_projeto = numero_match.group(1)
                    descricao = descricao_match.group(1).capitalize().rstrip('.')
                    prefixo = {"LEI": "PL", "DECRETO LEGISLATIVO": "PDL", "EMENDA À LEI ORGÂNICA": "PELOM", "LEI COMPLEMENTAR": "PLC"}.get(tipo, "PL")
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

    # Gerar os tweets com base no texto processado
    tweets = formatar_tweets(input_text)

    if tweets:
        st.write("Tweets Gerados:")
        for tweet in tweets:
            st.write(tweet)
    else:
        st.write("Nenhum projeto encontrado. Verifique o formato da entrada.")
