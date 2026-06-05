"""Cria o banco de dados e as tabelas. Execute uma vez antes de iniciar o app."""
from app import init_db
init_db()
print("Banco criado com sucesso em desafiofit.db")
