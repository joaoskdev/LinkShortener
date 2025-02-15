from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)

# Configuração para usar o SQLite como banco de dados persistente
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///links.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativar o monitoramento de modificações

db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form.get('url')
    if original_url:
        # Gerar um código de link curto aleatório com 6 caracteres
        short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

        # Verificar se o código curto já existe no banco de dados (para evitar duplicação)
        existing_link = Link.query.filter_by(short_url=short_url).first()
        if existing_link:
            short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Gerar um novo código se o anterior já existir

        # Salvar o link no banco de dados
        new_link = Link(original_url=original_url, short_url=short_url)
        db.session.add(new_link)
        db.session.commit()

        # Exibir o link encurtado para o usuário
        return render_template('index.html', short_url=short_url, original_url=original_url)
    
    return redirect(url_for('index'))

@app.route('/<short_url>')
def redirect_to_original(short_url):
    # Buscar o link original pelo código curto
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)

# Garantir que o banco de dados seja criado dentro do contexto da aplicação
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Criar banco de dados, se não existir

    app.run(debug=True)
