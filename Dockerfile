FROM python:2
MAINTAINER Anthony Monthe (ZuluPro) <anthony.monthe@gmail.com>

ENV PYTHONUNBUFFERED 1
ENV JARDINFAQ_CONFIG_FILE /conf/jardinfaq.cfg

RUN useradd -ms /bin/bash jardinfaq

ENV repo_dir /jardinfaq/
ADD . $repo_dir
WORKDIR $repo_dir
RUN chown -R jardinfaq $repo_dir

RUN pip install -r requirements.txt MySQL-Python uwsgi

USER jardinfaq

CMD ["uwsgi", "--ini", "./uwsgi.ini"]

EXPOSE 3031
