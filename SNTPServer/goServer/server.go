package main

import (
	"fmt"
	"net"
	"os"
)

type UDPInfo struct {
	buf  []byte
	addr *net.UDPAddr
}

type Server struct {
	address    *net.UDPAddr
	connection *net.UDPConn
	delay      int
}

func (server *Server) ConfigureAddress(port string) {
	address, err := net.ResolveUDPAddr("udp", port)
	server.address = address
	checkError(err)
}

func (server *Server) ConfigureConnection() {
	connection, err := net.ListenUDP("udp", server.address)
	server.connection = connection
	checkError(err)
}

func (server *Server) Run() {
	in := make(chan UDPInfo, 16)
	go server.Receive(in)
	defer server.connection.Close()

	for {
		buffer := make([]byte, 1024)
		n, address, err := server.connection.ReadFromUDP(buffer)
		if err != nil {
			println("Error", err)
		}
		println("new client", address.IP.String(), ":", address.Port)
		in <- UDPInfo{buffer[:n], address}
	}
}

func (server *Server) Receive(ch chan UDPInfo) {
	for frame := range ch {
		res := Generate(frame.buf, server.delay)
		server.connection.WriteToUDP(res, frame.addr)
	}
}

func startServer(port string, delay int) {
	server := Server{delay: delay}
	server.ConfigureAddress(port)
	server.ConfigureConnection()
	println("Server start on 127.0.0.1:123")
	server.Run()
}

func checkError(err error) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "Fatal error ", err.Error())
		os.Exit(1)
	}
}
