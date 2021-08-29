FROM netdata/netdata:v1.31.0

RUN apk update \
 && apk add vim ssmtp gettext

COPY ./init.sh ./
RUN chmod +x ./init.sh

RUN rm /usr/lib/netdata/conf.d/health.d/*

COPY ./configs/ssmtp /etc/ssmtp/
COPY ./configs/netdata/. /usr/lib/netdata/conf.d/
COPY ./plugins/ /usr/libexec/netdata/
COPY ./web /usr/share/netdata/web/

ENTRYPOINT ["./init.sh"]
