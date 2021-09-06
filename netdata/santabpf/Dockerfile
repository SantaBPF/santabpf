FROM netdata/netdata:v1.31.0


RUN apk add --no-cache --update \
	vim \
 && pip install tabulate

WORKDIR /etc/netdata

COPY ./exec ./exec/

RUN rm /usr/lib/netdata/conf.d/health.d/*

COPY ./configs/netdata/. /usr/lib/netdata/conf.d/
COPY ./plugins/ /usr/libexec/netdata/
COPY ./web /usr/share/netdata/web/
