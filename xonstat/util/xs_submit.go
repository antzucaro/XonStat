package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

/* xs_submit takes a file containing a single XonStat request and submits it
   to the server URL specified */
func main() {
	fn := flag.String("file", "xonstat.log", "Logfile from XonStat")
	url := flag.String("url", "http://localhost:6543/stats/submit", "XonStat submission URL")
	out := flag.Bool("out", false, "logs the response body to <file>.out")
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

	if *out {
		// open the output file for the response
		of, err := os.Create(*fn + ".out")
		if err != nil {
			fmt.Printf("Issue creating file %s.out\n", *fn)
			os.Exit(1)
		}
		defer of.Close()

		bo := bufio.NewWriter(of)
		defer bo.Flush()

		scanner := bufio.NewScanner(res.Body)
		for scanner.Scan() {
			fmt.Fprintln(bo, scanner.Text())
		}
	}
}
