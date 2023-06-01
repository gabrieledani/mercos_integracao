from cleantext import clean
import pdfplumber
import os
import datetime

def processa_file(filename,dir_edi,dir_pdf,dir_log):
    log_file = open(os.path.join(dir_log,'app_log.txt'),'a')

    if dir_pdf:
        pdf = pdfplumber.open(os.path.join(dir_pdf,filename))
    else:
        pdf = pdfplumber.open(filename)

    num_pages = len(pdf.pages)
    
    #dir = dir_edi#filename[:filename.rfind('/')]

    achou_produtos = 0
    qtde_produtos = 0
    txt_produtos = ''

    for num_page in range(num_pages):
        table = pdf.pages[num_page].extract_table()
        
        ordem_compra = 0
        obs = 0
        for line in table:
            new_line = [x.replace('\n',' ') for x in line if x is not None]

            
            if new_line[0].find('Pedido') > 0:
                ini = new_line[0].find('Pedido')+10
                pedido =new_line[0][ini:]
            elif new_line[0].find('Orçamento') > 0:
                ini = new_line[0].find('Orçamento')+13
                pedido =new_line[0][ini:]
                
            if new_line[0].startswith('Cliente') > 0:
                ini = new_line[0].find('Cliente')+9
                fin = new_line[0].find('Nome Fantasia')-1
                cliente = clean(new_line[0][ini:fin]).upper()
                #print('Cliente =',cliente)
                ini = new_line[0].find('CNPJ')+6
                fin = new_line[0].find('Inscrição Estadual')-1
                cnpj = new_line[0][ini:fin].replace('.','').replace('/','').replace('-','')
                #print('CNPJ=',cnpj)        
                    
            if new_line[0].startswith('Qtde. Total'):
                achou_produtos = 0

            if achou_produtos == 1:
                qtde_produtos = qtde_produtos + 1
                
                cod_item = new_line[0][new_line[0].find('Cód. Interno:')+14:-1]
                desc_item = clean(new_line[0][:new_line[0].find('Cód. Interno:')-2]).upper()
                
                desc_item = desc_item[:25]
                quantidade = new_line[1]
                preco = new_line[3][3:]
                preco = preco.replace(',','')

                if new_line[0].find('Cód. Interno:') > 0:
                    txt_produtos = txt_produtos + 'PP2'+'{:30}'.format(cod_item)+str(quantidade).zfill(9)+'{:25}'.format(desc_item)+preco.zfill(9)+'0'*41+' '*11+'\n'

            if new_line[0].startswith('Produto'):
                qtde_produtos = 0
                achou_produtos = 1

            if new_line[0].startswith('Condição de Pagamento'):
                cond_pagto = new_line[0][23:]
                dt_emis = new_line[1][new_line[1].find(':')+2:]

            if new_line[0].startswith('Ordem de Compra'):
                ordem_compra = new_line[0][25:]
                #print('oc',ordem_compra)

            if new_line[0].startswith('Informações Adicionais'):
                obs = new_line[0][24:]
                #print('obs',obs)

            if new_line[0].startswith('Todos os valores'):
                #cria arquivo do EDI
                #print('cria arquivo '+'EXPORTA_PEDIDO_HENGST_'+cliente+'_'+pedido+'.dir')
                #log_file.write(datetime.datetime.now+'--cria arquivo '+'EXPORTA_PEDIDO_HENGST_'+cliente+'_'+pedido+'.dir')
                edi_filename = 'EXPORTA_PEDIDO_HENGST_'+cliente.replace(' ','_')+'_'+pedido.replace(' ','_')+'.dir'
                log_file.write(str(datetime.datetime.now())+edi_filename+'\n')
                edi_arquivo = open(os.path.join(dir_edi,edi_filename),'w')

                #cria linha e identificação do cliente
                edi_arquivo.write('ITP6010000000000000000000'+str(cnpj)+'03429968000126'+'00000000'+'        ')
                edi_arquivo.write('{:25}'.format(cliente))
                edi_arquivo.write('HENGST INDUSTRIA DE FILTR')
                edi_arquivo.write(' '*9+'\n')

                #cria linha e identificação do pedido
                edi_arquivo.write('PP1'+str(qtde_produtos).zfill(4)+'0'+'{:12}'.format(str(pedido)))
                
                emissao = dt_emis[:7]+dt_emis[9:]#17/11/2022
                #edi_arquivo.write(str(datetime.datetime.today().year)[2:]+str(datetime.datetime.today().month).zfill(2)+str(datetime.datetime.today().day).zfill(2))
                edi_arquivo.write(emissao.replace('/',''))
                edi_arquivo.write('00          ')
                #edi_arquivo.write(str(datetime.datetime.today().year)[2:]+str(datetime.datetime.today().month).zfill(2)+str(datetime.datetime.today().day).zfill(2))
                edi_arquivo.write(emissao.replace('/',''))
                edi_arquivo.write(' '*84+'\n')
                
                edi_arquivo.write('AE3'+str(cnpj)+'0'*28+'\n')

                #print('antes'+str(cond_pagto)+str(ordem_compra)+str(obs))

                if (cond_pagto[:2] != '--') or (ordem_compra != 0) or (obs != 0):
                
                    if cond_pagto[:2] != '--':
                        cond_pagto = '{:40}'.format('COND PAGTO:'+str(cond_pagto))
                    if ordem_compra != 0:
                        ordem_compra = '{:40}'.format('ORD COMPRA:'+str(ordem_compra))
                    if obs != 0:
                        obs = '{:40}'.format('OBS:'+str(obs))
                    
                    #print('TE1'+str(cond_pagto)+str(ordem_compra)+str(obs))
                    edi_arquivo.write('TE1'+str(cond_pagto)+str(ordem_compra)+str(obs)+'\n')

                #cria linhas dos produtos
                edi_arquivo.write(txt_produtos)
                edi_arquivo.write('FTP0000000000000000000000000000000')
                edi_arquivo.close()
                
                cliente = ''
                pedido = ''
                txt_produtos = ''
                qtde_produtos = 0
                cnpj = ''
                dt_emis = ''
                achou_produtos = 0
    pdf.close()
    return edi_filename
