package main

import (
	"encoding/json"
	"flag"
	"fmt"
	glicko "github.com/Kashomon/goglicko"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"log"
	"os"
	"time"
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

type KReducer struct {
	// time in seconds required for full points
	FullTime int

	// the minimum time a player must play in the game
	MinTime int

	// the minimum ratio of time played in the game
	MinRatio float64
}

func (kr *KReducer) Evaluate(pgstat PlayerGameStat, game Game) float64 {
	k := 1.0

	if pgstat.AliveTime < kr.FullTime {
		k = float64(pgstat.AliveTime) / float64(kr.FullTime)
	}

	if pgstat.AliveTime < kr.MinTime || game.Duration < kr.MinTime {
		k = 0
	}

	if (float64(pgstat.AliveTime) / float64(game.Duration)) < kr.MinRatio {
		k = 0
	}

	return k
}

type GameProcessor struct {
	config        *Config
	db            *sqlx.DB
	playerRatings map[string]glicko.Rating
}

func NewGameProcessor(config *Config) *GameProcessor {
	processor := new(GameProcessor)

	processor.config = config

	db, err := sqlx.Connect("postgres", config.ConnStr)
	if err != nil {
		log.Fatal(err)
	}

	processor.db = db
	processor.playerRatings = make(map[string]glicko.Rating)

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

func (gp *GameProcessor) ProcessGame(game Game, pgstats []PlayerGameStat, reducer KReducer) error {
	fmt.Println(pgstats)
	for i := 0; i < len(pgstats)-1; i++ {
		for j := i + 1; j < len(pgstats); j++ {
			fmt.Printf("Comparing %s and %s.\n", pgstats[i].Nick, pgstats[j].Nick)
		}
	}
	return nil
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

	// reduction parameters
	reducer := KReducer{FullTime: 600, MinTime: 120, MinRatio: 0.5}

	processor := NewGameProcessor(config)
	for _, game := range processor.GamesInRange() {
		pgstats := processor.PlayerGameStats(game.GameID)
		processor.ProcessGame(game, pgstats, reducer)
	}
}
