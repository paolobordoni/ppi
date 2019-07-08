# Spider PPI - Scrapy
Automatização de coleta de dados do site da PPI (Programação Pactuada e Integrada).

Estes *spiders* foram escritos utilizando o framework: [Scrapy.org](https://scrapy.org/)

Fonte de Dados: [PPI](http://ppiassistencial.saude.mg.gov.br/municipioTabelaUnificada.php)



## Spiders
Os *spiders* estão no diretório `auto_ppi/spiders/`, sendo:

* robotMA: coleta Média Ambulatorial
* robotAA: coleta Alta Ambulatorial
* robotMH: coleta Média Hospitalar
* robotAH: coleta Alta Hospitalar

## Como Utilizar

É possível executar os spiders individualmente através do comando
```
scrapy crawl <sipder_name> -o "arquivo.csv" -t csv
```
Ex: 
```
scrapy crawl robotAA -o "arquivo.csv" -t csv
```

Também é possível executar todos de uma só vez através do comando:
```
python <caminho>/auto_ppi/allrobots.py
```
