package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
)

const DefaultStartGameID = 0
const DefaultEndGameID = -1
const DefaultRankingWindowDays = 7

type Config struct {
	// database connection string
	ConnStr string

	// the starting game_id in the games table
	StartGameID int

	// the ending game_id in the games table
	EndGameID int

	// the number of days constituting the ranking window
	RankingWindowDays int
}

func loadConfig(path string) (*Config, error) {
	config := new(Config)

	// defaults
	config.ConnStr = "user=xonstat host=localhost dbname=xonstatdb sslmode=disable"
	config.StartGameID = DefaultStartGameID
	config.EndGameID = DefaultEndGameID
	config.RankingWindowDays = DefaultRankingWindowDays

	file, err := os.Open(path)
	if err != nil {
		fmt.Println("Failed opening the file.")
		return config, err
	}

	decoder := json.NewDecoder(file)

	// overwrite in-mem config with new values
	err = decoder.Decode(config)
	if err != nil {
		fmt.Println("Failed to decode the JSON.")
		return config, err
	}

	return config, nil
}

func main() {
	path := flag.String("config", "xs_glicko.json", "configuration file path")
	start := flag.Int("start", DefaultStartGameID, "starting game_id")
	end := flag.Int("end", DefaultEndGameID, "ending game_id")
	days := flag.Int("days", DefaultRankingWindowDays, "number of days in the ranking window")
	flag.Parse()

	config, err := loadConfig(*path)
	if err != nil {
		log.Fatalf("Unable to load config file: %s.\n", err)
	}

	if *start != DefaultStartGameID {
		config.StartGameID = *start
	}

	if *end != DefaultEndGameID {
		config.EndGameID = *end
	}

	if *days != DefaultRankingWindowDays {
		config.RankingWindowDays = *days
	}

	fmt.Printf("%+v\n", config)
}
