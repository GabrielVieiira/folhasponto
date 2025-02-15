import streamlit as st
import PyPDF2
import re

def extract_holerite_info(pdf_reader):
    employee_dict = {}
    for page_number, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text()

        matricula_match = re.search(r"CNPJ: CC:\s*(\d+)\s*Cód", text)

        nome_match = re.search(r"(.+?)(?=\s*Nome do Funcionário)", text)

        if matricula_match and nome_match:
            matricula = matricula_match.group(1).strip()
            nome = nome_match.group(1).strip()

            employee_dict[matricula] = {"name": nome, "page": page_number}

    return employee_dict

def extract_ponto_info(pdf_reader):
    employee_dict = {}
    for page_number, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text()

        name_match = re.search(r"Funcionário\s+(.+?)\s+Departamento", text)
        matricula_match = re.search(r"Matrícula\s+(\d+)\s+Admissão", text)

        if name_match and matricula_match:
            name = name_match.group(1).strip()
            matricula = matricula_match.group(1).strip()
            employee_dict[matricula] = {"name": name, "page": page_number}
    return employee_dict

def detect_document_type(pdf_reader):
    for page in pdf_reader.pages[:3]:
        text = page.extract_text()
        if re.search(r"CNPJ: CC:", text) and re.search(r"Cód", text):
            return "holerite"
        elif re.search(r"Matrícula", text) and re.search(r"Admissão", text):
            return "ponto"
    return "desconhecido"

st.title("Visualizador de Folhas de Ponto e Holerites")

uploaded_file = st.file_uploader("Carregue o arquivo PDF", type="pdf")

if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None

if uploaded_file:
    if uploaded_file != st.session_state.uploaded_file_path:
        st.session_state.dicionario = {}
        
        st.session_state.uploaded_file_path = uploaded_file
    
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        
        document_type = detect_document_type(pdf_reader)
        
        if document_type == "holerite":
            dicionario = extract_holerite_info(pdf_reader)
        elif document_type == "ponto":
            dicionario = extract_ponto_info(pdf_reader)
        else:
            st.warning("Tipo de documento não identificado.")
            dicionario = {}
        
        st.session_state["dicionario"] = dicionario
    else:
        dicionario = st.session_state.get("dicionario", {})

    if dicionario:
        matriculas_selecionadas = st.sidebar.multiselect(
            "Selecione as matrículas para visualizar os detalhes",
            options=list(dicionario.keys()),
            format_func=lambda x: f"{x} - {dicionario[x]['name']}"
        )

        if matriculas_selecionadas:
            paginas_selecionadas = [dicionario[matricula]["page"] for matricula in matriculas_selecionadas]
            resumo_paginas = ",".join(map(str, paginas_selecionadas))
            st.subheader("Resumo das Páginas Selecionadas")
            st.write(f"Páginas: {resumo_paginas}")
            st.write(' ')
            for matricula in matriculas_selecionadas:
                st.write(f"**Matrícula:** {matricula}")
                st.write(f"**Nome:** {dicionario[matricula]['name']}")
                st.write(f"**Página:** {dicionario[matricula]['page']}")
                st.write(f"")
        else:
            st.info("Selecione ao menos uma matrícula para visualizar os detalhes.")
    else:
        st.warning("Nenhuma informação encontrada no arquivo PDF.")
else:
    st.info("Por favor, carregue um arquivo PDF.")
