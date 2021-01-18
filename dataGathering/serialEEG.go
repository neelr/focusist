package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/tarm/serial"
)

func main() {
	id := -1
	buf := 1
	count := 0
	go startserver(&id)
	fmt.Println("Starting Serial Listener")
	c := &serial.Config{Name: "/dev/cu.usbmodem142101", Baud: 9600, ReadTimeout: time.Second * 2}
	s, err := serial.OpenPort(c)
	if err != nil {
		fmt.Println(err)
		return
	}
	f, err := os.Create("data.csv")
	defer f.Close()
	f.Write([]byte("connection,attention,meditation,delta, theta, low alpha, high alpha, low beta, high beta, low gamma, high gamma, id\n"))
	scanner := bufio.NewScanner(s)
	for scanner.Scan() {
		if buf != id {
			count++
			if count == 5 {
				count = 0
				buf = id
			}
		} else if id >= 0 {
			line2put := scanner.Text()
			if len(line2put) > 0 && line2put[0] != 'E' {
				f.Write([]byte(scanner.Text() + "," + strconv.Itoa(id) + "\n"))
				buf = id
			}
		}
		fmt.Println(scanner.Text())
	}
}

func startserver(id *int) {
	http.HandleFunc("/switcharoo", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			fmt.Fprintf(w, "ONLY POST")
			return
		}
		fmt.Println("Switcharooing")
		b, err := ioutil.ReadAll(r.Body)
		newid, err := strconv.Atoi(string(b))
		if err != nil {
			panic(err)
		}
		*id = newid
		fmt.Fprintf(w, "Added ID!")
	})
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
