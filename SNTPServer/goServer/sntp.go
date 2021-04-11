package main

import "time"

const (
	From1900To1970 = 2208988800
)

func timeToNtpFormat(time int64) int64 {
	return time + From1900To1970
}

func intToBytes(i int64) []byte {
	b := make([]byte, 4)
	h1 := i >> 24
	h2 := (i >> 16) - (h1 << 8)
	h3 := (i >> 8) - (h1 << 16) - (h2 << 8)
	h4 := byte(i)
	b[0] = byte(h1)
	b[1] = byte(h2)
	b[2] = byte(h3)
	b[3] = byte(h4)
	return b
}

func getByteRepresentation(current int64, fraction int64) []byte {
	return append(intToBytes(current), intToBytes(fraction)...)
}

func Generate(request []byte, delay int) []byte {
	currentTime := timeToNtpFormat(time.Now().Unix())
	fraction := timeToNtpFormat(int64(time.Now().Nanosecond()))
	currentTimeWithDelay := currentTime + int64(delay)
	originateTimestamp := request[40:48]
	receivedTimestamp := getByteRepresentation(currentTime, fraction)
	transmitTimestamp := getByteRepresentation(currentTimeWithDelay, fraction)
	response := make([]byte, 48)
	LiVnMode := request[0]&0x38 + 4
	response[0] = LiVnMode
	response[1] = 1
	response[2] = 0
	copy(response[24:32], originateTimestamp)
	copy(response[32:40], receivedTimestamp)
	copy(response[40:48], transmitTimestamp)
	return response
}
