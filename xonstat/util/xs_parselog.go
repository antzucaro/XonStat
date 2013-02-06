package main

import "bufio"
import "flag"
import "fmt"
import "os"
import "strings"

/* xs_parselog parses a standard XonStat log and breaks it down into
   individual requests which are then saved into files. The file format
   is <game type>_<match_id>.txt, so one can easily identify which type
   of request the file contains and which one it is (the match_id is the
   'I' line in the actual request).

   There is also the ability to extract a specific match as well as to
   anonymize the hashkeys in the requests to prevent exposing player data
   unnecessarily. */
func main() {
  var fn = flag.String("file", "xonstat.log", "XonStat log file name")
  var target_match_id = flag.String("match", "", "the specific match_id (I line) to extract from the log")
  var anonymize = flag.Bool("anonymize", false, "whether or not to anonymize player hashkeys")
  flag.Parse()

  f, err := os.Open(*fn)
  if err != nil {
    fmt.Println("Issue opening file")
    os.Exit(1)
  }
  defer f.Close()

  r := bufio.NewReader(f)

  var inreq bool
  var match_id string
  var game_type_cd string
  lines := make([]string, 0, 100)
  hashkeys := make(map[string] int, 500)
  max_player_id := 0

  line, err := r.ReadString('\n')
  for err == nil {
    switch {
      case strings.Contains(line, "BEGIN REQUEST BODY"):
        inreq = true
      case strings.Contains(line, "END REQUEST BODY"):
        if *target_match_id == "" || match_id == *target_match_id {
          create_match_file(game_type_cd, match_id, lines)
        }
        inreq = false
        lines = make([]string, 0, 100)
      case inreq:
        if *anonymize && line[0] == 'P' {
          if line[2:5] != "bot" && line[2:8] != "player" {
            hashkey := line[2:len(line)-1]
            if _, ok := hashkeys[hashkey]; !ok {
              hashkeys[hashkey] = max_player_id
              max_player_id = max_player_id + 1
            }
            line = fmt.Sprintf("P %d\n", hashkeys[hashkey])
          }
        }
        if line[0] == 'I' {
          match_id = line[2:len(line)-1]
        }
        if line[0] == 'G' {
          game_type_cd = line[2:len(line)-1]
        }
        lines = append(lines, line)
    }

    line, err = r.ReadString('\n')
  }
}


func create_match_file(game_type_cd string, match_id string, body []string) {
  fn := fmt.Sprintf("%s_%s.txt", game_type_cd, match_id)
  f_raw, err := os.Create(fn)
  if err != nil {
    fmt.Printf("Error creating match_id %s.\n", match_id)
  }
  defer f_raw.Close()

  f := bufio.NewWriter(f_raw)
  for _, v := range body {
    fmt.Fprint(f, v)
  }
  f.Flush()
}
