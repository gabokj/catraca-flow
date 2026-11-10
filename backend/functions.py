import os
import re
import random
import sqlite3
from datetime import datetime, date, timedelta

from config import DB_TYPE, SQLITE_PATH, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

def get_db_connection():
    if DB_TYPE == "mysql":
        import pymysql
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    if DB_TYPE == "sqlite":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                turma TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER,
                cpf TEXT NOT NULL,
                motivo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                qr_codigo INTEGER NOT NULL,
                qr_instrucoes TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE SET NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocorrencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER,
                cpf TEXT NOT NULL,
                tipo TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES alunos (id) ON DELETE SET NULL
            )
        """)
        conn.commit()
    conn.close()

def obter_data_hora():
    agora = datetime.now()
    return {
        "data": agora.strftime("%d/%m/%y"),
        "hora": agora.strftime("%H:%M"),
        "agora": agora
    }

def buscar_aluno(cpf: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()

    if DB_TYPE == "sqlite":
        cursor.execute("SELECT id, cpf, nome, turma FROM alunos WHERE cpf = ? LIMIT 1", (cpf,))
    else:
        cursor.execute("SELECT id, cpf, nome, turma FROM alunos WHERE cpf = %s LIMIT 1", (cpf,))
    
    row = cursor.fetchone()
    if row:
        aluno = dict(row)
        conn.close()
        return aluno

    cpf_limpo = re.sub(r"\D", "", cpf)
    nome = f"Aluno {cpf_limpo}"
    turma = "Geral"

    if DB_TYPE == "sqlite":
        cursor.execute(
            "INSERT INTO alunos (cpf, nome, turma, created_at) VALUES (?, ?, ?, datetime('now'))",
            (cpf, nome, turma)
        )
        conn.commit()
        aluno_id = cursor.lastrowid
    else:
        cursor.execute(
            "INSERT INTO alunos (cpf, nome, turma, created_at) VALUES (%s, %s, %s, NOW())",
            (cpf, nome, turma)
        )
        aluno_id = cursor.lastrowid

    conn.close()
    return {
        "id": aluno_id,
        "cpf": cpf,
        "nome": nome,
        "turma": turma
    }

def obter_codigo_qr(tipo: str, motivo: str, hora_atual: str):
    try:
        parts = hora_atual.split(":")
        h = int(parts[0])
        m = int(parts[1])
    except Exception:
        now = datetime.now()
        h, m = now.hour, now.minute

    minutos_totais = h * 60 + m

    entrada_inicio = 7 * 60        # 07:00
    entrada_fim = 7 * 60 + 40      # 07:40
    atraso_leve = 7 * 60 + 41      # 07:41
    atraso_moderado = 7 * 60 + 50  # 07:50
    atraso_grave = 7 * 60 + 51     # 07:51
    saida_inicio = 17 * 60 + 20    # 17:20
    saida_fim = 17 * 60 + 50       # 17:50

    if tipo == "entrada":
        if entrada_inicio <= minutos_totais <= entrada_fim:
            return None
        if atraso_leve <= minutos_totais <= atraso_moderado:
            return {
                "codigo": random.randint(100, 200),
                "instrucoes": "Este ticket deve ser apresentado na portaria/coordenação. Entrada com atraso leve (liberação normal)."
            }
        if minutos_totais >= atraso_grave:
            return {
                "codigo": random.randint(300, 400),
                "instrucoes": "Atraso significativo. O aluno/usuário deve dirigir-se ao setor de apoio/coordenação."
            }
        return {
            "codigo": random.randint(100, 200),
            "instrucoes": "Entrada fora do horário padrão com registro de catraca."
        }

    elif tipo == "saida":
        if saida_inicio <= minutos_totais <= saida_fim:
            return None
        return {
            "codigo": random.randint(500, 600),
            "instrucoes": "Saída fora do horário padrão registrada."
        }

    elif tipo == "saida_apoio":
        codigo = random.randint(500, 600)
        responsaveis = ["Coordenação A", "Coordenação B", "Supervisão", "Apoio Geral"]
        responsavel = random.choice(responsaveis)
        return {
            "codigo": codigo,
            "instrucoes": f"Saída autorizada pelo setor de apoio. Responsável: {responsavel}."
        }

    elif tipo == "saida_esporte":
        return {
            "codigo": random.randint(700, 800),
            "instrucoes": "Saída autorizada para atividade esportiva. Horário restrito. Manter autorização em mãos."
        }

    elif tipo == "saida_biblioteca":
        return {
            "codigo": random.randint(900, 949),
            "instrucoes": "Saída autorizada para biblioteca / pesquisa / estudos externos."
        }

    elif tipo == "saida_tutor":
        return {
            "codigo": random.randint(950, 999),
            "instrucoes": "Saída autorizada por orientação ou tutor de projeto/TCC."
        }

    elif tipo == "cracha_esquecimento":
        return {
            "codigo": random.randint(200, 249),
            "instrucoes": "Esquecimento de crachá/cartão de identificação. Permitido 2x no mês. Na 3ª vez, dirigir-se à recepção/apoio."
        }

    elif tipo == "cracha_perda":
        return {
            "codigo": random.randint(250, 299),
            "instrucoes": "Perda de crachá/cartão de identificação. Solicitar 2ª via na secretaria. Permitido 3x na semana."
        }

    elif tipo == "uniforme":
        return {
            "codigo": random.randint(400, 449),
            "instrucoes": "Sem uniforme ou vestimenta padrão. Permitido 1x no mês. Na 2ª vez, encaminhamento à coordenação."
        }

    return {
        "codigo": random.randint(100, 500),
        "instrucoes": f"Ticket gerado para {motivo}."
    }

def verificar_limite(cpf: str, tipo: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    hoje = date.today()

    if tipo in ("esquecimento", "uniforme"):
        primeiro_dia = hoje.replace(day=1)
        if hoje.month == 12:
            ultimo_dia = hoje.replace(day=31)
        else:
            proximo_mes = hoje.replace(month=hoje.month + 1, day=1)
            ultimo_dia = proximo_mes - timedelta(days=1)
        
        limite = 2 if tipo == "esquecimento" else 1
        data_ini = primeiro_dia.isoformat()
        data_fim = ultimo_dia.isoformat()

    elif tipo == "perda":
        # Segunda-feira da semana
        segunda = hoje - timedelta(days=hoje.weekday())
        domingo = segunda + timedelta(days=6)
        limite = 3
        data_ini = segunda.isoformat()
        data_fim = domingo.isoformat()
    else:
        conn.close()
        return True

    if DB_TYPE == "sqlite":
        cursor.execute(
            "SELECT COUNT(*) as total FROM ocorrencias WHERE cpf = ? AND tipo = ? AND data BETWEEN ? AND ?",
            (cpf, tipo, data_ini, data_fim)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) as total FROM ocorrencias WHERE cpf = %s AND tipo = %s AND data BETWEEN %s AND %s",
            (cpf, tipo, data_ini, data_fim)
        )

    row = cursor.fetchone()
    total = row["total"] if isinstance(row, dict) else row[0]
    conn.close()
    return total < limite

def registrar_ocorrencia(cpf: str, tipo: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    hoje_iso = date.today().isoformat()

    if DB_TYPE == "sqlite":
        cursor.execute(
            "INSERT INTO ocorrencias (cpf, tipo, data, created_at) VALUES (?, ?, ?, datetime('now'))",
            (cpf, tipo, hoje_iso)
        )
        conn.commit()
    else:
        cursor.execute(
            "INSERT INTO ocorrencias (cpf, tipo, data, created_at) VALUES (%s, %s, %s, NOW())",
            (cpf, tipo, hoje_iso)
        )
    conn.close()

def criar_ticket(cpf: str, motivo: str, tipo: str, qr: dict) -> dict:
    aluno = buscar_aluno(cpf)
    data_hora = obter_data_hora()
    hoje_iso = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    if DB_TYPE == "sqlite":
        cursor.execute("""
            INSERT INTO tickets (aluno_id, cpf, motivo, tipo, qr_codigo, qr_instrucoes, data, hora, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            aluno.get("id"),
            cpf,
            motivo,
            tipo,
            qr["codigo"],
            qr["instrucoes"],
            hoje_iso,
            data_hora["hora"]
        ))
        conn.commit()
        ticket_id = cursor.lastrowid
    else:
        cursor.execute("""
            INSERT INTO tickets (aluno_id, cpf, motivo, tipo, qr_codigo, qr_instrucoes, data, hora, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            aluno.get("id"),
            cpf,
            motivo,
            tipo,
            qr["codigo"],
            qr["instrucoes"],
            hoje_iso,
            data_hora["hora"]
        ))
        ticket_id = cursor.lastrowid

    conn.close()

    return {
        "id": ticket_id,
        "aluno": aluno,
        "motivo": motivo,
        "tipo": tipo,
        "qr": qr,
        "data": data_hora["data"],
        "hora": data_hora["hora"]
    }

