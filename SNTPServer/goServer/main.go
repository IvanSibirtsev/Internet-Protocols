package main

import (
	"flag"
	"fmt"
)

func argParse() int {
	flag.Usage = func() {
		fmt.Printf("go run . -d [seconds]")
		flag.PrintDefaults()
	}
	delay := flag.Int("d", 0, "Delay added to real time. Default is 0.")
	flag.Parse()
	return *delay
}

func main() {
	delay := argParse()
	port := ":123"
	startServer(port, delay)
}
