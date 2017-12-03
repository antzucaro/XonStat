package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
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

type Game struct {
	GameID   int       `db:"game_id"`
	GameType string    `db:"game_type_cd"`
	ServerID int       `db:"server_id"`
	Duration int       `db:"duration"`
	CreateDt time.Time `db:"create_dt"`
}

type PlayerGameStat struct {
	PlayerGameStatID int    `db:"player_game_stat_id"`
	PlayerID         int    `db:"player_id"`
	GameID           int    `db:"game_id"`
	Nick             string `db:"stripped_nick"`
	AliveTime        int    `db:"alivetime"`
	Score            int    `db:"score"`
}

type GameProcessor struct {
	config *Config
	db     *sqlx.DB
}

func NewGameProcessor(config *Config) *GameProcessor {
	processor := new(GameProcessor)

	processor.config = config

	db, err := sqlx.Connect("postgres", config.ConnStr)
	if err != nil {
		log.Fatal(err)
	}
	processor.db = db

	return processor
}

func (gp *GameProcessor) GamesInRange() []Game {
	games := []Game{}

	sql := `select game_id, game_type_cd, server_id, EXTRACT(EPOCH FROM duration) duration, 
	create_dt from games where game_id between $1 and $2 order by game_id`

	err := gp.db.Select(&games, sql, gp.config.StartGameID, gp.config.EndGameID)
	if err != nil {
		log.Fatalf("Unable to select games: %s.\n", err)
	}

	return games
}

func (gp *GameProcessor) PlayerGameStats(gameID int) []PlayerGameStat {
	pgstats := []PlayerGameStat{}

	sql := `select player_game_stat_id, player_id, game_id, stripped_nick, 
	EXTRACT(EPOCH from alivetime) alivetime, score from player_game_stats 
	where game_id = $1 and player_id > 2 order by player_game_stat_id`

	err := gp.db.Select(&pgstats, sql, gameID)
	if err != nil {
		log.Fatalf("Unable to select player_game_stats for game %d: %s.\n", gameID, err)
	}

	return pgstats
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

	processor := NewGameProcessor(config)
	for _, game := range processor.GamesInRange() {
		pgstats := processor.PlayerGameStats(game.GameID)
		fmt.Println(pgstats)
	}
}
