import logging
from datetime import datetime
import os


def setup_logger():
    log_path = 'logs'
    os.makedirs(log_path, exist_ok=True)
    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"atendimentos_{current_date}.log"
    log_full_path = os.path.join(log_path,log_file)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_full_path,
        filemode='a',
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)sZ %(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def log_action(username=None, action=None, table=None, id=None):
    logging.info(f'Usuario:({username}) Acao:({action}) Tabela:({table}) Registro:({id})')

def log_emails(msg):
    logging.info(msg)


