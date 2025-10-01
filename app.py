import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from faker import Faker
import os

# ========== CONFIGURAÇÃO ==========
st.set_page_config(page_title="Consulta Cliente Claro", layout="wide")
fake = Faker('pt_BR')

# 🔒 CHAVE OPENAI SEGURA
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("❌ Chave da OpenAI não configurada. Configure a variável OPENAI_API_KEY.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# ========== CARREGA E PREPARA DATASET ==========
@st.cache_data
def carregar_dados():
    # 📁 CAMINHO RELATIVO (funciona no deploy)
    try:
        # Primeiro tenta carregar do diretório atual
        df = pd.read_excel('raio_x_clientes_claro_rev1.xlsx')
    except FileNotFoundError:
        try:
            # Se não encontrar, tenta na pasta dataset
            df = pd.read_excel('dataset/raio_x_clientes_claro_rev1.xlsx')
        except FileNotFoundError:
            st.error("❌ Arquivo Excel não encontrado. Certifique-se de que 'raio_x_clientes_claro_rev1.xlsx' está no repositório.")
            st.stop()

    if 'Nome do Cliente' not in df.columns:
        df.insert(1, 'Nome do Cliente', [fake.name() for _ in range(len(df))])

    nomes_colunas = [
        'Código da Operadora / Contrato do Cliente', 'Nome do Cliente',
        'Node da Instalação do Cliente', 'Município', 'Célula da Instalação do Cliente',
        'Produto Principal', 'Produto de Telefone', 'Produto de Banda Larga',
        'Modelo do Modem do Cliente', 'Modelo do Decoder da TV', 'Tecnologia da Banda Larga',
        'Visitas Técnicas Agendadas últimos 15 dias', 'Visitas Técnicas Executadas últimos 15 dias',
        'Visitas Técnicas Cqanceladas últimos 15 dias', 'Quantidade de Ligações ou Interações no digital últimos 15 dias',
        'Quantidade Ligações Retidas na URA, que não foram direcionadas a atendente humano',
        'Quantidade Ligações Direcionadas para Humano', 'Quantidade de Eventos no Digital (Site/App)',
        'Quantidade de Outage Sem Sinal Corretivo', 'Quantidade de Outage Sem Sinal Preventivo',
        'Quantidade de Outage por degradação', 'Quantidade de Outage Informativo',
        'Tempo de Outage Sem Sinal Corretivo', 'Tempo de Outage Sem Sinal Preventivo',
        'Tempo de Outage por degradação', 'Tempo de Outage Informativo',
        'Ferramenta Xpertrack - Porcentagem do Tempo que a rede estava Impactada',
        'Ferramenta Xpertrack - Porcentagem do Tempo que a rede estava Estressada',
        'Ferramenta Xpertrack - Quantidade de Dias que a rede estava em estado Crônica',
        'Ferramenta Xpertrack - Porcentagem do Tempo que a rede estava Online',
        'Ferramenta Xpertrack - "QOE" - Nota de Qualidade da Célula da Instalação (De 0 a 100)',
        'Speed Test OOKLA - Quantidade de Testes de Velocidades Feitos',
        'Speed Test OOKLA - Rating Testes', 'Speed Test OOKLA - Percent Rating Testes',
        'Speed Test OOKLA - Porcentagem de  Velocidade Atingida no Downstream versus a Contratada',
        'Ferramenta Beegol - Porcentagem de Velocidade Atingida no Downstream versus a Contratada',
        'Speed Test OOKLA - Porcentagem de Velocidade Atingida no Upstream versus a Contratada',
        'Ferramenta Beegol - Porcentagem de Velocidade Atingida no Upstream versus a Contratada',
        'Ferramenta Beegol - Velocidade Atingida no Downstream em kbps',
        'Speed Test OOKLA - Velocidade Atingida no Downstream em kbps',
        'Ferramenta Beegol - Velocidade Atingida no Upstream em kbps',
        'Speed Test OOKLA - Velocidade Atingida no Upstream em kbps', 'NOTA_RATING',
        'Speed Test OOKLA - Nota de Avaliação do Teste',
        'Speed Test OOKLA - RSSI Medido (Maior que -60 - Bom, Menor que -60 Ruim)',
        'Nota Pesquisa Recomendação Sinal', 'Nota da Pesquisa - Banda Larga',
        'Nota da Pesquisa - Produto TV', 'Nota da Pesquisa - Queda de Sinal',
        'A pesquisa  TNPS Inst teve Verbatin?', 'Data da Pesquisa TNPS', 'Quantidade de Manisfestos',
        'Ferramenta Beegol - Nota de Qualidade "QOE" - Geral',
        'Ferramenta Beegol - Nota de Qualidade "QOE" - Banda Larga',
        'Ferramenta Beegol - Nota de Qualidade "QOE" - Dispositivos',
        'Ferramenta Beegol - Nota de Qualidade "QOE" - Wifi',
        'Ferramenta Beegol - Média Sinal RSSI (Maior que -60 - Bom, Menor que -60 Ruim)',
        'Ferramenta Beegol - Quantidade de Devices Conectados no Período',
        'Ferramenta Raio X Nota de Qualidade'
    ]
    df.columns = nomes_colunas
    return df

df = carregar_dados()

# ========== INTERFACE ==========
st.markdown("<h2 style='color:#005bea;'>📋 Consulta de Cliente - Dados de Rede</h2>", unsafe_allow_html=True)

# Campo + botão limpar
col1, col2 = st.columns([4, 1])
with col1:
    codigo_cliente = st.text_input("🔢 Digite o código da Operadora / Contrato do Cliente:", key="codigo_input")
with col2:
    if st.button("🧹 Limpar Tudo"):
        for key in ["codigo_input", "resumo_cliente", "chat_history", "nova_pergunta"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Ação ao digitar código
if codigo_cliente:
    cliente = df[df['Código da Operadora / Contrato do Cliente'] == codigo_cliente]

    if cliente.empty:
        st.warning("❌ Cliente não encontrado.")
    else:
        linha = cliente.iloc[0]

        dados_chave = f"""
**Contrato/Operadora:** {linha['Código da Operadora / Contrato do Cliente']}  
**Nome:** {linha['Nome do Cliente']}  
**Município:** {linha['Município']}  
**Node:** {linha['Node da Instalação do Cliente']}  
**Célula:** {linha['Célula da Instalação do Cliente']}  
**Produto Banda Larga:** {linha['Produto de Banda Larga']}  
**Tecnologia:** {linha['Tecnologia da Banda Larga']}  
**Modem:** {linha['Modelo do Modem do Cliente']}
"""
        st.markdown("### 🧾 Dados do Cliente")
        st.info(dados_chave)

        # ======= RESUMO =========
        dados_completos = '\n'.join(f"{col}: {linha[col]}" for col in df.columns)

        if "resumo_cliente" not in st.session_state:
            prompt_resumo = (
                "Você é um assistente especializado em Banda Larga.\n"
                "A seguir estão várias informações referentes a um determinado Cliente:\n\n"
                f"{dados_completos}\n\n"
                "Faça um resumo de todas as informações do Cliente em questão.\n"
                "Regras:\n- Dê ênfase aos campos com informações úteis.\n- Ignore campos com valor 0 ou NaN."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # 🤖 MODELO CORRETO E MAIS BARATO
                    messages=[{"role": "user", "content": prompt_resumo}],
                    temperature=0
                )
                st.session_state.resumo_cliente = response.choices[0].message.content.strip()
            except Exception as e:
                st.session_state.resumo_cliente = f"Erro ao chamar API: {e}"

        st.markdown("### 📊 Resumo Geral do Cliente")
        st.success(st.session_state.resumo_cliente)

        # ======= PERGUNTA PERSONALIZADA ========
        st.markdown("###    Faça uma pergunta sobre o cliente")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "system", "content": "Você é um assistente especializado em Banda Larga. Use os dados abaixo como referência:\n" + dados_completos}
            ]

        pergunta_usuario = st.text_area("📝 Sua pergunta:", key="nova_pergunta", height=100)

        col_enviar = st.columns([8, 2])
        with col_enviar[1]:
            enviar = st.button("📨 Enviar pergunta")

        if enviar and pergunta_usuario.strip():
            st.session_state.chat_history.append({"role": "user", "content": pergunta_usuario})
            try:
                resposta_chat = client.chat.completions.create(
                    model="gpt-4o-mini",  # 🤖 MODELO CORRETO
                    messages=st.session_state.chat_history,
                    temperature=0
                )
                resposta = resposta_chat.choices[0].message.content.strip()
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})
            except Exception as e:
                resposta = f"Erro na API: {e}"
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})

            st.rerun()

        # ======= CONVERSA COM O ASSISTENTE ========
        st.markdown("### 💬 Conversa com o Assistente")

        with st.container():
            chat_html = """
            <div style='height:400px; overflow-y:scroll; padding:10px; border:1px solid #ccc;
                        border-radius:10px; background-color:#f9f9f9; font-family: sans-serif; font-size: 14px;'>
            """
            for msg in st.session_state.chat_history[1:]:
                if msg["role"] == "user":
                    chat_html += f"<p><b>🧑‍💼 Você:</b> {msg['content']}</p>"
                else:
                    chat_html += f"<p><b>🤖 Assistente:</b> {msg['content']}</p>"
            chat_html += "</div>"

            components.html(chat_html, height=420, scrolling=True)