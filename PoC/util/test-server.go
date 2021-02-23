package main

import (
	"fmt"
	tm "github.com/buger/goterm"
	"net/http"
	"os"
	"strconv"
	"time"
)

type addrTime struct {
	Addr        string
	Start       time.Time
	ElapsedTime time.Duration
}

var delayChannel = make(chan *addrTime)

func delay(w http.ResponseWriter, req *http.Request) {
	seconds, _ := strconv.ParseFloat(req.URL.Query().Get("seconds"), 64)

	addrTime := addrTime{req.RemoteAddr, time.Now(), 0}

	delayChannel <- &addrTime
	defer func() {
		addrTime.ElapsedTime = time.Since(addrTime.Start)
		fmt.Fprintf(w, "[%s] [%v in server]", addrTime.Addr, addrTime.ElapsedTime)
	}()
	time.Sleep(time.Duration(1000*seconds) * time.Millisecond)

}

func draw() {
	tm.Clear()

	addrKeys := make([]*addrTime, 0)

	for {
		select {
		case addrTime := <-delayChannel:
			addrKeys = append(addrKeys, addrTime)
			for len(addrKeys) > 12 {
				addrKeys = addrKeys[1:]
				tm.Clear()
			}
		default:
			for i, addrTime := range addrKeys {
				tm.MoveCursor(1, i+1)
				tm.Print(addrTime.Addr, " has been connected..")
				if addrTime.ElapsedTime != 0 {
					tm.Printf(" and finished! [%v]\n", addrTime.ElapsedTime)
				}
			}
			tm.Flush()
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func main() {
	http.HandleFunc("/delay", delay)

	go draw()

	port := os.Args[1]

	http.ListenAndServe(":"+port, nil)
}
