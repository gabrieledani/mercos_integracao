# Import libraries
import configparser
import os
import datetime

import processa_file_pdf

config = configparser.ConfigParser()
config.read('config.ini')

dir_pdf = config['CAMINHO_PDF']['dir_pdf']
dir_edi = config['CAMINHO_EDI']['dir_edi']
dir_log = config['LOG']['dir_log']

log_file = open(os.path.join(dir_log,'app_log.txt'),'a')

file = 'pedido_8000.pdf'

if __name__ == '__main__':
    #Read new e-mails
    print('Start')
    log_file.write(str(datetime.datetime.now())+'Start'+'\n')
    edi_filename = processa_file_pdf.processa_file(file,dir_edi,dir_pdf,dir_log)
    print(edi_filename)
    print('End!')
    log_file.write(str(datetime.datetime.now())+'End!'+'\n')
