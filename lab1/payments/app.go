package main;

import (
    "fmt"
    "io"
    "io/ioutil"
    "net/http"
    "github.com/buger/jsonparser"
    "log"
)

var productDB []map[string]interface{}

func processPayment(w http.ResponseWriter, r *http.Request) {
    var total int64 = 0
    data, _ := ioutil.ReadAll(r.Body)
    jsonparser.ArrayEach(
            data,
            func(value []byte, dataType jsonparser.ValueType, offset int, err error) {
                id, _ := jsonparser.GetInt(value, "id")
                qty, _ := jsonparser.GetInt(value, "qty")
                total = total + productDB[id]["price"].(int64) * qty;
            },
        "cart")

    io.WriteString(w, fmt.Sprintf("{\"total\": %d}", total))
}

func main() {
    // Initialize ProductDB
    data, err := ioutil.ReadFile("productDB.json")
    if err != nil {
        panic(err)
    }

    jsonparser.ArrayEach(data, func(value []byte, dataType jsonparser.ValueType, offset int, err error) {
        m := make(map[string]interface{})
        m["name"], _ = jsonparser.GetString(value, "name")
        m["price"], _ = jsonparser.GetInt(value, "price")
        productDB = append(productDB, m)
    })

    // Start Web server
    mux := http.NewServeMux()
    mux.HandleFunc("/process", processPayment)

    err = http.ListenAndServe(":8000", mux)
    log.Fatal(err)
}
