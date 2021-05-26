FROM netdata/netdata

RUN apk add --update \
  bcc-tools bcc-doc \
  bison build-base clang-dev clang-static curl cmake \
  elfutils-dev flex-dev linux-headers llvm10-dev llvm10-static \
  python3 python3-dev zlib-dev abuild bc \
  git binutils gcc ncurses-dev openssl-dev \
  musl-dev g++
RUN ln -s $(which python3) /usr/bin/python

COPY ./configs/ /usr/lib/netdata/conf.d/
COPY ./plugins/ /usr/libexec/netdata/

ENV PATH="/usr/share/bcc/tools:${PATH}"

WORKDIR /admin
COPY ./debug.sh ./debug.sh

ENTRYPOINT ["/usr/sbin/netdata", "-u", "root", "-D", "-s", "/host", "-p", "19999", "-W", "set", "web", "web", "files", "group", "root", "-W", "set", "web", "web", "files", "owner", "root"]
