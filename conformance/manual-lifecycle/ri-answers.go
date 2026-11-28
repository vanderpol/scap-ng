// This program runs from the pinned RI module and uses its public answer importer.
package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/vanderpol/scap-ng-ri/answers"
	"github.com/vanderpol/scap-ng-ri/benchmark"
)

func main() {
	type observation struct {
		Answers    map[string]benchmark.ManualAnswer `json:"answers,omitempty"`
		Diagnostic string                            `json:"diagnostic,omitempty"`
	}

	result := make([]observation, 0, len(os.Args)-1)
	for _, path := range os.Args[1:] {
		document, err := answers.Load(path)
		if err != nil {
			result = append(result, observation{Diagnostic: err.Error()})
			continue
		}
		result = append(result, observation{Answers: document.Answers})
	}
	if err := json.NewEncoder(os.Stdout).Encode(result); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
