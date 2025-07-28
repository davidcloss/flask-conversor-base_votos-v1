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
            coluna_serie_1 = request.form['coluna_serie_1']
            coluna_serie_2 = request.form.get('coluna_serie_2', '')  # Campo opcional

            # Processa o DataFrame
            df2 = pd.DataFrame()
            df2['NOME'] = df1[coluna_nome]
            df2['TIPO_PESSOA'] = df1[coluna_documento].apply(validar_documento)
            df2['CPF_CNPJ'] = df1[coluna_documento]

            # Adiciona SERIE_1 corretamente, preenchendo NaN com 0 e convertendo para inteiro
            if coluna_serie_1 and coluna_serie_1 in df1.columns:
                df2['SERIE_1'] = df1[coluna_serie_1].fillna(0).astype(int)
            else:
                df2['SERIE_1'] = 0

            # Adiciona SERIE_2 corretamente, preenchendo NaN com 0 e convertendo para inteiro
            if coluna_serie_2 and coluna_serie_2 in df1.columns:
                df2['SERIE_2'] = df1[coluna_serie_2].fillna(0).astype(int)
            else:
                df2['SERIE_2'] = 0

            output = BytesIO()
            df2.to_csv(output, index=False, sep=',')
            output.seek(0)

            return send_file(output, as_attachment=True, download_name='base_votos.csv', mimetype='text/csv')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)