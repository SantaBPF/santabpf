#!/bin/bash

tmp=`mktemp`
size=$(free -m | awk '/^Mem/{print int($7*0.6)}')

flush_stdin() {
	read -t .2 -n 10000 _
}

cleanup() {
	echo "[+] cleaning up start"
	./reset_available_memory_size.sh
	rm "$tmp"
	echo "[+] cleaning up end"
	exit
}

wait_any_key() {
	flush_stdin
	read -p "[+] press any key to continue" -n1 -s
	echo
}

benchmark() {
	echo "[+] press any key to benchmark (q for quit)"
	flush_stdin
	while read -sn 1 k && [[ $k != 'q' ]];
	do
		echo "[+] read $tmp"
		{ time cat "$tmp" >/dev/null; } 2>&1 | sed 's/^/\t/'
		flush_stdin
	done
}

trap cleanup INT EXIT

echo "[+] generating dummy data start at $tmp"
head -c ${size}M </dev/zero | tr '\0' 1 >$tmp
echo "[+] generating dummy data end"
wait_any_key

benchmark

echo "[+] lowering available memory size start"
./lower_available_memory_size.sh
echo "[+] lowering available memory size end"
wait_any_key

benchmark

echo "[+] reset available memory size start"
./reset_available_memory_size.sh
echo "[+] reset available memory size end"
wait_any_key

benchmark
