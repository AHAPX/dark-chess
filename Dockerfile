FROM python:3.5

MAINTAINER AHAPX
MAINTAINER anarchy.b@gmail.com

RUN git clone https://github.com/AHAPX/dark-chess.git /opt/dark-chess
RUN pip install -U pip
RUN pip install -r /opt/dark-chess/requirements.txt

CMD cd /opt/dark-chess/src && python main.py

