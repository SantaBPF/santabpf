package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

type client struct {
	remote_addr string
}

func (c *client) Get(seconds float64) {
	resp, _ := http.Get(fmt.Sprintf("http://%v:38500/delay?seconds=%v", c.remote_addr, seconds))
	rawBody, _ := ioutil.ReadAll(resp.Body)
	body := string(rawBody)

	fmt.Println(body)
}

func main() {
	c := client{os.Getenv("TEST_SERVER_ADDR")}

	c.Get(3)
	c.Get(6)
}