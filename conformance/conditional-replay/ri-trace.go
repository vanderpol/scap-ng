// This program runs from the pinned RI module and uses the report-side Evaluate reducer.
package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/vanderpol/scap-ng-ri/runtimecore"
)

type traceCase struct {
	Expression   json.RawMessage   `json:"expression"`
	Leaves       map[string]string `json:"leaves"`
	Dependencies map[string]string `json:"dependencies"`
	Presence     map[string]bool   `json:"presence"`
}

type observation struct {
	Entries []runtimecore.ExpressionTraceEntry `json:"entries"`
	Outcome string                             `json:"outcome"`
}

func run() error {
	var input map[string]traceCase
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		return err
	}
	results := make(map[string]observation, len(input))
	for name, scenario := range input {
		entries, outcome, err := runtimecore.LogicalExpressionTraceWithInputs(
			scenario.Expression, scenario.Leaves, scenario.Dependencies, scenario.Presence)
		if err != nil {
			return fmt.Errorf("%s: %w", name, err)
		}
		results[name] = observation{Entries: entries, Outcome: outcome}
	}
	return json.NewEncoder(os.Stdout).Encode(results)
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
