FROM netdata/netdata:v1.31.0


RUN apk add --no-cache --update \
	vim bpftrace sudo\
 && pip install tabulate loguru

RUN echo 'netdata ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/netdata

WORKDIR /etc/netdata

COPY ./exec ./exec/

RUN rm /usr/lib/netdata/conf.d/health.d/*

COPY ./configs/netdata/. /usr/lib/netdata/conf.d/
COPY ./plugins/ /usr/libexec/netdata/
COPY ./web /usr/share/netdata/web/

RUN mkdir /var/log/santabpf && chown netdata /var/log/santabpf
