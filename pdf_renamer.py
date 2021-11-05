import pdftotext
import re
import sys
import os
from os import walk
import argparse
from pathlib import Path
import logging


try:
    import colorlog
except ImportError:
    pass
class Company:
    def __init__(self, name):
        self.name = name
        self.number_of_appearance = 1

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    format      = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
              log_colors = { 'DEBUG'   : 'reset',       'INFO' : 'reset',
                             'WARNING' : 'bold_yellow', 'ERROR': 'bold_red',
                             'CRITICAL': 'bold_red' })
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)




def pdf_rename(file_name, path):
    folder = Path(path)
    file_to_open = folder / file_name
    pdf_to_text(file_to_open, folder)

def pdf_to_text(file_name, dest_folder):

    with open(file_name, "rb") as f:
        pdf = pdftotext.PDF(f)

    text = pdf[0]
    content = [line.split(':') for line in text.splitlines()]
    extract_company_name(content, file_name, dest_folder)

def extract_company_name(content, file_name, dest_folder): 
    ## remove items that is less than 2 in the list
    for x in content:
        if len(x) != 2:
            content.remove(x)

    company_name = None
    ## Extract content that has "To" keyword
    for x in content:
        ## get the company name if the first item has keyword "To "
        if x[0].startswith('To'):
            company_name = x[1]
            if(company_name not in [x.name for x in global_company]):
                global_company.append(Company(name=company_name))
            else:
                index = findCompanyByName(company_name)
                global_company[index].number_of_appearance += 1
            

    if company_name is None:
        output_msg = f'{os.path.basename(file_name)} does not contain keyword "To"'
        log.error(output_msg)
    else: 
        ##remove whitespace 
        ##company_name = company_name.strip()
        ##search company in the global list
        index = findCompanyByName(company_name)
        company_name = global_company[index].name.strip()
        number_of_appearance = global_company[index].number_of_appearance
        if(number_of_appearance == 1):
            rename_file(company_name, file_name, dest_folder)
        else:
            rename_file(newfile_name=company_name + " "+str(number_of_appearance), ori_file_name=file_name, dest_folder=dest_folder)


def rename_file(newfile_name,ori_file_name, dest_folder):
    target_file_name = os.path.join(dest_folder/"new", f'{newfile_name}.pdf')
    if not os.path.exists(dest_folder/"new"):
        os.makedirs(dest_folder/"new")
    os.rename(ori_file_name, target_file_name)
    output_msg = f' {os.path.basename(ori_file_name)} has been successfully renamed as {newfile_name}'
    log.info(output_msg)

def findCompanyByName(name):
      for i in range(len(global_company)):
        if global_company[i].name == name:
            return i

if __name__ == "__main__":
    setup_logging()
    global_company = []
    log = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='A simple pdf renamer')
    parser.add_argument("-p")

    args = parser.parse_args()
    path = args.p

    f = []
    for (dirpath, dirnames, filenames) in walk(path):
        if any(f.endswith('.pdf') for f in filenames):
            f.extend(filenames)
            break
        else:
            log.error(f'{filenames} does not have pdf extension')
    if len(f) == 0:
        log.error('No file is found')
        sys.exit()
    for x in f:
        pdf_rename(x, path)
    

