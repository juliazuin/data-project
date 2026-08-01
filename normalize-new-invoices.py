#!/usr/bin/env python3
"""
normaliza-new-invoices.py

Normaliza faturas (CSV exportado do Itaú) para um modelo simples:
    coluna 1: data       -> YYYY-MM-DD
    coluna 2: lancamento -> texto do lançamento
    coluna 3: valor      -> 0000.00 (ponto decimal, sinal preservado)

Modo padrão (sem argumentos):
    Varre a estrutura   invoices/<person>/new/*.csv
    Normaliza cada arquivo e salva em   invoices/<person>/<mesmo-nome>.csv
    (ou seja, "sobe de nível", saindo da pasta new/ e usando o mesmo nome)

    Estrutura esperada:
        invoices/
            julia/
                new/
                    2026-08.csv   -> normaliza -> invoices/julia/2026-08.csv
            joao/
                new/
                    2026-08.csv   -> normaliza -> invoices/joao/2026-08.csv

Uso:
    python3 normaliza-new-invoices.py
        # processa tudo em invoices/*/new/*.csv (pasta "invoices" no diretório atual)

    python3 normaliza-new-invoices.py --base-dir /caminho/para/invoices
        # mesma lógica, mas apontando para outra pasta base "invoices"

    python3 normaliza-new-invoices.py fatura1.csv fatura2.csv ...
        # modo manual: normaliza arquivos específicos e salva como
        # "normalizado-<nome-original>.csv" na mesma pasta do arquivo
"""

import csv
import glob
import re
import sys
from datetime import datetime
from pathlib import Path

# Posições das colunas no CSV original (0-indexed), conforme layout do Itaú:
# col 0 = vazio, col 1 = Data, col 2 = Lançamento, col 3 = Parcelamento, col 4 = Valor
COL_DATA = 1
COL_LANCAMENTO = 2
COL_VALOR = 4

DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")


def parse_data(valor: str) -> str:
    """Converte dd/mm/yyyy -> yyyy-mm-dd"""
    return datetime.strptime(valor.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


def parse_valor(valor: str) -> str:
    """
    Converte 'R$  4.590,36' ou 'R$  -4.042,23' -> '4590.36' / '-4042.23'
    (remove símbolo, separador de milhar '.', troca ',' decimal por '.')
    """
    limpo = valor.replace("R$", "").strip()
    limpo = limpo.replace(".", "").replace(",", ".")
    numero = float(limpo)
    return f"{numero:.2f}"


def linhas_normalizadas_de(caminho_entrada: Path) -> list:
    """Lê o CSV de fatura bruto e devolve as linhas já normalizadas."""
    linhas = []

    with open(caminho_entrada, encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        for linha in leitor:
            if len(linha) <= COL_VALOR:
                continue

            data_bruta = linha[COL_DATA].strip()
            lancamento = linha[COL_LANCAMENTO].strip()
            valor_bruto = linha[COL_VALOR].strip()

            # Só processa linhas cuja coluna de Data tenha uma data válida
            # (ignora cabeçalho, linhas em branco, rodapé, subtotal, etc.)
            if not DATE_RE.match(data_bruta):
                continue
            if not valor_bruto:
                continue

            try:
                data_norm = parse_data(data_bruta)
                valor_norm = parse_valor(valor_bruto)
            except ValueError:
                # linha que "parece" data/valor mas não é (ex: erro de parsing) -> ignora
                continue

            linhas.append([data_norm, lancamento, valor_norm])

    return linhas


def escreve_csv(caminho_saida: Path, linhas: list) -> None:
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(linhas)


def normaliza_arquivo(caminho_entrada: Path):
    """Modo manual: salva como 'normalizado-<nome>.csv' ao lado do arquivo original."""
    linhas = linhas_normalizadas_de(caminho_entrada)
    caminho_saida = caminho_entrada.with_name(f"normalizado-{caminho_entrada.name}")
    escreve_csv(caminho_saida, linhas)
    return caminho_saida, len(linhas)


def normaliza_pasta_invoices(base_dir: Path):
    """
    Varre base_dir/<person>/new/*.csv, normaliza cada fatura e salva em
    base_dir/<person>/<mesmo-nome>.csv (mesmo nome do arquivo, um nível acima
    da pasta 'new').
    """
    encontrados = False

    for pasta_new in sorted(base_dir.glob("*/new")):
        person = pasta_new.parent.name
        arquivos_csv = sorted(pasta_new.glob("*.csv"))

        if not arquivos_csv:
            continue

        for arquivo in arquivos_csv:
            encontrados = True
            linhas = linhas_normalizadas_de(arquivo)
            caminho_saida = pasta_new.parent / arquivo.name  # invoices/<person>/<mesmo-nome>.csv
            escreve_csv(caminho_saida, linhas)
            print(f"[ok] {person}: {arquivo} -> {caminho_saida} ({len(linhas)} lançamentos)")

    if not encontrados:
        print(f"Nenhuma fatura encontrada em '{base_dir}/<pessoa>/new/*.csv'.")


def main():
    argumentos = sys.argv[1:]

    # Modo: --base-dir <caminho>  (ou nenhum argumento -> usa "invoices" no diretório atual)
    if not argumentos or argumentos[0] == "--base-dir":
        if argumentos and argumentos[0] == "--base-dir":
            if len(argumentos) < 2:
                print("Uso: normaliza-new-invoices.py --base-dir <caminho>")
                sys.exit(1)
            base_dir = Path(argumentos[1])
        else:
            base_dir = Path("invoices")

        if not base_dir.exists():
            print(f"[erro] pasta base não encontrada: {base_dir}")
            sys.exit(1)

        normaliza_pasta_invoices(base_dir)
        return

    # Modo manual: arquivos específicos passados como argumentos
    arquivos = [Path(a) for a in argumentos]

    for arquivo in arquivos:
        if not arquivo.exists():
            print(f"[erro] arquivo não encontrado: {arquivo}")
            continue

        saida, total = normaliza_arquivo(arquivo)
        print(f"[ok] {arquivo.name} -> {saida.name} ({total} lançamentos)")


if __name__ == "__main__":
    main()