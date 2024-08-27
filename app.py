from flask import Flask, render_template, request, send_file
import pandas as pd
from validate_docbr import CPF, CNPJ
from io import BytesIO

app = Flask(__name__)

# Função para validar documento
def validar_documento(documento):
    cpf = CPF()
    cnpj = CNPJ()

    documento_str = str(documento).strip()  # Converte para string e remove espaços

    # Tentativa de validação com base no número de dígitos
    if len(documento_str) <= 11:
        # Preenche com zeros à esquerda, se necessário
        documento_str = documento_str.zfill(11)
        if cpf.validate(documento_str):
            return 'FISICA'
    elif 12 <= len(documento_str) <= 14:
        # Preenche com zeros à esquerda, se necessário
        documento_str = documento_str.zfill(14)
        if cnpj.validate(documento_str):
            return 'JURIDICA'
    
    # Caso falhe como CPF e CNPJ, tenta validar ambos
    if cpf.validate(documento_str.zfill(11)):
        return 'FISICA'
    elif cnpj.validate(documento_str.zfill(14)):
        return 'JURIDICA'
    else:
        return "Documento inválido"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verifica se um arquivo foi enviado
        if 'file' not in request.files:
            return 'Nenhum arquivo selecionado.'
        
        file = request.files['file']

        if file.filename == '':
            return 'Nenhum arquivo selecionado.'

        if file and file.filename.endswith('.xlsx'):
            # Lê o arquivo da memória
            df1 = pd.read_excel(file, dtype={'Documento do Participante': str})

            # Processa o DataFrame
            df2 = pd.DataFrame()
            df2['NOME'] = df1['Razão Social do Participante']

            # Aplica a validação e preenche a coluna TIPO_PESSOA
            df2['TIPO_PESSOA'] = df1['Documento do Participante'].apply(validar_documento)
            df2['CPF_CNPJ'] = df1['Documento do Participante']
            df2['ON'] = df1['Quantidade']
            df2['PN'] = 0  # Adiciona uma coluna 'PN' vazia

            # Salva o CSV na memória (BytesIO)
            output = BytesIO()
            df2.to_csv(output, index=False, sep=',')
            output.seek(0)

            # Envia o arquivo para download
            return send_file(output, as_attachment=True, download_name='base_votos.csv', mimetype='text/csv')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
