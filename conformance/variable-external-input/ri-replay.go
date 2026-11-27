package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/vanderpol/scap-ng-ri/evaluate"
)

type Case struct {
	Name   string         `json:"name"`
	Test   string         `json:"test"`
	Values map[string]any `json:"values"`
}

type Observation struct {
	Decision   evaluate.Decision    `json:"decision"`
	Diagnostic *evaluate.Diagnostic `json:"diagnostic,omitempty"`
}

func run() error {
	var input struct {
		Request     json.RawMessage            `json:"request"`
		Definitions map[string]json.RawMessage `json:"definitions"`
		Cases       []Case                     `json:"cases"`
	}
	decoder := json.NewDecoder(os.Stdin)
	decoder.UseNumber()
	if err := decoder.Decode(&input); err != nil {
		return err
	}
	results := make(map[string]Observation, len(input.Cases))
	for _, entry := range input.Cases {
		ctx := evaluate.WithEvaluationInputs(context.Background(), entry.Values, input.Definitions)
		decision, diagnostic := evaluate.EvaluateTest(ctx, input.Request, entry.Test)
		results[entry.Name] = Observation{Decision: decision, Diagnostic: diagnostic}
	}
	return json.NewEncoder(os.Stdout).Encode(results)
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
