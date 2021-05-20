package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/joho/godotenv"
	"log"
	"net/http"
	"os"
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
	rawGetFriendsUrl := "https://api.vk.com/method/friends.get?user_id=%d&fields=nickname&access_token=%s&v=5.130"
	getFriendsUrl := fmt.Sprintf(rawGetFriendsUrl, id, token)
	resp, err := http.Get(getFriendsUrl)
	checkError(err)
	defer resp.Body.Close()
	var response Response
	err = json.NewDecoder(resp.Body).Decode(&response)
	checkError(err)

	return response.Response
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
