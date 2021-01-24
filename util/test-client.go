package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sync"
	"time"
)

type client struct {
	remote_addr string
	remote_port string
	wg          sync.WaitGroup
}

func (c *client) Get(seconds float64) {
	defer c.wg.Done()

	start := time.Now()

	resp, _ := http.Get(fmt.Sprintf("http://%v:%v/delay?seconds=%v", c.remote_addr, c.remote_port, seconds))
	rawBody, _ := ioutil.ReadAll(resp.Body)
	body := string(rawBody)

	fmt.Println(body, fmt.Sprintf("[%v in client]", time.Since(start)))
}

func main() {
	flagSync := flag.Bool("sync", false, "send requests synchronously")
	flagN := flag.Int("n", 1, "how many requests you want")
	flagDelay := flag.Float64("delay", 0, "delay in seconds")

	flag.Parse()

	remote_addr := os.Getenv("TEST_SERVER_ADDR")
	remote_port := os.Getenv("TEST_SERVER_PORT")

	c := client{remote_addr, remote_port, sync.WaitGroup{}}

	for i := 0; i < *flagN; i++ {
		if *flagSync {
			c.Get(*flagDelay)
		} else {
			c.wg.Add(1)
			go c.Get(*flagDelay)
		}
	}

	c.wg.Wait()
}
