import streamlit as st
import PyPDF2
import re

def extract_employee_info(pdf_reader):
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

st.title("Visualizador de Folhas de Ponto")

uploaded_file = st.file_uploader("Carregue o arquivo PDF", type="pdf")

if uploaded_file:
    if "dicionario" not in st.session_state:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        dicionario = extract_employee_info(pdf_reader)
        st.session_state["dicionario"] = dicionario
    else:
        dicionario = st.session_state["dicionario"]

    if dicionario:
        matriculas_selecionadas = st.sidebar.multiselect(
            "Selecione as matrículas para visualizar os detalhes",
            options=list(dicionario.keys()),
            format_func=lambda x: f"{x} - {dicionario[x]['name']}"
        )

        if matriculas_selecionadas:
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