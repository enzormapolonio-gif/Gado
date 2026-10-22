import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard de Dados - IBGE",
    layout="wide"
)

st.title("Dashboard: Evolução do Rebanho Bovino no Brasil")
st.write("""
Este dashboard analisa o crescimento do efetivo de bovinos (em cabeças) no Brasil ao longo das décadas, com base nos dados oficiais do IBGE (Tabela 3939).
O objetivo é compreender como este indicador evoluiu e identificar os anos com os maiores registros.
""")

# --- AULA 2: LEITURA DIRETA DO ARQUIVO LOCAL ---
try:
    with open("tabela3939.csv", "r", encoding="utf-8") as f:
        linhas = f.read().splitlines()
        
    anos_brutos = linhas[3].split(";")
    anos = [ano.replace('"', '').strip() for ano in anos_brutos if ano.replace('"', '').strip().isdigit()]
    
    linha_brasil = ""
    for linha in linhas:
        if '"Brasil"' in linha:
            linha_brasil = linha
            break
            
    valores_brasil = linha_brasil.split(";")
    bovinos = []
    for i in range(2, len(valores_brasil), 10):
        val = valores_brasil[i].replace('"', '').strip()
        if val.isdigit():
            bovinos.append(int(val))
        elif val == '-':
            bovinos.append(None)
            
    df = pd.DataFrame({
        "Ano": anos,
        "Cabeças de Gado": bovinos[:len(anos)]
    })
    
    df = df.dropna()
    df["Ano"] = df["Ano"].astype(int)

    # --- PERGUNTAS E RESPOSTAS (AULA 1) ---
    ano_max = df.loc[df["Cabeças de Gado"].idxmax(), "Ano"]
    valor_max = df["Cabeças de Gado"].max()
    
    st.markdown(f"""
    **Perguntas de Pesquisa e Principais Descobertas**
    
    **Pergunta 1: Em que ano o rebanho bovino foi maior?**
    * **Resposta:** O maior registro ocorreu em **{ano_max}**, atingindo a marca de **{valor_max:,}** cabeças de gado.
    
    **Pergunta 2: Como evoluiu o número de cabeças de gado ao longo do tempo?**
    * **Resposta:** Os dados mostram um crescimento contínuo. O rebanho saiu de cerca de 92 milhões em 1974 para mais de 238 milhões em 2023, mais do que dobrando de tamanho ao longo das décadas.
    """)

    st.divider()

    # --- NOVA TABELA INTERATIVA (COM FILTRO) ---
    st.subheader("Exploração Interativa dos Dados")
    st.write("Utilize o filtro abaixo para selecionar um período específico e visualizar a evolução em detalhes.")

    ano_min = int(df["Ano"].min())
    ano_max_filtro = int(df["Ano"].max())
    
    # Slider para o usuário escolher o intervalo de anos
    anos_selecionados = st.slider(
        "Selecione o período (Ano Inicial - Ano Final):",
        min_value=ano_min,
        max_value=ano_max_filtro,
        value=(ano_min, ano_max_filtro)
    )

    # Filtrando a base de acordo com a escolha do usuário
    df_filtrado = df[(df["Ano"] >= anos_selecionados[0]) & (df["Ano"] <= anos_selecionados[1])]

    # Exibindo a tabela com colunas visuais
    st.dataframe(
        df_filtrado,
        column_config={
            "Ano": st.column_config.NumberColumn(format="%d"),
            "Cabeças de Gado": st.column_config.ProgressColumn(
                "Cabeças de Gado (Volume visual)",
                help="Barra comparativa baseada no valor máximo de todo o período",
                format="%d",
                min_value=0,
                max_value=int(valor_max),
            ),
        },
        hide_index=True,
        use_container_width=True
    )

    st.divider()

    # --- AULA 3 e 4: INDICADORES E GRÁFICOS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Anos Analisados", df.shape[0])
    
    media = df["Cabeças de Gado"].mean()
    col2.metric("Média (Cabeças)", f"{media:,.0f}")
    col3.metric("Maior Rebanho", f"{valor_max:,}")

    st.divider()

    # GRÁFICO 1: Linha do tempo (Evolução)
    fig_linha = px.line(
        df,
        x="Ano",
        y="Cabeças de Gado",
        title="Evolução Histórica do Rebanho Bovino (1974 em diante)",
        markers=True
    )
    st.plotly_chart(fig_linha, use_container_width=True)
    
    st.markdown("""
    **O que podemos observar?**
    Este gráfico demonstra a trajetória de crescimento do efetivo bovino no Brasil. É possível constatar uma forte tendência de subida constante ao longo das décadas, sem grandes quebras ou reduções significativas no número total de animais até atingir o pico recente.
    """)
    
    st.divider()

    # GRÁFICO 2: Barras (Comparação dos Top 10 anos)
    df_top10 = df.sort_values(by="Cabeças de Gado", ascending=False).head(10)
    
    fig_barra = px.bar(
        df_top10,
        x="Ano",
        y="Cabeças de Gado",
        title="Top 10 Anos com Maiores Rebanhos",
        color="Cabeças de Gado"
    )
    fig_barra.update_xaxes(type='category')
    st.plotly_chart(fig_barra, use_container_width=True)

    st.markdown("""
    **O que podemos observar?**
    Ao isolar os 10 anos com os maiores valores absolutos, nota-se que todos pertencem ao período mais recente (últimos 10 a 15 anos). Isso confirma que o rebanho atingiu seu volume máximo na história recente do país.
    """)
    
    st.divider()
    
    # --- EXEMPLO DE USO DA IA PARA O TRABALHO ---
    with st.expander("Exemplo de como a IA ajudou (Requisito da Aula 5)"):
        st.write("""
        **Problema encontrado:** O arquivo baixado do SIDRA/IBGE possuía um cabeçalho muito complexo, com células unidas, anos repetidos em várias linhas e muitos tipos de animais misturados. O `pd.read_csv` padrão do Pandas gerava erros na leitura das colunas.
        
        **Sugestão da IA e Solução:** A IA sugeriu que os dados fossem lidos primeiro como texto bruto através da função `open()`. Ajudou a criar um pequeno algoritmo em Python para capturar apenas a linha de anos e a linha específica da palavra "Brasil", saltando de 10 em 10 índices para extrair exclusivamente os dados de "Bovinos". O processo resultou em um DataFrame limpo e funcional.
        """)

except FileNotFoundError:
    st.error("Arquivo 'tabela3939.csv' não encontrado. Certifique-se de que ele está na mesma pasta do arquivo app.py.")
