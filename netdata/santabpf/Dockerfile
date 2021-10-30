FROM netdata/netdata:v1.31.0


RUN apk add --no-cache --update \
	vim bpftrace sudo perf perl\
 && pip install tabulate loguru fastapi uvicorn

RUN echo 'netdata ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/netdata

WORKDIR /etc/netdata

RUN rm /usr/lib/netdata/conf.d/health.d/*

COPY ./configs/netdata/. /usr/lib/netdata/conf.d/
COPY ./plugins/ /usr/libexec/netdata/
COPY ./web /usr/share/netdata/web/

WORKDIR /usr/libexec/netdata/santabpf

COPY app ./app

RUN mkdir svg && chown -R netdata:netdata svg
RUN mkdir /var/log/santabpf && chown -R netdata:netdata /var/log/santabpf

WORKDIR ./app
RUN ln -s /var/log/santabpf ./log

COPY ./tmp/_1min_cpu_usage_211017-164024.svg /usr/libexec/netdata/santabpf/svg/
RUN chown netdata:netdata /usr/libexec/netdata/santabpf/svg/_1min_cpu_usage_211017-164024.svg

ENTRYPOINT ["sh", "run.sh"]
