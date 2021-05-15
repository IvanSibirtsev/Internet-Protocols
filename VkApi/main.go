package main

import (
	"flag"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"github.com/SevereCloud/vksdk/v2/object"
	"github.com/joho/godotenv"
	"log"
	"os"
)

type FriendsGetUsersResp struct {
	Count int                `json:"count"`
	Items []object.UsersUser `json:"items"`
}

func init() {
	if err := godotenv.Load(); err != nil {
		log.Print("No .env file found")
	}
}

func main() {
	printFriends(Response(Id(), api.NewVK(Token())))
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

func Response(id int64, vk *api.VK) FriendsGetUsersResp {
	var response FriendsGetUsersResp
	params := api.Params{
		"user_id": id,
		"fields":  "nickname",
	}
	err := vk.RequestUnmarshal("friends.get", &response, params)
	if err != nil {
		log.Fatal(err)
	}

	return response
}

func printFriends(response FriendsGetUsersResp) {
	for i, user := range response.Items {
		userInformation := fmt.Sprintf("%s %s: %s%d", user.FirstName, user.LastName, "id", user)
		number := fmt.Sprintf("%d.", i+1)
		fmt.Println(number, userInformation)
	}
}
