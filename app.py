from flask import Flask, render_template, request, send_file
import pandas as pd
from validate_docbr import CPF, CNPJ
from io import BytesIO

app = Flask(__name__)


def validar_documento(documento):
    cpf = CPF()
    cnpj = CNPJ()
    documento_str = str(documento).strip()

    if len(documento_str) <= 11:
        documento_str = documento_str.zfill(11)
        if cpf.validate(documento_str):
            return 'FISICA'
    elif 12 <= len(documento_str) <= 14:
        documento_str = documento_str.zfill(14)
        if cnpj.validate(documento_str):
            return 'JURIDICA'

    if cpf.validate(documento_str.zfill(11)):
        return 'FISICA'
    elif cnpj.validate(documento_str.zfill(14)):
        return 'JURIDICA'
    else:
        return "Documento inválido"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Nenhum arquivo selecionado.'

        file = request.files['file']
        if file.filename == '':
            return 'Nenhum arquivo selecionado.'

        if file and file.filename.endswith('.xlsx'):
            df1 = pd.read_excel(file)

            # Obtém os nomes das colunas do formulário
            coluna_nome = request.form['coluna_nome']
            coluna_documento = request.form['coluna_documento']
            coluna_quantidade_on = request.form['coluna_quantidade_on']
            coluna_quantidade_pn = request.form.get('coluna_quantidade_pn', '')  # Campo opcional

            # Processa o DataFrame
            df2 = pd.DataFrame()
            df2['NOME'] = df1[coluna_nome]
            df2['TIPO_PESSOA'] = df1[coluna_documento].apply(validar_documento)
            df2['CPF_CNPJ'] = df1[coluna_documento]
            df2['ON'] = df1[coluna_quantidade_on]

            # Adiciona PN (usa 0 se não for fornecido)
            if coluna_quantidade_pn and coluna_quantidade_pn in df1.columns:
                df2['PN'] = df1[coluna_quantidade_pn]
            else:
                df2['PN'] = 0

            output = BytesIO()
            df2.to_csv(output, index=False, sep=',')
            output.seek(0)

            return send_file(output, as_attachment=True, download_name='base_votos.csv', mimetype='text/csv')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)