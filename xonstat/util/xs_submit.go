package main

import "bytes"
import "flag"
import "fmt"
import "io/ioutil"
import "net/http"
import "os"

/* xs_submit takes a file containing a single XonStat request and submits it
   to the server URL specified */
func main() {
  var fn = flag.String("file", "xonstat.log", "Logfile from XonStat")
  var url = flag.String("url", "http://localhost:6543/stats/submit", "XonStat submission URL")
  flag.Parse()

  body, err := ioutil.ReadFile(*fn)
  if err != nil {
    fmt.Printf("Issue opening file %s\n", *fn)
    os.Exit(1)
  }
  contentlength := int64(len(body))

  r := bytes.NewReader(body)

  req, _ := http.NewRequest("POST", *url, r)
  req.ContentLength = contentlength
  res, _ := http.DefaultClient.Do(req)
  defer res.Body.Close()

  fmt.Printf("%s: %s\n", *fn, res.Status)
}
