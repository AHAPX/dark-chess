FROM python:3.5

MAINTAINER AHAPX
MAINTAINER anarchy.b@gmail.com

RUN git clone https://github.com/AHAPX/dark-chess.git /dark-chess
RUN pip install -U pip
RUN pip install -r /dark-chess/requirements.txt

EXPOSE 38599

CMD cd /dark-chess/src && python main.py
