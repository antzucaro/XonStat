package main

import "database/sql"
import "flag"
import "fmt"
import "html/template"
import "net/http"
import "os"
import "strings"
import "time"
import _ "github.com/mattn/go-sqlite3"

// HTML templates
var templates = template.Must(template.ParseFiles("templates/landing.html"))

func main() {
	port := flag.Int("port", 6543, "Default port on which to accept requests")
	url := flag.String("url", "http://localhost:6543/stats/submit", "URL to send POST requests against")
	flag.Usage = usage
	flag.Parse()

	if len(flag.Args()) < 1 {
		fmt.Println("Insufficient arguments: need a <command> to run. Exiting...")
		os.Exit(1)
	}

	command := flag.Args()[0]
	switch {
	case command == "drop":
		drop_db()
	case command == "create":
		create_db()
	case command == "serve":
		serve(*port)
	case command == "resubmit":
		resubmit(*url)
	case command == "list":
		list()
	default:
		fmt.Println("Unknown command! Exiting...")
		os.Exit(1)
	}
}

// override the default Usage function to show the different "commands"
// that are in the switch statement in main()
func usage() {
	fmt.Fprintf(os.Stderr, "Usage of xs_interceptor:\n")
	fmt.Fprintf(os.Stderr, "    xs_interceptor [options] <command>\n\n")
	fmt.Fprintf(os.Stderr, "Where <command> is one of the following:\n")
	fmt.Fprintf(os.Stderr, "    create   - create the requests db (sqlite3 db file)\n")
	fmt.Fprintf(os.Stderr, "    drop     - remove the requests db\n")
	fmt.Fprintf(os.Stderr, "    list     - lists the requests in the db\n")
	fmt.Fprintf(os.Stderr, "    serve    - listens for stats requests, storing them if found\n")
	fmt.Fprintf(os.Stderr, "    resubmit - resubmits the requests to another URL\n\n")
	fmt.Fprintf(os.Stderr, "Where [options] is one or more of the following:\n")
	fmt.Fprintf(os.Stderr, "    -port    - port number (int) to listen on for 'serve' command\n")
	fmt.Fprintf(os.Stderr, "    -url     - url (string) to submit requests\n\n")
}

// removes the requests database. it is just a file, so this is really easy.
func drop_db() {
	err := os.Remove("middleman.db")

	if err != nil {
		fmt.Println("Error dropping the database middleman.db. Exiting...")
		os.Exit(1)
	} else {
		fmt.Println("Dropped middleman.db successfully!")
		os.Exit(0)
	}
}

// creates the sqlite database. it's a hard-coded name because I don't see
// a need to change db names for this purpose.
func create_db() {
	db, err := sql.Open("sqlite3", "./middleman.db")
	defer db.Close()

	if err != nil {
		fmt.Println("Error creating the database middleman.db. Exiting...")
		fmt.Println(err)
		os.Exit(1)
	} else {
		fmt.Println("Created middleman.db successfully!")
	}

	_, err = db.Exec(`
     CREATE TABLE requests (
        request_id INTEGER PRIMARY KEY ASC, 
        blind_id_header TEXT, 
        ip_addr VARCHAR(32), 
        body TEXT, 
        bodylength int 
     );
  `)

	if err != nil {
		fmt.Println("Error creating the table 'requests' in middleman.db. Exiting...")
		os.Exit(1)
	} else {
		fmt.Println("Created table 'requests' successfully!")
	}
}

// an HTTP server that responds to two types of URLs: stats submissions (which it records)
// and everything else, which receive a down-page
func serve(port int) {
	requests := 0

	// routing
	http.HandleFunc("/", defaultHandler)
	http.HandleFunc("/stats/submit", makeSubmitHandler(requests))
	http.Handle("/m/", http.StripPrefix("/m/", http.FileServer(http.Dir("m"))))

	// serving
	fmt.Printf("Serving on port %d...\n", port)
	addr := fmt.Sprintf(":%d", port)
  for true {
    http.ListenAndServe(addr, nil)
    time.Sleep(100*time.Millisecond)
  }
}

// intercepts all URLs, displays a landing page
func defaultHandler(w http.ResponseWriter, r *http.Request) {
	err := templates.ExecuteTemplate(w, "landing.html", nil)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

// accepts stats requests at a given URL, stores them in requests
func makeSubmitHandler(requests int) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("in submission handler")

		if r.Method != "POST" {
			http.Redirect(w, r, "/", http.StatusFound)
			return
		}

		// check for blind ID header. If we don't have it, don't do anything
		var blind_id_header string
		_, ok := r.Header["X-D0-Blind-Id-Detached-Signature"]
		if ok {
			fmt.Println("Found a blind_id header. Extracting...")
			blind_id_header = r.Header["X-D0-Blind-Id-Detached-Signature"][0]
		} else {
			fmt.Println("No blind_id header found.")
			blind_id_header = ""
		}

		remoteAddr := getRemoteAddr(r)

		// and finally, read the body
		body := make([]byte, r.ContentLength)
		r.Body.Read(body)

		db := getDBConn()
		defer db.Close()

		_, err := db.Exec("INSERT INTO requests(blind_id_header, ip_addr, body, bodylength) VALUES(?, ?, ?, ?)", blind_id_header, remoteAddr, string(body), r.ContentLength)
		if err != nil {
			fmt.Println("Unable to insert request.")
			fmt.Println(err)
		}
	}
}

// gets the remote address out of http.Requests with X-Forwarded-For handling
func getRemoteAddr(r *http.Request) (remoteAddr string) {
	val, ok := r.Header["X-Forwarded-For"]
	if ok {
		remoteAddr = val[0]
	} else {
		remoteAddr = r.RemoteAddr
	}

	// sometimes a ":<port number>" comes attached, which
	// needs removing
	idx := strings.Index(remoteAddr, ":")
	if idx != -1 {
		remoteAddr = remoteAddr[0:idx]
	}

	return
}

// resubmits stats request to a particular URL. this is intended to be used when
// you want to write back to the "real" XonStat
func resubmit(url string) {
	db := getDBConn()
	defer db.Close()

	rows, err := db.Query("SELECT request_id, ip_addr, blind_id_header, body, bodylength FROM requests ORDER BY request_id")
	if err != nil {
		fmt.Println("Error reading rows from the database. Exiting...")
		os.Exit(1)
	}
	defer rows.Close()

	successfulRequests := make([]int, 0, 10)
	for rows.Next() {
		// could use a struct here, but isntead just a bunch of vars
		var request_id int
		var blind_id_header string
		var ip_addr string
		var body string
		var bodylength int

		if err := rows.Scan(&request_id, &ip_addr, &blind_id_header, &body, &bodylength); err != nil {
			fmt.Println("Error reading row for submission. Continuing...")
			continue
		}

		req, _ := http.NewRequest("POST", url, strings.NewReader(body))
		//req.ContentLength = int64(bodylength)
    //req.ContentLength = 0
		req.ContentLength = int64(len([]byte(body)))

		header := map[string][]string{
			"X-D0-Blind-Id-Detached-Signature": {blind_id_header},
			"X-Forwarded-For":                  {ip_addr},
		}
		req.Header = header

		res, err := http.DefaultClient.Do(req)
		if err != nil {
			fmt.Printf("Error submitting request #%d. Continuing...\n", request_id)
			fmt.Println(err)
			continue
		}
		defer res.Body.Close()

		fmt.Printf("Request #%d: %s\n", request_id, res.Status)

		if res.StatusCode < 500 {
			successfulRequests = append(successfulRequests, request_id)
		}
	}

	// now that we're done resubmitting, let's clean up the successful requests
	// by deleting them outright from the database
	for _, val := range successfulRequests {
		deleteRequest(db, val)
	}
}

// lists all the requests and their information *in the XonStat log format* in
// order to 1) show what's in the db and 2) to be able to save/parse it (with
// xs_parse) for later use.
func list() {
	db := getDBConn()
	defer db.Close()

	rows, err := db.Query("SELECT request_id, ip_addr, blind_id_header, body FROM requests ORDER BY request_id")
	if err != nil {
		fmt.Println("Error reading rows from the database. Exiting...")
		os.Exit(1)
	}
	defer rows.Close()

	for rows.Next() {
		var request_id int
		var blind_id_header string
		var ip_addr string
		var body string

		if err := rows.Scan(&request_id, &ip_addr, &blind_id_header, &body); err != nil {
			fmt.Println("Error opening middleman.db. Did you create it?")
			continue
		}

		fmt.Printf("Request: %d\n", request_id)
		fmt.Printf("IP Address: %s\n", ip_addr)
		fmt.Println("----- BEGIN REQUEST BODY -----")

		if len(blind_id_header) > 0 {
			fmt.Printf("d0_blind_id: %s\n", blind_id_header)
		}

		fmt.Print(body)
		fmt.Printf("\n----- END REQUEST BODY -----\n")
	}
}

// hard-coded sqlite database connection retriever to keep it simple
func getDBConn() *sql.DB {
	conn, err := sql.Open("sqlite3", "./middleman.db")

	if err != nil {
		fmt.Println("Error opening middleman.db. Did you create it?")
		os.Exit(1)
	}

	return conn
}

// removes reqeusts from the database by request_id
func deleteRequest(db *sql.DB, request_id int) {
	_, err := db.Exec("delete from requests where request_id = ?", request_id)
	if err != nil {
		fmt.Printf("Could not remove request_id %d from the database. Reason: %v\n", request_id, err)
	} else {
		fmt.Printf("Request #%d removed from the database.\n", request_id)
	}
}
