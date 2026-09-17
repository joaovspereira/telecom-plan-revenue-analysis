![Telecom Plan Revenue Analysis](assets/banner.svg)

[English](README.md) · **Português** · [Portfólio](https://github.com/joaovspereira)

# Telecom Plan Revenue Analysis

## Objetivo

Calcular faturas mensais corretamente e comparar receitas médias por cliente entre planos.

## O que foi implementado

Corrigi a cobrança duplicada de internet, o preenchimento de consumo ausente e a chave de mês. A implementação inclui meses de assinatura sem consumo e explicita cobrança integral, sem proporcionalidade, no mês de entrada e saída. A comparação estatística utiliza uma média mensal por cliente, evitando tratar meses do mesmo cliente como observações independentes. No exemplo sintético, a fatura calculada é US$ 30,09 e a do assinante sem consumo é US$ 20,00.

## Evidências e execução

[Notebook](notebooks/analysis.ipynb) · [Implementation](billing.py) · [Synthetic output](reports/synthetic_demo.json)

Foram verificados **5 testes automatizados**. Eles validam a implementação com dados sintéticos; não substituem a avaliação nos dados reais. Veja [VALIDATION.md](VALIDATION.md) para o registro e os limites da verificação.

Execute a partir da raiz do repositório, com Python 3.12:

```bash
python -m pip install -r requirements.txt
python billing.py
python -m unittest discover -s tests -v
python -m notebook notebooks/analysis.ipynb
```

As [instruções completas](README.md#run-locally) incluem a criação do ambiente virtual. Consulte [data/README.md](data/README.md) para os arquivos e campos esperados.

## Tecnologias

Python · pandas · NumPy · SciPy · billing rules · cohort comparison · Welch t-test

## Limitações e próximos passos

Totais de receita e p-valores do notebook antigo não foram reaproveitados: dependiam da fórmula incorreta. Os testes publicados conferem regras com dados inventados. A reexecução com os cinco CSVs originais continua pendente; a comparação entre planos é observacional.

Projeto educacional derivado do Data Science Bootcamp da TripleTen, revisado para publicação em setembro de 2026. Datasets originais não são redistribuídos. O aprendizado central desta revisão é tornar explícitos os pressupostos, as unidades de medida e os limites das conclusões.
