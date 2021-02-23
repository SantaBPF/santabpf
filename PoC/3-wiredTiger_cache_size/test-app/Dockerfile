FROM mongo:4.4.3

WORKDIR tmp

RUN apt update && apt install -y wget

RUN wget https://github.com/feliixx/mgodatagen/releases/download/v0.8.4/mgodatagen_linux_x86_64.tar.gz -O- | tar -xz

COPY ./dummy-data.json ./
COPY ./entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

CMD ["/tmp/entrypoint.sh"]
