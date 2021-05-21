package main

import (
	"crypto/tls"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/joho/godotenv"
	"log"
	"os"
	"regexp"
	"strings"
)

type User struct {
	FirstName       string `json:"first_name"`
	Id              int    `json:"id"`
	LastName        string `json:"last_name"`
	CanAccessClosed bool   `json:"can_access_closed"`
	IsClosed        bool   `json:"is_closed"`
}

type Friends struct {
	Count int    `json:"count"`
	Items []User `json:"items"`
}

type Response struct {
	Response Friends `json:"response"`
}

func init() {
	if err := godotenv.Load(); err != nil {
		log.Fatal("No .env file found")
	}
}

func main() {
	printFriends(getFriends(Token(), Id()))
}

func Token() string {
	token, exist := os.LookupEnv("TOKEN")
	if !exist {
		log.Fatal("No token in .env file")
	}

	return token
}

func Id() int64 {
	flag.Usage = func() {
		fmt.Printf("go run main -id [id]")
		flag.PrintDefaults()
	}
	id := flag.Int64("id", 0, "User id")
	flag.Parse()

	return *id
}

func getFriends(token string, id int64) Friends {
	connection := makeRequest(id, token)
	var friends Response
	answer := HandelConnection(connection, "")
	response := strings.Split(answer, "\r\n\r\n")[1]
	err := json.Unmarshal([]byte(response), &friends)
	checkError(err)
	return friends.Response
}

func makeRequest(id int64, token string) *tls.Conn {
	host := "api.vk.com"
	conn, err := tls.Dial("tcp", fmt.Sprintf("%s:443", host), nil)
	checkError(err)
	url := fmt.Sprintf("method/friends.get?user_id=%d&fields=nickname&access_token=%s&v=5.130", id, token)
	request := httpRequest(url, host)
	_, err = fmt.Fprintf(conn, request)
	checkError(err)
	return conn
}

func httpRequest(url string, host string) string {
	return fmt.Sprintf("GET /%s HTTP/1.1\nHost: %s\nAccept: */*\n\n", url, host)
}

func HandelConnection(connection *tls.Conn, acc string) string {
	reply := make([]byte, 65535)
	n, _ := connection.Read(reply)
	ans := fmt.Sprintf(string(reply[:n]), n)
	if strings.Contains(ans, "}]}}") {
		return parse(acc + ans)
	}
	return HandelConnection(connection, acc+ans)
}

func parse(answer string) string {
	re := regexp.MustCompile(`%!\(EXTRA int=[0-9]+\)`)
	return re.ReplaceAllString(answer, "")
}

func printFriends(response Friends) {
	for i, user := range response.Items {
		userInformation := fmt.Sprintf("%s %s: %s%d", user.FirstName, user.LastName, "id", user.Id)
		number := fmt.Sprintf("%d.", i+1)
		fmt.Println(number, userInformation)
	}
}

func checkError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
