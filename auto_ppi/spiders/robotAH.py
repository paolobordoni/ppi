# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest, Request
import logging

class PpiSpider3(scrapy.Spider):
    name = 'robotAH'
    allowed_domains = ['ppiassistencial_antigo.saude.mg.gov.br']
    start_urls = ['http://ppiassistencial_antigo.saude.mg.gov.br/municipioTabelaUnificada.php']
    competencia = '201806' #Competendia yyyymm
    atendimento = '312230' #Atendimento 0=Todas, XXXXXX=Cod. da Regiao
    complexidade = '3' #Complexidade 0=Todas 2=Media 3=Alta
    modAtendimento = '2' #Registro 0=Todas 1=Ambulatorial 2=Hospitalar
    arquivo = name + competencia + '.csv'
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv',
        'FEED_URI': arquivo
    }

    def parse(self,response):
        data = {'rbFoco': '1', #Foco da Pesquisa 0=Origem, 1=Atendimento)
            'cbCompetencia': self.competencia,
            'rbReferencia': '1', #Origem 0=Minicipio, 1=Micro Regiao
            'cbOrigem': '0', #Origem 0=Todas, XXXXXX=Cod. da Regiao
            'cbAtendimento': self.atendimento,
            'cbGrupo': '', #Grupo 0=Todas
            'cbSubgrupo': '0', #SubGrupo 0=Todas
            'cbForma': '0', #Forma de Organizacao 0=Todas
            'cbProcedimento': '0', #Procedimento 0=Todas
            'cbComplexidade': self.complexidade,
            'cbRegistro': self.modAtendimento,
            'rbRecurso': '1',
            'cbCodigo': 'codigo',
            'cbDiscriminar': '5'
            }

        yield FormRequest(url='http://ppiassistencial.saude.mg.gov.br/relatorioTabelaUnificada.php',method='POST', formdata=data, callback=self.parse_dados_grupo)

    def parse_dados_grupo(self, response):

        trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

        #trs_num = 3

        data_tr = 1

        while data_tr < trs_num:

            tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

            tr_titulo = tr.xpath('.//td//text()')[0].extract()

            if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                print("GRUPO: " + str(tr_titulo))     

                url = tr.xpath('.//td//a/@href').extract_first()

                url = response.urljoin(url)

                yield Request(url, callback=self.parse_dados_subgrupo)

            data_tr += 1

    def parse_dados_subgrupo(self, response):

        trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

        if trs_num == 1:

            tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[1]

            tr_titulo = tr.xpath('.//td//text()')[0].extract()

            print("SUBGRUPO COM 1: " + str(tr_titulo))

            if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                url = tr.xpath('.//td//a/@href')[0].extract()

                url = response.urljoin(url)

                yield Request(url, callback=self.parse_dados_organizacao)

        else:

            data_tr = 1

            while data_tr < trs_num:

                tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

                tr_titulo = tr.xpath('.//td//text()')[0].extract()

                print("SUBGRUPO: " + str(tr_titulo))

                if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                    url = tr.xpath('.//td//a/@href')[0].extract()

                    url = response.urljoin(url)

                    yield Request(url, callback=self.parse_dados_organizacao)

                data_tr += 1

    def parse_dados_organizacao(self, response):

        trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

        if trs_num == 1:

            tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[1]

            tr_titulo = tr.xpath('.//td//text()')[0].extract()

            #print("ORGANIZACAO COM 1: " + str(tr_titulo))

            if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                url = tr.xpath('.//td//a/@href')[0].extract()

                url = response.urljoin(url)

                yield Request(url, callback=self.parse_dados_procedimento)

        else:

            data_tr = 1

            while data_tr < trs_num:

                tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

                tr_titulo = tr.xpath('.//td//text()')[0].extract()

                #print("ORGANIZACAO: " + str(tr_titulo))

                if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                    url = tr.xpath('.//td//a/@href')[0].extract()

                    url = response.urljoin(url)

                    yield Request(url, callback=self.parse_dados_procedimento)

                data_tr += 1


    def parse_dados_procedimento(self, response):

        table_title = response.xpath('//table[@class="tbImprimirTabela"]//tr[1]/td[1]//text()').extract_first().split()

        if (len(table_title) == 2) and (table_title[1]) == "Origem":
            grupo = response.xpath('//table[3]//tr[1]/td/text()').extract_first()
            subgrupo = response.xpath('//table[3]//tr[2]/td/text()').extract_first()
            organizacao = response.xpath('//table[3]//tr[3]/td/text()').extract_first()
            procedimento = ''

            trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

            if trs_num == 1:

                #print("UM REGISTRO: ----------------------------")

                tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[1]

                tr_titulo = tr.xpath('.//td//text()')[0].extract()

                #print("PROCEDIMENTO COM 1: " + str(tr_titulo))

                if (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                    municipio = tr.xpath('.//td//text()')[0].extract()
                    quantidade = tr.xpath('.//td//text()')[1].extract()
                    valor = tr.xpath('.//td//text()')[2].extract()

                    yield {
                        'Competencia' : self.competencia[0]+self.competencia[1]+self.competencia[2]+self.competencia[3]+'-'+self.competencia[4]+self.competencia[5]+'-01',
                        #'Atendimento' : self.atendimento,
                        'Complexidade' :   self.complexidade,
                        'Atendimento' : self.modAtendimento,
                        'Grupo' : grupo.strip(),
                        'Subgrupo' : subgrupo.strip(),
                        'Organizacao' : organizacao.strip(),
                        'Procedimento' : procedimento.strip(),
                        'Municipio' : municipio.strip(),
                        'Quantidade' : quantidade.strip(),
                        'Valor' : valor.strip()
                        }

            else:

                #print("MAIS DE UM REGISTRO: ----------------------------")

                data_tr = 1

                while data_tr < trs_num:

                    tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

                    tr_titulo = tr.xpath('.//td//text()')[0].extract()

                    if (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                        municipio = tr.xpath('.//td//text()')[0].extract()
                        quantidade = tr.xpath('.//td//text()')[1].extract()
                        valor = tr.xpath('.//td//text()')[2].extract()

                    yield {
                        'Competencia' : self.competencia[0]+self.competencia[1]+self.competencia[2]+self.competencia[3]+'-'+self.competencia[4]+self.competencia[5]+'-01',
                        #'Atendimento' : self.atendimento,
                        'Complexidade' :   self.complexidade,
                        'Atendimento' : self.modAtendimento,
                        'Grupo' : grupo.strip(),
                        'Subgrupo' : subgrupo.strip(),
                        'Organizacao' : organizacao.strip(),
                        'Procedimento' : procedimento.strip(),
                        'Municipio' : municipio.strip(),
                        'Quantidade' : quantidade.strip(),
                        'Valor' : valor.strip()
                        }

                    data_tr += 1

        else:

            #print("ENTROU NO ELSE: ----------------------------")

            trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

            if trs_num == 1:

                #print("UM REGISTRO: ----------------------------")

                tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[1]

                tr_titulo = tr.xpath('.//td//text()')[0].extract()

                #print("PROCEDIMENTO COM 1: " + str(tr_titulo))

                if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                    url = tr.xpath('.//td//a/@href')[0].extract()

                    url = response.urljoin(url)

                    yield Request(url, callback=self.parse_dados_origem)

            else:

                #print("MAIS DE UM REGISTRO: ----------------------------")

                data_tr = 1

                while data_tr < trs_num:

                    tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

                    tr_titulo = tr.xpath('.//td//text()')[0].extract()

                    #print("PROCEDIMENTO: " + str(tr_titulo))

                    if (tr_titulo.strip() != "SADT") and (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                        url = tr.xpath('.//td//a/@href')[0].extract()

                        url = response.urljoin(url)

                        yield Request(url, callback=self.parse_dados_origem)

                    data_tr += 1   


    def parse_dados_origem(self, response):

        grupo = response.xpath('//table[3]//tr[1]/td/text()').extract_first()
        subgrupo = response.xpath('//table[3]//tr[2]/td/text()').extract_first()
        organizacao = response.xpath('//table[3]//tr[3]/td/text()').extract_first()

        if (response.xpath('//table[3]//tr[4]/td/text()').extract_first()):
            procedimento = response.xpath('//table[3]//tr[4]/td/text()').extract_first()

        else:
            procedimento = '0 Programacao por forma de Organizacao'



        trs_num = len(response.xpath('//table[@class="tbImprimirTabela"]//tr')) - 1

        if trs_num == 1:

            #print("UM REGISTRO: ----------------------------")

            tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[1]

            tr_titulo = tr.xpath('.//td//text()')[0].extract()

            #print("PROCEDIMENTO COM 1: " + str(tr_titulo))

            if (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                municipio = tr.xpath('.//td//text()')[0].extract()
                quantidade = tr.xpath('.//td//text()')[1].extract()
                valor = tr.xpath('.//td//text()')[2].extract()

                yield {
                    'Competencia' : self.competencia[0]+self.competencia[1]+self.competencia[2]+self.competencia[3]+'-'+self.competencia[4]+self.competencia[5]+'-01',
                    #'Atendimento' : self.atendimento,
                    'Complexidade' :   self.complexidade,
                    'Atendimento' : self.modAtendimento,
                    'Grupo' : grupo.strip(),
                    'Subgrupo' : subgrupo.strip(),
                    'Organizacao' : organizacao.strip(),
                    'Procedimento' : procedimento.strip(),
                    'Municipio' : municipio.strip(),
                    'Quantidade' : quantidade.strip(),
                    'Valor' : valor.strip()
                    }

        else:

            #print("MAIS DE UM REGISTRO: ----------------------------")

            data_tr = 1

            while data_tr < trs_num:

                tr = response.xpath('//table[@class="tbImprimirTabela"]//tr')[data_tr]

                tr_titulo = tr.xpath('.//td//text()')[0].extract()

                if (tr_titulo.strip() != "Soma:") and (tr_titulo.strip() != ""):

                    municipio = tr.xpath('.//td//text()')[0].extract()
                    quantidade = tr.xpath('.//td//text()')[1].extract()
                    valor = tr.xpath('.//td//text()')[2].extract()

                yield {
                    'Competencia' : self.competencia[0]+self.competencia[1]+self.competencia[2]+self.competencia[3]+'-'+self.competencia[4]+self.competencia[5]+'-01',
                    #'Atendimento' : self.atendimento,
                    'Complexidade' :   self.complexidade,
                    'Atendimento' : self.modAtendimento,
                    'Grupo' : grupo.strip(),
                    'Subgrupo' : subgrupo.strip(),
                    'Organizacao' : organizacao.strip(),
                    'Procedimento' : procedimento.strip(),
                    'Municipio' : municipio.strip(),
                    'Quantidade' : quantidade.strip(),
                    'Valor' : valor.strip()
                    }

                data_tr += 1
